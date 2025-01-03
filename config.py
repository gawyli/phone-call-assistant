import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PORT = int(os.getenv('PORT', 5050))
VOICE = 'ballad'
SYSTEM_MESSAGE = (
    "You are best personal motivator who loves to chat about with people "
    "about anything that makes them happy, in move and inspired. "
    "Your role is to brake the morning brain fog and get the day started "
    "by calling out at sheduled morning time and wake up your frineds."
    "Always stay positive, but work in a joke when appropriate."
)
SHOW_TIMING_MATH = False
LOG_EVENT_TYPES = [
    'error', 'response.content.done', 'rate_limits.updated',
    'response.done', 'input_audio_buffer.committed',
    'input_audio_buffer.speech_stopped', 'input_audio_buffer.speech_started',
    'session.created'
]
OUTBOUND_PHONE_NUMBER = "07402033899"
ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
CALLER_ID = os.getenv('TWILIO_CALLER_ID')  # e.g. +1234567890
WEBHOOK_HOST = os.getenv('PUBLIC_WEBHOOK_HOST')   # e.g. ngrok.net