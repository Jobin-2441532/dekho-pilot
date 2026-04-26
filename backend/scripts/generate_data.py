"""
generate_data.py
────────────────
Generates synthetic (fictional) financial data for the Dekho prototype.
All data is invented — no real personal information is used.

Run from project root:
    python backend/scripts/generate_data.py
"""

import csv
import json
import os
import random
from datetime import date, timedelta

# ── Output directories ────────────────────────────────────────────────────
ROOT      = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
TX_DIR    = os.path.join(ROOT, 'transactions')
PROF_DIR  = os.path.join(ROOT, 'profiles')
GOAL_DIR  = os.path.join(ROOT, 'goals')

for d in [TX_DIR, PROF_DIR, GOAL_DIR]:
    os.makedirs(d, exist_ok=True)

# ── Date range: Nov 2025 – Apr 14 2026 ───────────────────────────────────
START_DATE = date(2025, 11, 1)
END_DATE   = date(2026, 4, 14)

random.seed(2026)  # reproducible

# ── Transaction pool ──────────────────────────────────────────────────────
MERCHANTS = {
    'Food': [
        ('Zomato', 280, 750),
        ('Swiggy', 220, 650),
        ('BigBasket', 1800, 4500),
        ('D-Mart', 1500, 4000),
        ('Blinkit', 350, 900),
        ('Local dhaba', 120, 380),
        ('Chai Point', 60, 150),
        ('Starbucks', 350, 650),
    ],
    'Travel': [
        ('Uber', 80, 450),
        ('Rapido', 50, 180),
        ('Hyderabad Metro', 30, 200),
        ('Ola', 90, 420),
        ('IndiGo Airlines', 2800, 8500),
        ('IRCTC', 450, 3500),
        ('OYO', 1200, 4000),
        ('MakeMyTrip', 3500, 12000),
    ],
    'Shopping': [
        ('Amazon', 299, 6000),
        ('Flipkart', 350, 4500),
        ('Myntra', 599, 3500),
        ('Ajio', 499, 2800),
        ('Nykaa', 350, 1800),
        ('Croma', 1500, 18000),
        ('H&M', 999, 4000),
    ],
    'Bills': [
        ('PhonePe BBPS', 500, 1500),
        ('TPCODL Electricity', 700, 2200),
        ('Airtel Broadband', 799, 1399),
        ('Jio Recharge', 349, 999),
        ('HMWSSB Water', 120, 400),
        ('Gas Agency', 900, 1100),
    ],
    'Entertainment': [
        ('BookMyShow', 320, 1200),
        ('PVR Cinemas', 400, 1500),
        ('SonyLIV', 299, 599),
        ('Hotstar', 299, 999),
    ],
    'Health': [
        ('Cult.fit Gym', 1999, 1999),
        ('PharmEasy', 200, 1800),
        ('Apollo Pharmacy', 300, 2200),
        ('Practo Consult', 500, 1500),
        ('HealthifyMe', 499, 999),
    ],
    'Subscriptions': [
        ('Netflix', 649, 649),
        ('Spotify', 119, 119),
        ('YouTube Premium', 189, 189),
        ('Notion Pro', 320, 320),
        ('Amazon Prime', 299, 299),
    ],
    'Rent': [
        ('House Rent', 18000, 18000),
    ],
}

PAYMENT_MODES = ['UPI', 'UPI', 'UPI', 'Card', 'Net Banking']  # weighted


def random_date_in_month(year: int, month: int) -> date:
    """Return a random date in the given month."""
    if month == 12:
        last_day = 31
    else:
        last_day = (date(year, month + 1, 1) - timedelta(days=1)).day
    return date(year, month, random.randint(1, last_day))


def generate_transactions():
    rows = []
    tx_id = 1

    # Month configs: (year, month, multiplier) — Dec higher for festive
    months = [
        (2025, 11, 1.0),
        (2025, 12, 1.35),   # festive season
        (2026,  1, 0.95),
        (2026,  2, 0.90),
        (2026,  3, 1.05),
        (2026,  4, 0.60),   # partial month (1-14)
    ]

    for year, month, mult in months:
        # Always add rent on the 1st
        rows.append({
            'id': f'TX{tx_id:04d}',
            'date': date(year, month, 1).isoformat(),
            'merchant': 'House Rent',
            'amount': 18000,
            'category': 'Rent',
            'payment_mode': 'Net Banking',
            'notes': 'Monthly rent',
        })
        tx_id += 1

        # Recurring subscriptions (first 5 days)
        for merchant, lo, hi in MERCHANTS['Subscriptions']:
            rows.append({
                'id': f'TX{tx_id:04d}',
                'date': random_date_in_month(year, month) if month != 4 else date(year, month, random.randint(1, 14)),
                'merchant': merchant,
                'amount': lo,
                'category': 'Subscriptions',
                'payment_mode': 'Card',
                'notes': 'Monthly subscription',
            })
            tx_id += 1

        # Health — gym monthly
        rows.append({
            'id': f'TX{tx_id:04d}',
            'date': date(year, month, random.randint(8, 12)).isoformat(),
            'merchant': 'Cult.fit Gym',
            'amount': 1999,
            'category': 'Health',
            'payment_mode': 'UPI',
            'notes': 'Monthly gym membership',
        })
        tx_id += 1

        # Bills (2-3 per month)
        for _ in range(random.randint(2, 3)):
            merchant, lo, hi = random.choice(MERCHANTS['Bills'])
            amt = round(random.uniform(lo, hi))
            rows.append({
                'id': f'TX{tx_id:04d}',
                'date': random_date_in_month(year, month),
                'merchant': merchant,
                'amount': amt,
                'category': 'Bills',
                'payment_mode': random.choice(PAYMENT_MODES),
                'notes': '',
            })
            tx_id += 1

        # Food — most frequent (8-12 per month, scaled by mult)
        n_food = round(random.randint(8, 12) * mult)
        if month == 4:
            n_food = round(n_food * 0.45)   # partial April
        for _ in range(n_food):
            merchant, lo, hi = random.choice(MERCHANTS['Food'][:-3])  # skip café for variety
            amt = round(random.uniform(lo, hi))
            day = random.randint(1, 14 if month == 4 else 28)
            rows.append({
                'id': f'TX{tx_id:04d}',
                'date': date(year, month, min(day, 28)).isoformat(),
                'merchant': merchant,
                'amount': amt,
                'category': 'Food',
                'payment_mode': 'UPI',
                'notes': '',
            })
            tx_id += 1

        # Travel (3-6 per month)
        n_travel = round(random.randint(3, 6) * mult)
        if month == 4:
            n_travel = 3
        for _ in range(n_travel):
            merchant, lo, hi = random.choice(MERCHANTS['Travel'][:4])  # mostly local
            amt = round(random.uniform(lo, hi))
            day = random.randint(1, 14 if month == 4 else 28)
            rows.append({
                'id': f'TX{tx_id:04d}',
                'date': date(year, month, min(day, 28)).isoformat(),
                'merchant': merchant,
                'amount': amt,
                'category': 'Travel',
                'payment_mode': 'UPI',
                'notes': '',
            })
            tx_id += 1

        # Shopping (2-5 per month, festive spike in Dec)
        n_shop = round(random.randint(2, 5) * mult)
        if month == 4:
            n_shop = 2
        for _ in range(n_shop):
            merchant, lo, hi = random.choice(MERCHANTS['Shopping'])
            amt = round(random.uniform(lo, hi))
            day = random.randint(1, 14 if month == 4 else 28)
            rows.append({
                'id': f'TX{tx_id:04d}',
                'date': date(year, month, min(day, 28)).isoformat(),
                'merchant': merchant,
                'amount': amt,
                'category': 'Shopping',
                'payment_mode': random.choice(['Card', 'UPI']),
                'notes': '',
            })
            tx_id += 1

        # Entertainment (1-3 per month)
        n_ent = random.randint(1, 3)
        if month == 4:
            n_ent = 1
        for _ in range(n_ent):
            merchant, lo, hi = random.choice(MERCHANTS['Entertainment'])
            amt = round(random.uniform(lo, hi))
            day = random.randint(1, 14 if month == 4 else 28)
            rows.append({
                'id': f'TX{tx_id:04d}',
                'date': date(year, month, min(day, 28)).isoformat(),
                'merchant': merchant,
                'amount': amt,
                'category': 'Entertainment',
                'payment_mode': 'Card',
                'notes': '',
            })
            tx_id += 1

        # Health (1-2 extra per month)
        for _ in range(random.randint(1, 2)):
            merchant, lo, hi = random.choice(MERCHANTS['Health'][1:])  # skip gym
            amt = round(random.uniform(lo, hi))
            day = random.randint(1, 14 if month == 4 else 28)
            rows.append({
                'id': f'TX{tx_id:04d}',
                'date': date(year, month, min(day, 28)).isoformat(),
                'merchant': merchant,
                'amount': amt,
                'category': 'Health',
                'payment_mode': 'UPI',
                'notes': '',
            })
            tx_id += 1

        # Big travel in Dec (Goa trip expense)
        if month == 12:
            for m, lo, hi in [('IndiGo Airlines', 4500, 6000), ('OYO', 3000, 5000)]:
                rows.append({
                    'id': f'TX{tx_id:04d}',
                    'date': date(year, month, random.randint(20, 28)).isoformat(),
                    'merchant': m,
                    'amount': round(random.uniform(lo, hi)),
                    'category': 'Travel',
                    'payment_mode': 'Card',
                    'notes': 'Goa trip',
                })
                tx_id += 1

    # Sort by date
    rows.sort(key=lambda r: str(r['date']))

    path = os.path.join(TX_DIR, 'transactions.csv')
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'date', 'merchant', 'amount', 'category', 'payment_mode', 'notes'])
        writer.writeheader()
        for row in rows:
            row['date'] = str(row['date'])   # ensure ISO string
        writer.writerows(rows)

    print(f'[OK] Wrote {len(rows)} transactions to {path}')
    return rows


def generate_income():
    rows = []
    months = [
        (2025, 11), (2025, 12),
        (2026,  1), (2026,  2), (2026,  3), (2026,  4),
    ]
    for i, (year, month) in enumerate(months):
        rows.append({
            'id': f'INC{i+1:03d}',
            'date': date(year, month, 1).isoformat(),
            'source': 'Employer — TechCorp Hyderabad',
            'amount': 75000,
            'type': 'salary',
            'notes': 'Monthly net salary',
        })
        # Occasional freelance income
        if random.random() > 0.6:
            rows.append({
                'id': f'INC{i+100:03d}',
                'date': date(year, month, random.randint(10, 25)).isoformat(),
                'source': 'Freelance — UI Design',
                'amount': round(random.uniform(5000, 15000)),
                'type': 'freelance',
                'notes': 'Contract project',
            })

    path = os.path.join(TX_DIR, 'income.csv')
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'date', 'source', 'amount', 'type', 'notes'])
        writer.writeheader()
        writer.writerows(rows)
    print(f'[OK] Wrote {len(rows)} income entries to {path}')


def generate_profile():
    profile = {
        'user_id': 'user_001',
        'name': 'Arjun Sharma',
        'city': 'Hyderabad',
        'age_group': '25-30',
        'income_range': '60k-1L',
        'monthly_income': 75000,
        'financial_stage': 'Early career',
        'purposes': ['Track spending', 'Build emergency fund', 'Save for a goal'],
        'monthly_budget': 45000,
        'risk_comfort': 'moderate',
        'rent': 18000,
        'note': 'SYNTHETIC DATA — fictional user for prototype demonstration only',
    }
    path = os.path.join(PROF_DIR, 'user_profile.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(profile, f, indent=2)
    print(f'[OK] Wrote user profile to {path}')


def generate_goals():
    goals = [
        {
            'id': 'g1',
            'name': 'Emergency Fund',
            'emoji': 'shield',
            'target_amount': 90000,
            'current_amount': 45000,
            'monthly_contribution': 5000,
            'deadline': '2026-09-30',
            'priority': 'high',
            'status': 'active',
            'notes': '3 months of expenses (rent + living costs)',
        },
        {
            'id': 'g2',
            'name': 'Goa Trip',
            'emoji': 'beach',
            'target_amount': 25000,
            'current_amount': 18000,
            'monthly_contribution': 3500,
            'deadline': '2026-06-15',
            'priority': 'medium',
            'status': 'active',
            'notes': 'Flight + hotel for 4 days',
        },
        {
            'id': 'g3',
            'name': 'New Laptop',
            'emoji': 'laptop',
            'target_amount': 80000,
            'current_amount': 12000,
            'monthly_contribution': 4000,
            'deadline': '2026-12-31',
            'priority': 'low',
            'status': 'active',
            'notes': 'MacBook Air or equivalent',
        },
    ]
    budgets = [
        {'category': 'Food',          'monthly_limit': 8000},
        {'category': 'Shopping',      'monthly_limit': 4000},
        {'category': 'Entertainment', 'monthly_limit': 2000},
        {'category': 'Travel',        'monthly_limit': 3000},
        {'category': 'Subscriptions', 'monthly_limit': 1500},
        {'category': 'Health',        'monthly_limit': 3000},
        {'category': 'Bills',         'monthly_limit': 5000},
    ]
    goals_path = os.path.join(GOAL_DIR, 'savings_goals.json')
    with open(goals_path, 'w', encoding='utf-8') as f:
        json.dump(goals, f, indent=2)
    budgets_path = os.path.join(GOAL_DIR, 'budgets.json')
    with open(budgets_path, 'w', encoding='utf-8') as f:
        json.dump(budgets, f, indent=2)
    print(f'[OK] Wrote goals to {goals_path}')
    print(f'[OK] Wrote budgets to {budgets_path}')


if __name__ == '__main__':
    print('\n=== Dekho — Synthetic Data Generator ===\n')
    generate_transactions()
    generate_income()
    generate_profile()
    generate_goals()
    print('\n[DONE] All data files generated.\n')
    print('REMINDER: All data is synthetic and fictional — for prototype use only.\n')
