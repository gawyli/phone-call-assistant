from collections import OrderedDict
from fastapi import Request, HTTPException
from twilio.request_validator import RequestValidator
from config import AUTH_TOKEN, WEBHOOK_HOST
import os
import logging

logger = logging.getLogger(__name__)

validator = RequestValidator(AUTH_TOKEN)

async def twilio_signature_verifier(request: Request) -> bool:
    # Try both header cases for Twilio signature
    signature = request.headers.get("X-Twilio-Signature") or request.headers.get("x-twilio-signature")
    if not signature:
        raise HTTPException(status_code=401, detail="Missing Twilio signature")
    
    uri = f"https://{WEBHOOK_HOST}/outcoming-call-webhook"

    try:
        params={}
        # Handle POST requests
        if request.method == "POST":
            content_type = request.headers.get("Content-Type", "")
            if "application/json" not in content_type:
                form_data = await request.form()
                # Sort parameters alphabetically
                params.update(OrderedDict(sorted(dict(form_data).items(), key=lambda x: x[0])))

        logger.debug(f"Validating URL: {uri}")
        logger.debug(f"With sorted params: {params}")
        
        is_valid = validator.validate(uri, params, signature)
        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid Twilio signature")
        return True

    except Exception as e:
        logger.error(f"Error validating Twilio signature: {str(e)}")
        raise HTTPException(status_code=401, detail="Error validating request")