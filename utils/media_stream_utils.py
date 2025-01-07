from rtclient import (
    ItemCreateMessage,
    UserMessageItem,
    UserContentPart,
    InputTextContentPart,
    ResponseCreateMessage,
    SessionUpdateMessage,
    SessionUpdateParams,
    ServerVAD,
)
import logging

logger = logging.getLogger(__name__)

async def initialize_session(client_ws):
    logger.info("Initializing OpenAI session.")
    session_update = SessionUpdateMessage(session=SessionUpdateParams(
                                            voice="dan",
                                            input_audio_format="g711_ulaw",
                                            output_audio_format="g711_ulaw",
                                            turn_detection=ServerVAD(type="server_vad"),                  
                                            )
                                          )
    
    await client_ws.send(session_update)
    await send_initial_conversation_item(client_ws)

async def send_initial_conversation_item(client_ws):
    logger.info("Sending initial conversation item.")  
    initial_conversation_item = ItemCreateMessage(item=UserMessageItem(content=UserContentPart(
        InputTextContentPart(text="Greet the user with very positive Morning Hello. Ask them how was the sleep last night."))))
    
    await client_ws.send(initial_conversation_item)
    await client_ws.send(ResponseCreateMessage())