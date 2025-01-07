from fastapi import APIRouter, WebSocket
from fastapi.websockets import WebSocketDisconnect
from utils.media_stream_utils import initialize_session
from azure.core.credentials import AzureKeyCredential
from config import OPENAI_API_KEY, OPENAI_MODEL, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT, AZURE_OPENAI_ENDPOINT, LOG_EVENT_TYPES
from rtclient import (
    InputAudioBufferAppendMessage,
    RTLowLevelClient,
    ItemTruncatedMessage,
)
import json
import base64
import asyncio
import logging


logger = logging.getLogger(__name__)

router_media = APIRouter()

@router_media.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    try:
        logger.info("Client connected to /media-stream.")
        print("Client connected")

        await websocket.accept()

        is_azure = False
        if not OPENAI_API_KEY or not OPENAI_MODEL:
            is_azure = True
            logger.info("Using Azure OpenAI Realtime API")
        else:
            logger.info("Using OpenAI Realtime API")
    
        async with RTLowLevelClient(
            url=AZURE_OPENAI_ENDPOINT if is_azure else None,
            key_credential=AzureKeyCredential(AZURE_OPENAI_API_KEY if is_azure else OPENAI_API_KEY),
            azure_deployment=AZURE_OPENAI_DEPLOYMENT if is_azure else None,
            model=None if is_azure else OPENAI_MODEL
        ) as client:
            await initialize_session(client)
        
            stream_sid = None
            event_id = None
            latest_media_timestamp = 0
            last_assistant_item = None
            mark_queue = []
            response_start_timestamp_twilio = None

            async def receive_from_twilio():
                nonlocal stream_sid, latest_media_timestamp, response_start_timestamp_twilio, last_assistant_item
                try:
                    async for message in websocket.iter_text():
                        data = json.loads(message)
                        if data['event'] == 'media' and not client.closed:
                            latest_media_timestamp = int(data['media']['timestamp'])
                            audio_append = InputAudioBufferAppendMessage(audio=data['media']['payload'])
                            await client.send(audio_append)
                        elif data['event'] == 'start':
                            stream_sid = data['start']['streamSid']
                            latest_media_timestamp = 0
                            last_assistant_item = None
                        elif data['event'] == 'mark':
                            if mark_queue:
                                mark_queue.pop(0)
                except WebSocketDisconnect:
                    if not client.closed:
                        await client.close()

            async def send_to_twilio():
                nonlocal stream_sid, last_assistant_item, response_start_timestamp_twilio, event_id
                try:
                    async for azure_openai_message in client:
                        response = azure_openai_message.model_dump()
                        if response['type'] in LOG_EVENT_TYPES:
                            print(f"Received event: {response['type']}", response)

                        if response.get('type') == 'response.audio.delta' and 'delta' in response:
                            audio_payload = base64.b64encode(base64.b64decode(response['delta'])).decode('utf-8')
                            audio_delta = {"event": "media","streamSid": stream_sid,"media": {"payload": audio_payload}}
                            await websocket.send_json(audio_delta)
                            if response_start_timestamp_twilio is None:
                                response_start_timestamp_twilio = latest_media_timestamp
                            if response.get('item_id'):
                                last_assistant_item = response['item_id']
                            await send_mark(websocket, stream_sid)

                        if response.get('type') == 'input_audio_buffer.speech_started':
                            if last_assistant_item:
                                event_id = response.get('event_id')
                                await handle_speech_started_event()

                except Exception as e:
                    print(f"Error in send_to_twilio: {e}")

            async def handle_speech_started_event():
                nonlocal response_start_timestamp_twilio, last_assistant_item, event_id
                if mark_queue and response_start_timestamp_twilio is not None:
                    elapsed_time = latest_media_timestamp - response_start_timestamp_twilio
                    if last_assistant_item:
                        truncate_message = ItemTruncatedMessage(event_id=event_id, 
                                                                item_id=last_assistant_item, 
                                                                content_index=0, 
                                                                audio_end_ms=elapsed_time)
                        await client.send(truncate_message)
                    await websocket.send_json({"event": "clear","streamSid": stream_sid})
                    mark_queue.clear()
                    last_assistant_item = None
                    response_start_timestamp_twilio = None
                    event_id = None

            async def send_mark(connection, sid):
                if sid:
                    mark_event = {"event": "mark","streamSid": sid,"mark": {"name": "responsePart"}}
                    await connection.send_json(mark_event)
                    mark_queue.append('responsePart')

            await asyncio.gather(receive_from_twilio(), send_to_twilio())
    except Exception as e:
        logger.error(f"Error from /media-stream: {e}")
        await websocket.close()