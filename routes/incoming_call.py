from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from twilio.twiml.voice_response import VoiceResponse, Connect
import logging

logger = logging.getLogger(__name__)

router_incoming = APIRouter()

@router_incoming.api_route("/incoming-call", methods=["GET", "POST"])
async def handle_incoming_call(request: Request):
    logger.info("Incoming call webhook triggered.")
    response = VoiceResponse()
    response.say("Please wait while we connect your call.")
    response.pause(length=1)
    response.say("O.K. you can start talking!")
    host = "turbo-chainsaw-p9w4gw4qqqq2r76p-5050.app.github.dev/" #request.url.hostname
    connect = Connect()
    connect.stream(url=f'wss://{host}/media-stream')
    response.append(connect)
    return HTMLResponse(content=str(response), media_type="application/xml")