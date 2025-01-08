import logging
import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from routes.outbound_call import make_outgoing_call

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def schedule_outgoing_call(call_time: str = "07:00"):
    """Schedule the outgoing call at HH:MM every day."""
    hour, minute = map(int, call_time.split(":"))
    logger.info(f"Scheduling job for daily_outgoing_call at {hour}:{minute}")

    # Wrap async call in a function the scheduler can handle
    def job_wrapper():
        logger.info("APSCHEDULER: Triggering async outgoing call.")
        asyncio.run(make_outgoing_call())

    scheduler.add_job(
        job_wrapper,
        "cron",
        hour=hour,
        minute=minute,
        id="daily_outgoing_call",
        replace_existing=True
    )
    scheduler.start()
    logger.info("BackgroundScheduler started.")
    return scheduler