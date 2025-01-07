from scipy.signal import resample
import logging
import json
import config

from rtclient import (
    ServerVAD,
    UserMessageItem,
    UserContentPart,
    InputTextContentPart,
    SessionUpdateMessage,
    SessionUpdateParams,
)

#logger = logging.getLogger(__name__)

#async def initialize_session(azure_openai_ws):
    #logger.info("Initializing OpenAI session.")
    
    

    #await send_initial_conversation_item(azure_openai_ws)

#async def send_initial_conversation_item(azure_openai_ws):
    #logger.info("Sending initial conversation item.")

    #await azure_openai_ws.send(UserMessageItem(content=UserContentPart(InputTextContentPart("Greet a human with morning positive atitude"))))
