from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv(r"c:\Dekho Pilot\backend\.env")
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.begin() as conn:
    conn.execute(text('UPDATE users SET monthly_budget = 0 WHERE monthly_budget = 50000'))
print('Database updated successfully')
