"""
Celery app configuration with beat schedule for periodic tasks.
"""

from celery import Celery

# Initialize Celery app
app = Celery(
    "investease",
    broker="redis://localhost:6379/1",  # Redis broker on DB 1 (separate from cache)
    backend="redis://localhost:6379/1",  # Results backend
)

# Celery beat schedule - currently empty, tasks will be added in future chunks
app.conf.beat_schedule = {}

# Additional Celery configuration
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
