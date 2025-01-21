from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from twilio.twiml.voice_response import VoiceResponse, Connect
from utils.twilio_auth_utils import twilio_signature_verifier
import logging

logger = logging.getLogger(__name__)

router_incoming = APIRouter()

@router_incoming.api_route("/incoming-call", methods=["GET", "POST"], dependencies=[Depends(twilio_signature_verifier)])
async def handle_incoming_call(request: Request):
    logger.info("Incoming call webhook triggered.")
    response = VoiceResponse()
    response.say("Please wait while we connect your call.")
    response.pause(length=1)
    response.say("O.K. you can start talking!")
    host = request.url.hostname
    connect = Connect()
    connect.stream(url=f'wss://{host}/media-stream')
    response.append(connect)
    return HTMLResponse(content=str(response), media_type="application/xml")