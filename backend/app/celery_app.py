"""
Celery application — configured to use Redis as both broker and result backend.
Redis is already running on port 6379 via Docker.
"""
from celery import Celery
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "dekho",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "app.tasks.parsing",
        "app.tasks.features",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    result_expires=3600,  # Results expire after 1 hour
)
