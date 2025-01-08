import logging
import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the scheduler on app startup
    scheduler = schedule_outgoing_call("11:30")
    yield
    # Shutdown the scheduler on app shutdown
    scheduler.shutdown()
    logger.info("Scheduler shut down.")


def get_environment():
    """
    Determines if the app is running locally or in a cloud environment (Azure).
    Returns a string indicating the environment type: 'local' or 'azure'.
    """
    if "WEBSITE_INSTANCE_ID" in os.environ:
        # This environment variable is specific to Azure App Services
        return "azure"
    else:
        return "local"

# Start the app
if __name__ == "__main__":
    env = get_environment()
    if env == "local":
        logger.info("Running locally with Uvicorn...")
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=PORT)
    else:
        logger.info("Running on Azure...")
        # Azure will manage the server with a specific port
        port = int(os.getenv("PORT", 8000))
        logger.info(f"Azure environment detected. Using port {port}.")
