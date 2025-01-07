import logging
from fastapi import FastAPI
from routes.incoming_call import router_incoming
from routes.outbound_call import router_outcoming
from services.media_stream import router_media
from services.scheduler import schedule_outgoing_call
from config import PORT

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("Main app starting...")

app = FastAPI()
#app.include_router(router_incoming)
app.include_router(router_media)
app.include_router(router_outcoming)

@app.get("/", tags=["root"])
async def index_page():
    logger.info("Root endpoint invoked.")
    return {"message": "Twilio Media Stream Server is running!"}

if __name__ == "__main__":
    logger.info("Scheduling outgoing call")
    # e.g. schedule call at 07:00
    schedule_outgoing_call("19:51")
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
