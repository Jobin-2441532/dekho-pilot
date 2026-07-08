import os
from dotenv import load_dotenv

load_dotenv(".env")

from app.core.database import SessionLocal
from sqlalchemy import text
from app.core.database import get_all_models

print("🐘 Connecting to Neon PostgreSQL to fix sequences...")
try:
    db = SessionLocal()
    
    # Check if this is actually PostgreSQL
    if not os.getenv("DATABASE_URL", "").startswith("sqlite"):
        for model in get_all_models():
            table_name = model.__tablename__
            
            # Reset sequence using postgres specific commands
            # Using coalesce(max(id), 1) + 1 if we just used standard setval, 
            # but Postgres setval with max(id) and true is safer
            query = f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), coalesce(max(id), 1), max(id) IS NOT null) FROM {table_name};"
            try:
                db.execute(text(query))
                print(f"Fixed sequence for {table_name}")
            except Exception as e:
                # Some tables might not have an auto-incrementing id sequence or id column
                print(f"Could not fix sequence for {table_name} (might be normal): {e}")
                db.rollback()
        
        db.commit()
        print("✅ Sequences updated successfully!")
    else:
        print("Not PostgreSQL, skipping sequence fix.")
        
finally:
    db.close()
