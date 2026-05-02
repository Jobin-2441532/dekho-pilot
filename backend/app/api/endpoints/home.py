from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from datetime import datetime, date
from app.core.database import get_db
from app.models import Transaction, User
from app.api.endpoints.auth import get_current_user

router = APIRouter()

@router.get("/reflection")
def get_home_reflection(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate today's reflection data for the Home screen ReflectionCard.
    Analyzes today's spending versus average and determines the "mood".
    """
    today_str = date.today().isoformat()
    
    # Get all debits for this user
    all_txns = db.query(Transaction).filter(
        Transaction.user_id == current_user.id, 
        Transaction.direction == 'debit'
    ).all()
    
    # Calculate average daily spend
    unique_days = len(set(t.date[:10] for t in all_txns if t.date)) or 1
    total_spend = sum(t.amount for t in all_txns)
    avg_daily_spend = total_spend / unique_days
    
    # Today's transactions
    today_txns = [t for t in all_txns if t.date and t.date.startswith(today_str)]
    today_spend = sum(t.amount for t in today_txns)
    
    vs_average_percent = 0
    if avg_daily_spend > 0:
        vs_average_percent = round(((today_spend - avg_daily_spend) / avg_daily_spend) * 100)
    
    # Determine top category today
    category_totals = {}
    for t in today_txns:
        cat = t.category or "Others"
        category_totals[cat] = category_totals.get(cat, 0) + t.amount
        
    top_category = None
    if category_totals:
        top_category = max(category_totals.items(), key=lambda x: x[1])[0]
        
    # Logic to determine mood
    # 'quiet': Zero or near-zero spend
    if today_spend < 50:
        return {
            "mood": "quiet",
            "headline": "A quiet day for your wallet.",
            "subtext": "Barely anything went out today. Rest days matter.",
            "top_category": top_category or "None",
            "today_spend": today_spend,
            "vs_average_percent": vs_average_percent
        }
    
    # 'big_ticket': Single transaction > 40% of daily average
    if any(t.amount > (avg_daily_spend * 0.4) for t in today_txns) and len(today_txns) > 0 and avg_daily_spend > 500:
        return {
            "mood": "big_ticket",
            "headline": "One big move today. That's okay.",
            "subtext": "A larger purchase came through. Everything else stayed steady.",
            "top_category": top_category,
            "today_spend": today_spend,
            "vs_average_percent": vs_average_percent
        }
        
    # 'generous': Transfer or gift transaction detected
    if any(c in str(t.category).lower() for c in ["transfer", "gift", "donation", "family"] for t in today_txns):
        return {
            "mood": "generous",
            "headline": "You showed up for someone today.",
            "subtext": "A transfer went out — generosity is part of your story too.",
            "top_category": top_category,
            "today_spend": today_spend,
            "vs_average_percent": vs_average_percent
        }

    # 'productive': Essentials only, low spend
    essential_cats = ["groceries", "bills", "utilities", "housing", "essentials", "health"]
    if top_category and top_category.lower() in essential_cats and today_spend <= avg_daily_spend:
        return {
            "mood": "productive",
            "headline": "A clean, intentional day.",
            "subtext": f"Only essentials like {top_category.lower()} today. Your wallet thanks you.",
            "top_category": top_category,
            "today_spend": today_spend,
            "vs_average_percent": vs_average_percent
        }
        
    # 'weekend': Weekend day + leisure category
    today_weekday = date.today().weekday()
    leisure_cats = ["food & dining", "entertainment", "shopping", "leisure", "travel"]
    if today_weekday >= 5 and top_category and top_category.lower() in leisure_cats:
        return {
            "mood": "weekend",
            "headline": "Weekend mode — earned and enjoyed.",
            "subtext": f"A bit of leisure spending on {top_category.lower()}. You've worked for it.",
            "top_category": top_category,
            "today_spend": today_spend,
            "vs_average_percent": vs_average_percent
        }
        
    # 'comfort': Food or Entertainment spike
    if top_category and top_category.lower() in leisure_cats and today_spend > avg_daily_spend:
        return {
            "mood": "comfort",
            "headline": "Today was a comfort spending day.",
            "subtext": f"You spent a little more on {top_category.lower()} than usual. That's okay.",
            "top_category": top_category,
            "today_spend": today_spend,
            "vs_average_percent": vs_average_percent
        }
        
    # Fallback to 'calm'
    return {
        "mood": "calm",
        "headline": "Nothing unusual — just a regular day.",
        "subtext": f"{top_category or 'Everything'} was within normal range.",
        "top_category": top_category or "None",
        "today_spend": today_spend,
        "vs_average_percent": vs_average_percent
    }
