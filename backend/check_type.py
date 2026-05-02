from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    res = db.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'transactions' AND column_name = 'date'")).fetchone()
    print(f"COL TYPE: {res}")
except Exception as e:
    print(f"ERROR: {e}")
finally:
    db.close()
