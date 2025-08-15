"""
Celery background tasks
"""
from celery import current_task
from celery_app import celery_app
import time
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def process_data(self, data: dict):
    """
    Example data processing task
    """
    try:
        # Simulate processing
        total_items = data.get("total", 100)
        
        for i in range(total_items):
            # Update task progress
            self.update_state(
                state="PROGRESS",
                meta={"current": i + 1, "total": total_items}
            )
            time.sleep(0.1)  # Simulate work
        
        result = {
            "status": "completed",
            "processed_items": total_items,
            "task_id": self.request.id
        }
        
        logger.info(f"Data processing completed: {result}")
        return result
        
    except Exception as exc:
        logger.error(f"Data processing failed: {exc}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)


@celery_app.task
def send_email(recipient: str, subject: str, body: str):
    """
    Example email sending task
    """
    try:
        # Simulate email sending
        logger.info(f"Sending email to {recipient}: {subject}")
        time.sleep(2)  # Simulate email sending delay
        
        return {
            "status": "sent",
            "recipient": recipient,
            "subject": subject
        }
        
    except Exception as exc:
        logger.error(f"Email sending failed: {exc}")
        raise exc


@celery_app.task
def cleanup_old_files():
    """
    Periodic task to cleanup old files
    """
    try:
        # Example cleanup logic
        temp_dir = "/tmp"
        cleaned_files = 0
        
        # This is just an example - implement actual cleanup logic
        logger.info(f"Starting cleanup of {temp_dir}")
        
        # In real implementation, you would clean up old logs, temp files, etc.
        cleaned_files = 0  # Placeholder
        
        result = {
            "status": "completed",
            "cleaned_files": cleaned_files,
            "directory": temp_dir
        }
        
        logger.info(f"Cleanup completed: {result}")
        return result
        
    except Exception as exc:
        logger.error(f"Cleanup failed: {exc}")
        raise exc


@celery_app.task
def health_check():
    """
    Health check task
    """
    try:
        # Check system health
        import psutil
        
        health_data = {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent,
            "timestamp": time.time()
        }
        
        logger.info(f"Health check completed: {health_data}")
        return health_data
        
    except ImportError:
        # psutil not installed, return basic health
        return {
            "status": "healthy",
            "timestamp": time.time()
        }
    except Exception as exc:
        logger.error(f"Health check failed: {exc}")
        return {
            "status": "unhealthy",
            "error": str(exc),
            "timestamp": time.time()
        }