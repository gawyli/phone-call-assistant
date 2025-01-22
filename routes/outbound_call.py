from fastapi import APIRouter, Request, Query, Depends
from fastapi.responses import HTMLResponse
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Connect
from utils.twilio_auth_utils import twilio_signature_verifier
from utils.azure_auth_utils import azure_scheme
from config import OUTBOUND_PHONE_NUMBER, ACCOUNT_SID, AUTH_TOKEN, CALLER_ID, WEBHOOK_HOST
import logging

logger = logging.getLogger(__name__)

router_outcoming = APIRouter()

@router_outcoming.get("/outcoming-call")    #you can add depends on azure_schema to enable Azure Auth e.g: dependencies=[Depends(azure_scheme)]
async def make_outgoing_call(phone_number: str = Query(..., description="The phone number to query")):
    logger.info("Initiates the outbound call.")
    if not (phone_number and ACCOUNT_SID and AUTH_TOKEN and CALLER_ID):
        logger.warning("Missing configuration or phone number.")
        return {"error": "Missing configuration or phone number."}
    
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    webhook_url = f"https://{WEBHOOK_HOST}/outcoming-call-webhook"
    
    call = client.calls.create(
        to=phone_number,
        from_=CALLER_ID,
        url=webhook_url,  # Our TwiML webhook URL
        status_callback=webhook_url,
        status_callback_event=['initiated', 'ringing', 'answered', 'completed']
    )
    logger.info(f"Outbound call initiated: {call.sid}")
    return {"message": f"Calling {OUTBOUND_PHONE_NUMBER}. Call SID: {call.sid}"}

@router_outcoming.api_route("/outcoming-call-webhook", methods=["POST"], dependencies=[Depends(twilio_signature_verifier)])
async def handle_outcoming_call_webhook(request: Request):
    logger.info("Outbound call webhook triggered.")

    # Get form data from the request
    form_data = await request.form()
    phone_number = form_data.get('To')

    response = VoiceResponse()
    response.say("Connecting to the personal assistant.")
    response.pause(length=1)
    
    # Connect to media stream websocket
    host = WEBHOOK_HOST #request.url.hostname <- in prod we use this instead of hardcoded value
    connect = Connect()
    
    stream = connect.stream(url=f'wss://{host}/media-stream')
    if phone_number:
        stream.parameter(name="phone_number", value=phone_number)  # Pass phone_number as a query parameter
    
    response.append(connect)
    
    logger.info("Returning TwiML for outbound call.")
    return HTMLResponse(content=str(response), media_type="application/xml")