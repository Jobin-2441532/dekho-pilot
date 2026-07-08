import json
import os
import sys

# Add backend dir to path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models import Transaction

def run_migration():
    manual_file = "manual_transactions.json"
    if not os.path.exists(manual_file):
        print("No manual transactions to migrate.")
        return

    with open(manual_file, "r") as f:
        data = json.load(f)

    if not data:
        print("manual_transactions.json is empty.")
        return

    db = SessionLocal()
    try:
        migrated_count = 0
        for tx in data:
            db_tx = Transaction(
                user_id=tx["user_id"],
                amount=tx["amount"],
                merchant=tx["merchant"],
                category=tx["category"],
                date=tx["date"],
                notes=tx["notes"],
                direction=tx.get("direction", "debit"),
                payment_mode=tx.get("payment_mode", "Cash"),
                source_type=tx.get("source_type", "Manual"),
                review_status="reviewed", # Mark as reviewed so it shows up immediately
                raw_sms="",
                confidence=1.0
            )
            db.add(db_tx)
            migrated_count += 1
            
        db.commit()
        print(f"Successfully migrated {migrated_count} manual transactions to the database.")
        
        # Rename the file so we don't migrate again
        os.rename(manual_file, "manual_transactions.json.migrated")
        print("Renamed file to manual_transactions.json.migrated")
        
    except Exception as e:
        db.rollback()
        print(f"Error during migration: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_migration()
