"""
File: celery.py

Overview:
Celery configuration for background task processing

Purpose:
Configures Celery app with Redis broker and task routing

Dependencies:
- celery: Distributed task queue
- redis: Message broker

Last Modified: 2025-08-15
Author: Claude
"""

import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "aihub_worker",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["backend.tasks.ml_tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_routes={
        "backend.tasks.ml_tasks.analyze_dataset": {"queue": "ml_analysis"},
        "backend.tasks.ml_tasks.impute_missing_data": {"queue": "data_processing"},
        "backend.tasks.ml_tasks.calculate_correlations": {"queue": "data_processing"},
    },
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
)