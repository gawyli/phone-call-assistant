from fastapi import APIRouter, WebSocket
from fastapi.websockets import WebSocketDisconnect
from utils.openai_utils import initialize_session
from config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT, AZURE_OPENAI_ENDPOINT, LOG_EVENT_TYPES
import websockets
import json
import base64
import asyncio
import logging

logger = logging.getLogger(__name__)

router_media = APIRouter()

# Azure OpenAI Realtime API WebSocket URL format
AZURE_REALTIME_URL = f"wss://{AZURE_OPENAI_ENDPOINT}/openai/realtime?api-version=2024-10-01-preview&deployment={AZURE_OPENAI_DEPLOYMENT}"


@router_media.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    logger.info("Client connected to /media-stream.")
    print("Client connected")

    await websocket.accept()

    async with websockets.connect(
        AZURE_REALTIME_URL,
        extra_headers={
            "api-key": AZURE_OPENAI_API_KEY
        }
    ) as openai_ws:
        await initialize_session(openai_ws)
        
        stream_sid = None
        latest_media_timestamp = 0
        last_assistant_item = None
        mark_queue = []
        response_start_timestamp_twilio = None

        async def receive_from_twilio():
            nonlocal stream_sid, latest_media_timestamp, response_start_timestamp_twilio, last_assistant_item
            try:
                async for message in websocket.iter_text():
                    data = json.loads(message)
                    if data['event'] == 'media' and openai_ws.open:
                        latest_media_timestamp = int(data['media']['timestamp'])
                        audio_append = {"type": "input_audio_buffer.append","audio": data['media']['payload']}
                        await openai_ws.send(json.dumps(audio_append))
                    elif data['event'] == 'start':
                        stream_sid = data['start']['streamSid']
                        latest_media_timestamp = 0
                        last_assistant_item = None
                    elif data['event'] == 'mark':
                        if mark_queue:
                            mark_queue.pop(0)
            except WebSocketDisconnect:
                if openai_ws.open:
                    await openai_ws.close()

        async def send_to_twilio():
            nonlocal stream_sid, last_assistant_item, response_start_timestamp_twilio
            try:
                async for openai_message in openai_ws:
                    response = json.loads(openai_message)
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
                            await handle_speech_started_event()

            except Exception as e:
                print(f"Error in send_to_twilio: {e}")

        async def handle_speech_started_event():
            nonlocal response_start_timestamp_twilio, last_assistant_item
            if mark_queue and response_start_timestamp_twilio is not None:
                elapsed_time = latest_media_timestamp - response_start_timestamp_twilio
                if last_assistant_item:
                    truncate_event = {
                        "type": "conversation.item.truncate",
                        "item_id": last_assistant_item,
                        "content_index": 0,
                        "audio_end_ms": elapsed_time
                    }
                    await openai_ws.send(json.dumps(truncate_event))
                await websocket.send_json({"event": "clear","streamSid": stream_sid})
                mark_queue.clear()
                last_assistant_item = None
                response_start_timestamp_twilio = None

        async def send_mark(connection, sid):
            if sid:
                mark_event = {"event": "mark","streamSid": sid,"mark": {"name": "responsePart"}}
                await connection.send_json(mark_event)
                mark_queue.append('responsePart')

        await asyncio.gather(receive_from_twilio(), send_to_twilio())