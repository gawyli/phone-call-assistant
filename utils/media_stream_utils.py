from rtclient import (
    ItemCreateMessage,
    UserMessageItem,
    InputTextContentPart,
    ResponseCreateMessage,
    SessionUpdateMessage,
    SessionUpdateParams,
    ServerVAD,
)
import logging

logger = logging.getLogger(__name__)

async def initialize_session(client_ws):
    logger.info(f"Initializing {client_ws._azure_deployment} session.")
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

    content_part = InputTextContentPart(
        text="Greet the user with very positive Morning Hello. Ask them how was the sleep last night."
    )
    initial_conversation_item = ItemCreateMessage(item=UserMessageItem(content=[content_part]))
    
    await client_ws.send(initial_conversation_item)
    await client_ws.send(ResponseCreateMessage())