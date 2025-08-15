"""
Celery application configuration for background tasks
"""
from celery import Celery
import os

# Get Redis URL from environment
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/1")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/2")

# Create Celery instance
celery_app = Celery(
    "aihub_celery",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["celery_tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    result_expires=3600,
    
    # Task routing
    task_routes={
        "celery_tasks.process_data": {"queue": "data_processing"},
        "celery_tasks.send_email": {"queue": "notifications"},
        "celery_tasks.cleanup_old_files": {"queue": "maintenance"},
    },
    
    # Beat schedule for periodic tasks
    beat_schedule={
        "cleanup-every-day": {
            "task": "celery_tasks.cleanup_old_files",
            "schedule": 86400.0,  # 24 hours
        },
        "health-check-every-minute": {
            "task": "celery_tasks.health_check",
            "schedule": 60.0,  # 1 minute
        },
    },
)

# Auto-discover tasks
celery_app.autodiscover_tasks()

if __name__ == "__main__":
    celery_app.start()