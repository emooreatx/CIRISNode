from celery import Celery
from cirisnode.config import settings # Import settings

# Configure Celery
celery_app = Celery(
    "cirisnode",
    broker=settings.REDIS_URL,  # Use REDIS_URL from settings
    backend=settings.REDIS_URL  # Use REDIS_URL from settings
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True, # Added this line
)

# Task registration is now handled in cirisnode/celery_tasks.py
