import sys
import os
from datetime import date

# Add the project root to sys.path to import app
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.transaction import Transaction

db = SessionLocal()
try:
    user_id = 1
    year, month = 2026, 6
    start_date = date(year, month, 1).isoformat()
    if month == 12:
        end_date = date(year + 1, 1, 1).isoformat()
    else:
        end_date = date(year, month + 1, 1).isoformat()

    print(f"Querying for User {user_id}, Date range: {start_date} to {end_date}")
    
    txns = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.date >= start_date,
        Transaction.date < end_date
    ).all()
    
    print(f"Found {len(txns)} transactions.")
    for t in txns[:3]:
        print(f"  TX: {t.id}, Date: {t.date}, Amount: {t.amount}, Direction: {t.direction}")

    # Check previous month
    prev_year, prev_month = 2026, 5
    prev_start = date(prev_year, prev_month, 1).isoformat()
    prev_end = start_date
    
    prev_txns = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.date >= prev_start,
        Transaction.date < prev_end
    ).all()
    print(f"Found {len(prev_txns)} transactions for May.")

finally:
    db.close()
