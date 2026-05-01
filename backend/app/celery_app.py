"""
Celery application — configured to use Redis as both broker and result backend.
Redis is already running on port 6379 via Docker.

NOTE: Celery is optional for local development. If celery is not installed
or Redis is unavailable, a lightweight mock is used so the server starts
without background task support.
"""
import os
import logging

logger = logging.getLogger("dekho.celery")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


class _MockCelery:
    """Fallback when Celery is unavailable. Jobs endpoint will return 'unavailable'."""
    class _MockResult:
        status = "UNAVAILABLE"
        result = None

    def AsyncResult(self, job_id: str):
        return self._MockResult()


try:
    from celery import Celery

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
    logger.info("Celery initialized with Redis broker.")

except ImportError:
    logger.warning("Celery not installed — background jobs disabled. Install with: pip install celery[redis]")
    celery_app = _MockCelery()
except Exception as e:
    logger.warning(f"Celery init failed ({e}) — background jobs disabled.")
    celery_app = _MockCelery()
