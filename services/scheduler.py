from apscheduler.schedulers.background import BackgroundScheduler
from ..routes.outbound_call import make_outgoing_call

scheduler = BackgroundScheduler()

def schedule_outgoing_call(call_time: str = "07:00"):
    """Schedule the outgoing call at HH:MM every day."""
    hour, minute = map(int, call_time.split(":"))
    scheduler.add_job(
        make_outgoing_call,
        "cron",
        hour=hour,
        minute=minute,
        id="daily_outgoing_call",
        replace_existing=True
    )
    scheduler.start()