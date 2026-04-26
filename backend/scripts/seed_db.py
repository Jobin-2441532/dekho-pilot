import sqlite3
import json
import csv
import sys
from pathlib import Path
from dateutil import parser

# Add project backend root to pythonpath
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.core.database import init_db, get_db_connection

def seed_db():
    print("Initializing Database Schema...")
    init_db()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Profile -> User
    print("Seeding Users...")
    profile_path = Path(settings.DATA_DIR) / 'profiles' / 'user_profile.json'
    if profile_path.exists():
        with open(profile_path, 'r', encoding='utf-8') as f:
            profile = json.load(f)
            
        cursor.execute("SELECT id FROM users WHERE email = ?", (profile.get('email', 'arjun@dekho.app'),))
        user_row = cursor.fetchone()
        
        if not user_row:
            cursor.execute("""
                INSERT INTO users (name, email, income_range, goal_type, risk_comfort, monthly_budget, financial_stage)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                profile.get('name', 'Arjun Sharma'),
                profile.get('email', 'arjun@dekho.app'),
                profile.get('income_range', '5-10L'),
                ",".join(profile.get('purposes', [])),
                profile.get('risk_comfort', 'Moderate'),
                profile.get('monthly_budget', 50000),
                profile.get('financial_stage', 'Early Career')
            ))
            user_id = cursor.lastrowid
        else:
            user_id = user_row['id']
            
    else:
        print(f"Warning: {profile_path} not found. Skipping user seeding.")
        user_id = 1
        
    # 2. Transactions
    print("Seeding Transactions...")
    tx_path = Path(settings.DATA_DIR) / 'transactions' / 'transactions.csv'
    if tx_path.exists():
        cursor.execute("DELETE FROM transactions") # reset
        with open(tx_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cursor.execute("""
                    INSERT INTO transactions (user_id, date, merchant, amount, category, payment_mode, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    row['date'],
                    row['merchant'],
                    float(row['amount']),
                    row['category'],
                    row['payment_mode'],
                    row.get('notes', '')
                ))

    # 3. Savings Goals
    print("Seeding Goals...")
    goals_path = Path(settings.DATA_DIR) / 'goals' / 'savings_goals.json'
    if goals_path.exists():
        cursor.execute("DELETE FROM savings_goals") # reset
        with open(goals_path, 'r', encoding='utf-8') as f:
            goals = json.load(f)
            for g in goals:
                cursor.execute("""
                    INSERT INTO savings_goals (user_id, name, target_amount, current_amount, deadline, status)
                    VALUES (?, ?, ?, ?, ?, 'active')
                """, (
                    user_id,
                    g['name'],
                    float(g['target_amount']),
                    float(g['current_amount']),
                    g.get('deadline', '')
                ))

    # 4. Budgets
    print("Seeding Budgets...")
    budgets_path = Path(settings.DATA_DIR) / 'goals' / 'budgets.json'
    if budgets_path.exists():
        cursor.execute("DELETE FROM budgets") # reset
        with open(budgets_path, 'r', encoding='utf-8') as f:
            budgets = json.load(f)
            for b in budgets:
                cursor.execute("""
                    INSERT INTO budgets (user_id, category, monthly_limit, month)
                    VALUES (?, ?, ?, '2026-04')
                """, (
                    user_id,
                    b['category'],
                    float(b['monthly_limit'])
                ))
                
    conn.commit()
    conn.close()
    print("Seeding complete.")

if __name__ == "__main__":
    seed_db()
