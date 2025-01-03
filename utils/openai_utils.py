import logging
import json
import config

logger = logging.getLogger(__name__)

async def initialize_session(openai_ws):
    logger.info("Initializing OpenAI session.")
    session_update = {
        "type": "session.update",
        "session": {
            "turn_detection": {"type": "server_vad"},
            "input_audio_format": "g711_ulaw",
            "output_audio_format": "g711_ulaw",
            "voice": config.VOICE,
            "instructions": config.SYSTEM_MESSAGE,
            "modalities": ["text", "audio"],
            "temperature": 0.8,
        }
    }
    await openai_ws.send(json.dumps(session_update))
    await send_initial_conversation_item(openai_ws)

async def send_initial_conversation_item(openai_ws):
    logger.info("Sending initial conversation item.")
    initial_conversation_item = {
        "type": "conversation.item.create",
        "item": {
            "type": "message",
            "role": "user",
            "content": [
                {"type": "input_text", "text": "Greet the user with Morning Hello. Ask them how was the sleep last night."}
            ]
        }
    }
    await openai_ws.send(json.dumps(initial_conversation_item))
    await openai_ws.send(json.dumps({"type": "response.create"}))