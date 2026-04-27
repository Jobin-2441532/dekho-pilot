from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.core.database import get_db
from app.models import Transaction, SavingsGoal, User, Asset, Recommendation

router = APIRouter()

@router.get("/transactions")
def get_transactions(db: Session = Depends(get_db)):
    rows = db.query(Transaction).order_by(Transaction.date.desc()).all()
    
    return [
        {
            "id": f"t{row.id}",
            "date": row.date,
            "merchant": row.merchant,
            "amount": row.amount,
            "category": row.category,
            "paymentMode": row.payment_mode,
            "notes": row.notes
        }
        for row in rows
    ]

@router.get("/goals")
def get_goals(db: Session = Depends(get_db)):
    rows = db.query(SavingsGoal).all()
    
    # Assign some emojis based on standard strings for frontend mapping
    emoji_map = {"Emergency Fund": "🛡️", "Goa Trip": "🏖️", "New Laptop": "💻"}
    color_map = {"Emergency Fund": "#5C3D2E", "Goa Trip": "#2563EB", "New Laptop": "#7C3AED"}
    
    return [
        {
            "id": f"g{row.id}",
            "name": row.name,
            "emoji": emoji_map.get(row.name, "🎯"),
            "targetAmount": row.target_amount,
            "currentAmount": row.current_amount,
            "deadline": row.deadline,
            "color": color_map.get(row.name, "#10B981")
        }
        for row in rows
    ]

@router.get("/profile")
def get_profile(db: Session = Depends(get_db)):
    user = db.query(User).first()
    
    if not user:
        return {}
        
    return {
        "name": user.name.split()[0],
        "fullName": user.name,
        "incomeRange": user.income_range,
        "monthlyIncome": 75000, # Hardcoded mapped mock for prototype
        "stage": user.financial_stage,
        "purposes": user.goal_type.split(','),
        "monthlyBudget": user.monthly_budget
    }

@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    """Aggregates all-time categories and basic insights based on current transactions"""
    rows = db.query(
        Transaction.category, 
        func.sum(Transaction.amount).label("total")
    ).group_by(Transaction.category).order_by(func.sum(Transaction.amount).desc()).all()
    
    return [
        {"category": row.category, "total": row.total}
        for row in rows
    ]

@router.get("/assets")
def get_assets(db: Session = Depends(get_db)):
    rows = db.query(Asset).all()
    return [
        {
            "id": f"a{row.id}", 
            "name": row.name, 
            "type": row.type, 
            "balance": row.value, 
            "change": 0.0 # Placeholder for prototype
        }
        for row in rows
    ]

@router.get("/opportunities")
def get_opportunities(db: Session = Depends(get_db)):
    rows = db.query(Recommendation).all()
    
    emoji_map = {
        "Safety first": "🛡️",
        "Wealth building": "📈",
        "Quick saving": "💳",
        "You're on track": "🏠"
    }
    
    color_map = {
        "Safety first": "positive",
        "Wealth building": "filter",
        "Quick saving": "warning",
        "You're on track": "positive"
    }
    
    return [
        {
            "id": f"op{row.id}",
            "emoji": emoji_map.get(row.tag, "💡"),
            "title": row.title,
            "description": row.description,
            "why": row.why or "",
            "cta": row.cta,
            "tag": row.tag,
            "tagColor": color_map.get(row.tag, "filter")
        }
        for row in rows
    ]
