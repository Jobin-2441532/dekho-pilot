from fastapi import APIRouter, HTTPException, Depends

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(*args, **kwargs):
    raise HTTPException(
        status_code=410, 
        detail="The old chatbot has been completely deleted. Please use Chatbot 2.0 (port 8002)."
    )

@router.post("/chat/message")
async def simple_chat_endpoint(*args, **kwargs):
    raise HTTPException(
        status_code=410, 
        detail="The old chatbot has been completely deleted. Please use Chatbot 2.0 (port 8002)."
    )

from app.api.endpoints.auth import get_current_user
from app.core.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import text

@router.get("/chat/history")
async def get_chat_history(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        rows = db.execute(
            text("SELECT role, content, timestamp FROM conversations WHERE user_id = :uid ORDER BY timestamp ASC, role DESC"),
            {"uid": str(current_user.id)}
        ).fetchall()
        return [
            {
                "role": r.role,
                "content": r.content,
                "timestamp": r.timestamp
            }
            for r in rows
        ]
    except Exception as e:
        # Table might not exist yet if chatbot hasn't started, or query failed
        return []

@router.delete("/chat/history")
async def clear_chat_history(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        db.execute(
            text("DELETE FROM conversations WHERE user_id = :uid"),
            {"uid": str(current_user.id)}
        )
        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear chat history: {str(e)}"
        )

@router.post("/chat/action")
async def chat_action_endpoint(*args, **kwargs):
    raise HTTPException(
        status_code=410, 
        detail="The old chatbot has been completely deleted. Please use Chatbot 2.0 (port 8002)."
    )
