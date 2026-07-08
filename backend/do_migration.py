import os
from dotenv import load_dotenv

# Load database URL from .env
load_dotenv(".env")

print(f"DATABASE_URL is: {os.getenv('DATABASE_URL')}")

from app.core.database import init_db

print("🐘 Connecting to Neon PostgreSQL and migrating data...")
try:
    init_db()
    print("✅ All tables created and data migrated successfully to Neon database!")
except Exception as e:
    print(f"❌ Migration failed: {e}")
    import traceback
    traceback.print_exc()
