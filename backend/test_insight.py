from app.core.database import SessionLocal
from app.models import Transaction, User

db = SessionLocal()

# Simulate the insight endpoint for user 2 (the one with 20490 spend)
user_id = 2
month_prefix = "2026-05"

txns = db.query(Transaction).filter(
    Transaction.user_id == user_id,
    Transaction.date.like(f"{month_prefix}%")
).all()

print(f"Found {len(txns)} transactions for user {user_id} in {month_prefix}")
for t in txns:
    print(f"  {t.date} | {t.direction} | {t.category} | {t.amount}")

total_debit = sum(t.amount for t in txns if t.direction == "debit")
print(f"\nTotal debit: {total_debit}")

cat_totals = {}
for t in txns:
    if t.direction == "debit":
        cat = t.category or "Others"
        cat_totals[cat] = cat_totals.get(cat, 0) + t.amount

print(f"Category totals: {cat_totals}")

if cat_totals:
    top_cat = max(cat_totals, key=cat_totals.get)
    top_amt = cat_totals[top_cat]
    print(f"Top category: {top_cat} = {top_amt} ({top_amt/total_debit*100:.1f}%)")
    
    # Mood check
    mood = "balanced"
    if total_debit < 5000:
        mood = "low_spend"
    elif top_amt > (total_debit * 0.4):
        cat_lower = top_cat.lower()
        if "housing" in cat_lower or "rent" in cat_lower:
            mood = "housing_spike"
        elif any(k in cat_lower for k in ["food", "dining", "restaurant", "groceries"]):
            mood = "food_spike"
        elif any(k in cat_lower for k in ["transport", "fuel", "cab"]):
            mood = "transport_spike"
        elif any(k in cat_lower for k in ["shopping", "lifestyle", "clothing"]):
            mood = "shopping_spike"
    print(f"Mood: {mood}")

db.close()
