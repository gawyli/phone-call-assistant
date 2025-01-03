from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Connect
from config import OUTBOUND_PHONE_NUMBER, ACCOUNT_SID, AUTH_TOKEN, CALLER_ID, WEBHOOK_HOST
import logging

logger = logging.getLogger(__name__)

router_outcoming = APIRouter()

@router_outcoming.get("/outcoming-call")
async def make_outgoing_call():
    logger.info("Initiates the outbound call.")
    if not (OUTBOUND_PHONE_NUMBER and ACCOUNT_SID and AUTH_TOKEN and CALLER_ID):
        logger.warning("Missing configuration or phone number.")
        return {"error": "Missing configuration or phone number."}
    
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    webhook_url = f"https://{WEBHOOK_HOST}/outcoming-call-webhook"
    
    call = client.calls.create(
        to=OUTBOUND_PHONE_NUMBER,
        from_=CALLER_ID,
        url=webhook_url,  # Our TwiML webhook URL
        status_callback=webhook_url,
        status_callback_event=['initiated', 'ringing', 'answered', 'completed']
    )
    logger.info(f"Outbound call initiated: {call.sid}")
    return {"message": f"Calling {OUTBOUND_PHONE_NUMBER}. Call SID: {call.sid}"}

@router_outcoming.api_route("/outcoming-call-webhook", methods=["GET", "POST"])
async def handle_outcoming_call_webhook(request: Request):
    logger.info("Outbound call webhook triggered.")
    response = VoiceResponse()
    response.say("Connecting to the personal assistant.")
    response.pause(length=1)
    
    # Connect to media stream websocket
    host = WEBHOOK_HOST #request.url.hostname <- in prod we use this instead hard coded
    connect = Connect()
    connect.stream(url=f'wss://{host}/media-stream')
    response.append(connect)
    
    logger.info("Returning TwiML for outbound call.")
    return HTMLResponse(content=str(response), media_type="application/xml")