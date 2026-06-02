import os
from dotenv import load_dotenv
import psycopg2

# Load environment variables
load_dotenv()

db_url = os.getenv("DATABASE_URL")
if not db_url:
    print("Error: DATABASE_URL not set in environment.")
    exit(1)

print(f"Connecting to database to clear tables: {db_url}")

try:
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cur = conn.cursor()
    
    # Drop all tables in cascade mode
    drop_query = """
    DROP TABLE IF EXISTS 
        chat_sessions, 
        recommendations, 
        feedback_logs, 
        merchant_mappings, 
        uploaded_files, 
        raw_records, 
        split_groups, 
        recurring_expenses, 
        wallet_floats, 
        social_contacts, 
        user_salary_profiles, 
        savings_goals, 
        budgets, 
        income_entries, 
        assets, 
        transactions, 
        users, 
        alembic_version 
    CASCADE;
    """
    
    cur.execute(drop_query)
    print("Success: All existing tables and constraints dropped successfully!")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error clearing database: {e}")
    exit(1)
