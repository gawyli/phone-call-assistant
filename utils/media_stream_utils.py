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

#TODO: Add this to the rtclient models (test)
tools = [
    {
        "type": "function",
        "name": "weather_function",
        "description": "Give today's weather based on the specified location.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The location given from the user e.g. New York, London, Warsaw.",
                }
            },
            "required": ["location"]
        }
    }
]

async def initialize_session(client_ws):
    logger.info(f"Initializing {client_ws._url} session.")
    session_update = SessionUpdateMessage(session=SessionUpdateParams(
                                            voice="alloy",
                                            input_audio_format="g711_ulaw",
                                            output_audio_format="g711_ulaw",
                                            turn_detection=ServerVAD(type="server_vad"),
                                            tools=tools,
                                            tool_choice="auto",                  
                                            )
                                          )
    
    await client_ws.send(session_update)

async def send_default_conversation_item(client_ws):
    logger.info("Sending initial conversation item.")  

    content_part = InputTextContentPart(
        text="Greet the user with very positive Morning Hello. Ask them how was the sleep last night."
    )
    initial_conversation_item = ItemCreateMessage(item=UserMessageItem(content=[content_part]))
    
    await client_ws.send(initial_conversation_item)
    await client_ws.send(ResponseCreateMessage())
    
async def send_custom_conversation_item(client_ws, text):
    logger.info("Sending initial conversation item.")  

    content_part = InputTextContentPart(
        text=text
    )
    initial_conversation_item = ItemCreateMessage(item=UserMessageItem(content=[content_part]))
    
    await client_ws.send(initial_conversation_item)
    await client_ws.send(ResponseCreateMessage())
    
async def send_user_conversation_item(client_ws, user_id):
    logger.info("Sending user custom conversation item from memory.")  

    content_part = InputTextContentPart(
        text=""
    )
    initial_conversation_item = ItemCreateMessage(item=UserMessageItem(content=[content_part]))
    
    await client_ws.send(initial_conversation_item)
    await client_ws.send(ResponseCreateMessage())