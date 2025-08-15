"""
File: celery_app.py

Overview:
Celery application configuration for background task processing.

Purpose:
Configures Celery with Redis broker, task routing, and monitoring
for the AI Hub AI/ML Wrangler background processing system.

Dependencies:
- celery: Distributed task queue
- app.config: Configuration settings
- app.tasks: Task definitions

Last Modified: 2025-08-15
Author: Claude
"""

import logging
from celery import Celery
from celery.signals import setup_logging

from app.config import settings

# Configure logging
logger = logging.getLogger(__name__)


@setup_logging.connect
def config_loggers(*args, **kwargs):
    """Configure Celery logging."""
    from logging.config import dictConfig
    
    LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'level': 'INFO',
            },
        },
        'root': {
            'level': 'INFO',
            'handlers': ['console'],
        },
        'loggers': {
            'celery': {
                'level': 'INFO',
                'handlers': ['console'],
                'propagate': False,
            },
        },
    }
    dictConfig(LOGGING_CONFIG)


# Create Celery application
celery_app = Celery(
    "aihub_ml_wrangler",
    broker=settings.celery.broker_url,
    backend=settings.celery.result_backend,
    include=[
        "app.tasks.imputation_tasks",
        "app.tasks.analysis_tasks",
    ]
)

# Configure Celery
celery_app.conf.update(
    # Task serialization
    task_serializer=settings.celery.task_serializer,
    accept_content=settings.celery.accept_content,
    result_serializer=settings.celery.result_serializer,
    
    # Timezone settings
    timezone=settings.celery.timezone,
    enable_utc=settings.celery.enable_utc,
    
    # Task execution settings
    task_acks_late=settings.celery.task_acks_late,
    task_reject_on_worker_lost=settings.celery.task_reject_on_worker_lost,
    worker_prefetch_multiplier=settings.celery.worker_prefetch_multiplier,
    
    # Task routing
    task_routes={
        'app.tasks.imputation_tasks.*': {'queue': 'imputation'},
        'app.tasks.analysis_tasks.*': {'queue': 'analysis'},
    },
    
    # Worker settings
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=True,
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    result_persistent=True,
    
    # Task result settings
    task_track_started=True,
    task_send_sent_event=True,
    
    # Beat scheduler settings (for periodic tasks)
    beat_schedule={
        'cleanup-expired-results': {
            'task': 'app.tasks.maintenance_tasks.cleanup_expired_results',
            'schedule': 3600.0,  # Run every hour
        },
        'health-check': {
            'task': 'app.tasks.maintenance_tasks.health_check',
            'schedule': 300.0,  # Run every 5 minutes
        },
    },
    
    # Monitoring
    worker_send_task_events=True,
    task_send_events=True,
    
    # Error handling
    task_ignore_result=False,
    task_store_errors_even_if_ignored=True,
    
    # Security
    worker_hijack_root_logger=False,
    worker_log_color=False,
    
    # Task time limits
    task_soft_time_limit=1800,  # 30 minutes
    task_time_limit=3600,       # 1 hour
)

# Task discovery
celery_app.autodiscover_tasks([
    "app.tasks"
], force=True)


@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery configuration."""
    print(f'Request: {self.request!r}')
    return "Debug task completed successfully"


# Task failure handler
@celery_app.task(bind=True)
def task_failure_handler(self, task_id, error, traceback):
    """Handle task failures."""
    logger.error(f"Task {task_id} failed: {error}")
    logger.error(f"Traceback: {traceback}")


# Celery signal handlers
from celery.signals import (
    task_prerun,
    task_postrun,
    task_failure,
    task_success,
    worker_ready,
    worker_shutdown
)


@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **kwds):
    """Handle task pre-run."""
    logger.info(f"Task {task.name} [{task_id}] starting")


@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, 
                        retval=None, state=None, **kwds):
    """Handle task post-run."""
    logger.info(f"Task {task.name} [{task_id}] completed with state: {state}")


@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, traceback=None, einfo=None, **kwds):
    """Handle task failures."""
    logger.error(f"Task {sender.name} [{task_id}] failed: {exception}")


@task_success.connect
def task_success_handler(sender=None, result=None, **kwargs):
    """Handle task success."""
    logger.info(f"Task {sender.name} completed successfully")


@worker_ready.connect
def worker_ready_handler(sender=None, **kwargs):
    """Handle worker ready signal."""
    logger.info(f"Celery worker {sender.hostname} is ready")


@worker_shutdown.connect
def worker_shutdown_handler(sender=None, **kwargs):
    """Handle worker shutdown signal."""
    logger.info(f"Celery worker {sender.hostname} is shutting down")


if __name__ == '__main__':
    celery_app.start()