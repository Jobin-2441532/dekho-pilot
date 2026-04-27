"""
Celery task for feature recomputation after new transaction batches.
"""
from datetime import date
from app.celery_app import celery_app
from app.core.database import SessionLocal
from app.services.feature_service import feature_service


@celery_app.task(name="tasks.recompute_features")
def recompute_features_task(user_id: int):
    """
    Recompute monthly and profile features for a user.
    Should be triggered after every new batch of transactions is ingested.
    """
    db = SessionLocal()
    try:
        current_month = date.today().strftime("%Y-%m")
        monthly = feature_service.compute_monthly_features(db, user_id, current_month)
        profile = feature_service.compute_user_profile(db, user_id, months=3)
        return {
            "status": "ok",
            "month": current_month,
            "total_spend": monthly.get("total_spend"),
            "avg_monthly_spend": profile.get("avg_monthly_spend"),
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}
    finally:
        db.close()
