from fastapi import APIRouter
from twilio.rest import Client
from ..config import OUTBOUND_PHONE_NUMBER, ACCOUNT_SID, AUTH_TOKEN, CALLER_ID

router_outcoming = APIRouter()

@router_outcoming.get("/outcoming-call")
async def make_outgoing_call():
    if not (OUTBOUND_PHONE_NUMBER and ACCOUNT_SID and AUTH_TOKEN and CALLER_ID):
        return {"error": "Missing configuration or phone number."}
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    call = client.calls.create(
        to=OUTBOUND_PHONE_NUMBER,
        from_=CALLER_ID,
        url="https://demo.twilio.com/docs/voice.xml"
    )
    return {"message": f"Calling {OUTBOUND_PHONE_NUMBER}. Call SID: {call.sid}"}