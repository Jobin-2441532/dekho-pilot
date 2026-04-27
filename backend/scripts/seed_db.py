import sys
from pathlib import Path
import json
import csv

# Add project backend root to pythonpath
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.core.database import SessionLocal, Base, engine
from app.models import User, Transaction, SavingsGoal, Budget, Asset, Recommendation

def seed_db():
    print("Initializing Database Schema...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # 1. Profile -> User
        print("Seeding Users...")
        profile_path = Path(settings.DATA_DIR) / 'profiles' / 'user_profile.json'
        
        user_id = 1
        if profile_path.exists():
            with open(profile_path, 'r', encoding='utf-8') as f:
                profile = json.load(f)
                
            user = db.query(User).filter(User.email == profile.get('email', 'arjun@dekho.app')).first()
            if not user:
                user = User(
                    name=profile.get('name', 'Arjun Sharma'),
                    email=profile.get('email', 'arjun@dekho.app'),
                    income_range=profile.get('income_range', '5-10L'),
                    goal_type=",".join(profile.get('purposes', [])),
                    risk_comfort=profile.get('risk_comfort', 'Moderate'),
                    monthly_budget=float(profile.get('monthly_budget', 50000)),
                    financial_stage=profile.get('financial_stage', 'Early Career')
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            user_id = user.id
        else:
            print(f"Warning: {profile_path} not found. Skipping user seeding.")
            
        # 2. Transactions
        print("Seeding Transactions...")
        tx_path = Path(settings.DATA_DIR) / 'transactions' / 'transactions.csv'
        if tx_path.exists():
            db.query(Transaction).delete()
            with open(tx_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                transactions = []
                for row in reader:
                    transactions.append(Transaction(
                        user_id=user_id,
                        date=row['date'],
                        merchant=row['merchant'],
                        amount=float(row['amount']),
                        category=row['category'],
                        payment_mode=row.get('payment_mode', ''),
                        notes=row.get('notes', ''),
                        direction='debit' if float(row['amount']) < 0 else 'credit',
                        source_type='csv'
                    ))
                db.add_all(transactions)

        # 3. Savings Goals
        print("Seeding Goals...")
        goals_path = Path(settings.DATA_DIR) / 'goals' / 'savings_goals.json'
        if goals_path.exists():
            db.query(SavingsGoal).delete()
            with open(goals_path, 'r', encoding='utf-8') as f:
                goals = json.load(f)
                db.add_all([
                    SavingsGoal(
                        user_id=user_id,
                        name=g['name'],
                        target_amount=float(g['target_amount']),
                        current_amount=float(g['current_amount']),
                        deadline=g.get('deadline', ''),
                        status='active'
                    ) for g in goals
                ])

        # 4. Budgets
        print("Seeding Budgets...")
        budgets_path = Path(settings.DATA_DIR) / 'goals' / 'budgets.json'
        if budgets_path.exists():
            db.query(Budget).delete()
            with open(budgets_path, 'r', encoding='utf-8') as f:
                budgets = json.load(f)
                db.add_all([
                    Budget(
                        user_id=user_id,
                        category=b['category'],
                        monthly_limit=float(b['monthly_limit']),
                        month='2026-04'
                    ) for b in budgets
                ])
                
        # 5. Assets (Quick Win)
        print("Seeding Assets...")
        db.query(Asset).delete()
        db.add_all([
            Asset(user_id=user_id, name="HDFC Savings", type="Cash", value=45000),
            Asset(user_id=user_id, name="Axis Mutual Fund", type="Investment", value=120500),
            Asset(user_id=user_id, name="PF Account", type="Retirement", value=240000),
            Asset(user_id=user_id, name="Gold ETF", type="Investment", value=35000)
        ])
        
        # 6. Recommendations (Quick Win)
        print("Seeding Recommendations...")
        db.query(Recommendation).delete()
        db.add_all([
            Recommendation(
                user_id=user_id,
                title="Top up Emergency Fund",
                description="You have ₹45,000 in savings, which covers about 1.2 months of spending (₹35k/mo average).",
                cta="Set a top-up goal",
                tag="Safety first"
            ),
            Recommendation(
                user_id=user_id,
                title="Start a small SIP",
                description="Even ₹1,000/month in a diversified index fund builds wealth quietly over time.",
                cta="Learn about SIPs",
                tag="Wealth building"
            ),
            Recommendation(
                user_id=user_id,
                title="Review your subscriptions",
                description="You're spending ₹957/month on subscriptions. That's ₹11,484 a year.",
                cta="See subscriptions",
                tag="Quick saving"
            ),
            Recommendation(
                user_id=user_id,
                title="Track your rent-to-income ratio",
                description="Your rent is 24% of monthly income. Financial guides suggest keeping it under 30%.",
                cta="See full breakdown",
                tag="You're on track"
            )
        ])
                
        db.commit()
        print("Seeding complete.")
        
    except Exception as e:
        print(f"Error seeding DB: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
