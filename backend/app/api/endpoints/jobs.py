"""
Jobs API — exposes job status polling for Celery background tasks.
"""
from fastapi import APIRouter, HTTPException
from app.celery_app import celery_app

router = APIRouter()


@router.get("/{job_id}/status")
def get_job_status(job_id: str):
    """
    Poll the status of a background Celery task.

    Returns:
        job_id, status (PENDING | STARTED | SUCCESS | FAILURE | RETRY), result (if done)
    """
    result = celery_app.AsyncResult(job_id)

    response = {
        "job_id": job_id,
        "status": result.status,
    }

    if result.status == "SUCCESS":
        response["result"] = result.result
    elif result.status == "FAILURE":
        response["error"] = str(result.result)

    return response
