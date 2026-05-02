from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from datetime import date, datetime
from app.core.database import get_db
from app.models import Transaction, User
from app.api.endpoints.auth import get_current_user

router = APIRouter()

INSIGHT_CONTENT = {
    "housing_spike": {
        "headline": "Housing took the lead this month.",
        "subtext": "Rent and home expenses were your biggest chapter. That's expected — it keeps life running."
    },
    "food_spike": {
        "headline": "Food was your comfort zone this month.",
        "subtext": "Dining and delivery made up most of your spending. Some months are just like that."
    },
    "transport_spike": {
        "headline": "You were on the move this month.",
        "subtext": "Getting around cost more than usual. Busy months tend to do that."
    },
    "shopping_spike": {
        "headline": "A bit of a shopping month.",
        "subtext": "More went into lifestyle this month. Nothing wrong with treating yourself occasionally."
    },
    "balanced": {
        "headline": "A well-spread month, actually.",
        "subtext": "No single category dominated. Your spending was pretty balanced this time."
    },
    "low_spend": {
        "headline": "A quiet, contained month.",
        "subtext": "You kept things lean. That's a month worth noting."
    }
}

@router.get("/insight")
def get_expenses_insight(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        # Fetch transactions for the selected month using string matching
        month_prefix = f"{year}-{month:02d}"
        txns = db.query(Transaction).filter(
            Transaction.user_id == current_user.id,
            Transaction.date.like(f"{month_prefix}%")
        ).all()

        # Previous month for trend
        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1
        prev_prefix = f"{prev_year}-{prev_month:02d}"
        
        prev_txns = db.query(Transaction).filter(
            Transaction.user_id == current_user.id,
            Transaction.date.like(f"{prev_prefix}%")
        ).all()

        total_debit = sum(t.amount for t in txns if t.direction == "debit")
        prev_total_debit = sum(t.amount for t in prev_txns if t.direction == "debit")

        # Trend logic
        vs_last_month_percent = 0
        vs_last_month_direction = "flat"
        
        if prev_total_debit > 0:
            diff = total_debit - prev_total_debit
            percent = (diff / prev_total_debit) * 100
            vs_last_month_percent = abs(round(percent))
            if abs(percent) <= 5:
                vs_last_month_direction = "flat"
            else:
                vs_last_month_direction = "up" if diff > 0 else "down"
        elif total_debit > 0:
            vs_last_month_direction = "up"
            vs_last_month_percent = 100

        # Mood detection
        mood = "balanced"
        if not txns or total_debit == 0:
            mood = "empty"
        else:
            if total_debit < 5000:
                mood = "low_spend"
            else:
                cat_totals = {}
                for t in txns:
                    if t.direction == "debit":
                        cat = t.category or "Others"
                        cat_totals[cat] = cat_totals.get(cat, 0) + t.amount
                
                if cat_totals:
                    top_cat = max(cat_totals, key=cat_totals.get)
                    top_amt = cat_totals[top_cat]
                    if top_amt > (total_debit * 0.4):
                        cat_lower = top_cat.lower()
                        if "housing" in cat_lower or "rent" in cat_lower:
                            mood = "housing_spike"
                        elif any(k in cat_lower for k in ["food", "dining", "restaurant", "groceries"]):
                            mood = "food_spike"
                        elif any(k in cat_lower for k in ["transport", "fuel", "cab"]):
                            mood = "transport_spike"
                        elif any(k in cat_lower for k in ["shopping", "lifestyle", "clothing"]):
                            mood = "shopping_spike"

        content = INSIGHT_CONTENT.get(mood, INSIGHT_CONTENT["balanced"])
        if mood == "empty":
            content = {
                "headline": "A fresh chapter begins.",
                "subtext": "You haven't recorded any spending yet this month. A great time to start with intention."
            }

        return {
            "insight_mood": mood,
            "headline": content["headline"],
            "subtext": content["subtext"],
            "potential_breathing_room": round(total_debit * 0.1, 2),
            "vs_last_month_percent": vs_last_month_percent,
            "vs_last_month_direction": vs_last_month_direction
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "insight_mood": "balanced",
            "headline": "Gathering your patterns...",
            "subtext": f"One moment while I analyze your chapters. (Error: {str(e)})",
            "potential_breathing_room": 0,
            "vs_last_month_percent": 0,
            "vs_last_month_direction": "flat"
        }


