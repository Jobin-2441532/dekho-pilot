from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.endpoints.auth import get_current_user
from app.models.user import User
from app.models.notification import Notification

router = APIRouter()

@router.get("/")
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notifications = db.query(Notification).filter(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).limit(20).all()
    
    return [{
        "id": n.id,
        "rule_type": n.rule_type,
        "title": n.title,
        "message": n.message,
        "is_read": n.is_read,
        "created_at": n.created_at.isoformat()
    } for n in notifications]

@router.post("/{notification_id}/read")
def mark_read(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if notification_id == "all":
        db.query(Notification).filter(Notification.user_id == current_user.id).update({"is_read": True})
    else:
        db.query(Notification).filter(
            Notification.id == int(notification_id), 
            Notification.user_id == current_user.id
        ).update({"is_read": True})
        
    db.commit()
    return {"status": "ok"}
