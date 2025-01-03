import logging
from fastapi import FastAPI
from routes.incoming_call import router_incoming
from routes.outbound_call import router_outcoming
from services.scheduler import schedule_outgoing_call
from services.openai_ws import router_media
from config import OPENAI_API_KEY, PORT

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("Main app starting...")
if not OPENAI_API_KEY:
    raise ValueError('Missing the OpenAI API key. Please set it in the .env file.')

app = FastAPI()
#app.include_router(router_incoming)
app.include_router(router_media)
app.include_router(router_outcoming)

@app.get("/", tags=["root"])
async def index_page():
    logger.info("Root endpoint invoked.")
    return {"message": "Twilio Media Stream Server is running!"}

if __name__ == "__main__":
    logger.info("Scheduling outgoing call at 07:00")
    # e.g. schedule call at 07:00
    schedule_outgoing_call("14:04")
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
