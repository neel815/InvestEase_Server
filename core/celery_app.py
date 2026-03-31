"""
Celery app configuration with beat schedule for periodic tasks.
"""

from celery import Celery
from celery.schedules import crontab

# Initialize Celery app
app = Celery(
    "investease",
    broker="redis://localhost:6379/1",  # Redis broker on DB 1 (separate from cache)
    backend="redis://localhost:6379/1",  # Results backend
)

# Celery beat schedule: run cache_top_funds task daily at midnight
app.conf.beat_schedule = {
    "cache-top-funds-daily": {
        "task": "tasks.fund_cache_task.cache_top_funds",
        "schedule": crontab(hour=0, minute=0),  # Run at midnight UTC daily
    },
}

# Additional Celery configuration
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
