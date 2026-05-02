import sys
import os

# Add the project root to sys.path to import app
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.transaction import Transaction

db = SessionLocal()
try:
    tx = db.query(Transaction).first()
    if tx:
        print(f"ID: {tx.id}, Date: {tx.date}, Amount: {tx.amount}, User: {tx.user_id}")
    else:
        print("No transactions found.")
finally:
    db.close()
