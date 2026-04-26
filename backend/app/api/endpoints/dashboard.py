from fastapi import APIRouter
from app.core.database import get_db_connection

router = APIRouter()

@router.get("/transactions")
def get_transactions():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, date, merchant, amount, category, payment_mode, notes FROM transactions ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": f"t{row['id']}",
            "date": row['date'],
            "merchant": row['merchant'],
            "amount": row['amount'],
            "category": row['category'],
            "paymentMode": row['payment_mode'],
            "notes": row['notes']
        }
        for row in rows
    ]

@router.get("/goals")
def get_goals():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, target_amount, current_amount, deadline FROM savings_goals")
    rows = cursor.fetchall()
    conn.close()
    
    # Assign some emojis based on standard strings for frontend mapping
    emoji_map = {"Emergency Fund": "🛡️", "Goa Trip": "🏖️", "New Laptop": "💻"}
    color_map = {"Emergency Fund": "#5C3D2E", "Goa Trip": "#2563EB", "New Laptop": "#7C3AED"}
    
    return [
        {
            "id": f"g{row['id']}",
            "name": row['name'],
            "emoji": emoji_map.get(row['name'], "🎯"),
            "targetAmount": row['target_amount'],
            "currentAmount": row['current_amount'],
            "deadline": row['deadline'],
            "color": color_map.get(row['name'], "#10B981")
        }
        for row in rows
    ]

@router.get("/profile")
def get_profile():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, email, income_range, monthly_budget, goal_type, financial_stage FROM users LIMIT 1")
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return {}
        
    return {
        "name": user['name'].split()[0],
        "fullName": user['name'],
        "incomeRange": user['income_range'],
        "monthlyIncome": 75000, # Hardcoded mapped mock for prototype
        "stage": user['financial_stage'],
        "purposes": user['goal_type'].split(','),
        "monthlyBudget": user['monthly_budget']
    }

@router.get("/summary")
def get_summary():
    """Aggregates all-time categories and basic insights based on current transactions"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT category, SUM(amount) as total FROM transactions GROUP BY category ORDER BY total DESC")
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {"category": row['category'], "total": row['total']}
        for row in rows
    ]

@router.get("/assets")
def get_assets():
    return [
        {"id": "a1", "name": "HDFC Savings", "type": "Cash", "balance": 45000, "change": 2.1},
        {"id": "a2", "name": "Axis Mutual Fund", "type": "Investment", "balance": 120500, "change": 8.4},
        {"id": "a3", "name": "PF Account", "type": "Retirement", "balance": 240000, "change": 7.1},
        {"id": "a4", "name": "Gold ETF", "type": "Investment", "balance": 35000, "change": -1.2}
    ]

@router.get("/opportunities")
def get_opportunities():
    return [
  {
    "id": "op1",
    "emoji": "🛡️",
    "title": "Top up Emergency Fund",
    "description": "You have ₹45,000 in savings, which covers about 1.2 months of spending (₹35k/mo average).",
    "why": "Financial safety nets usually aim for 3-6 months coverage to be truly protective.",
    "cta": "Set a top-up goal",
    "tag": "Safety first",
    "tagColor": "positive"
  },
  {
    "id": "op2",
    "emoji": "📈",
    "title": "Start a small SIP",
    "description": "Even ₹1,000/month in a diversified index fund builds wealth quietly over time.",
    "why": "Your spending suggests ₹1,000–2,000 room for savings after rent and bills.",
    "cta": "Learn about SIPs",
    "tag": "Wealth building",
    "tagColor": "filter"
  },
  {
    "id": "op3",
    "emoji": "💳",
    "title": "Review your subscriptions",
    "description": "You're spending ₹957/month on subscriptions. That's ₹11,484 a year.",
    "why": "Netflix + Spotify + YouTube — are you using all three regularly?",
    "cta": "See subscriptions",
    "tag": "Quick saving",
    "tagColor": "warning"
  },
  {
    "id": "op4",
    "emoji": "🏠",
    "title": "Track your rent-to-income ratio",
    "description": "Your rent is 24% of monthly income. Financial guides suggest keeping it under 30%.",
    "why": "You're within the healthy range — this gives room for other goals.",
    "cta": "See full breakdown",
    "tag": "You're on track",
    "tagColor": "positive"
  }
]
