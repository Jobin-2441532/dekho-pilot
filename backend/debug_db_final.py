import sys
import os
from datetime import date

# Add the project root to sys.path to import app
sys.path.append(os.getcwd())

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.transaction import Transaction

print(f"DATABASE_URL: {settings.DATABASE_URL}")

db = SessionLocal()
try:
    user_id = 1
    # Check all transactions count
    total = db.query(Transaction).count()
    print(f"Total transactions in DB: {total}")
    
    # Check months again
    months = sorted(list(set([t.date[:7] for t in db.query(Transaction).all() if t.date])))
    print(f"Months in DB: {months}")

finally:
    db.close()
