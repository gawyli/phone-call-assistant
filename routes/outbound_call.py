from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Connect
from ..config import OUTBOUND_PHONE_NUMBER, ACCOUNT_SID, AUTH_TOKEN, CALLER_ID, NGROK_URL

router_outcoming = APIRouter()

@router_outcoming.get("/outcoming-call")
async def make_outgoing_call():
    """Initiates the outbound call"""
    if not (OUTBOUND_PHONE_NUMBER and ACCOUNT_SID and AUTH_TOKEN and CALLER_ID):
        return {"error": "Missing configuration or phone number."}
    
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    webhook_url = f"https://{NGROK_URL}/outcoming-call-webhook"
    
    call = client.calls.create(
        to=OUTBOUND_PHONE_NUMBER,
        from_=CALLER_ID,
        url=webhook_url,  # Our TwiML webhook URL
        status_callback=webhook_url,
        status_callback_event=['initiated', 'ringing', 'answered', 'completed']
    )
    return {"message": f"Calling {OUTBOUND_PHONE_NUMBER}. Call SID: {call.sid}"}

@router_outcoming.api_route("/outcoming-call-webhook", methods=["GET", "POST"])
async def handle_outcoming_call_webhook(request: Request):
    """Generates TwiML when call is answered"""
    response = VoiceResponse()
    response.say("Connecting to the personal assistant.")
    response.pause(length=1)
    
    # Connect to media stream websocket
    host = request.url.hostname #webhook
    connect = Connect()
    connect.stream(url=f'wss://{host}/media-stream')
    response.append(connect)
    
    return HTMLResponse(content=str(response), media_type="application/xml")