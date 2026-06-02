import os
import sys
from dotenv import load_dotenv

# Load database URL from backend/.env instead of hardcoding
load_dotenv("backend/.env")

if not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "postgresql://dekho:dekho_password@localhost:5432/dekho_pilot"

from backend.app.db.session import engine
from backend.app.db.base import Base

print("🐘 Connecting to Neon PostgreSQL...")
Base.metadata.create_all(bind=engine)
print("✅ All tables created successfully in Neon database!")
