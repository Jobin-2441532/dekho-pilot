import os
import sys
from dotenv import load_dotenv

# Force the environment variable to be the Neon URL
os.environ["DATABASE_URL"] = "postgresql://neondb_owner:npg_qi1nAyO9eIHx@ep-ancient-haze-aoiorosj-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

from backend.app.db.session import engine
from backend.app.db.base import Base

print("🐘 Connecting to Neon PostgreSQL...")
Base.metadata.create_all(bind=engine)
print("✅ All tables created successfully in Neon database!")
