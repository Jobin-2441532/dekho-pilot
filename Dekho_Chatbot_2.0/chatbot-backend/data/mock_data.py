"""
Mock Data Layer — realistic Indian user scenarios for chatbot dev & testing.
Switch between mock and real DB via USE_MOCK_DATA env flag.
"""

from __future__ import annotations
from datetime import date, timedelta
from app.models.schemas import (
    UserProfile, Transaction, BudgetEntry, SavingsGoal,
    MonthlySnapshot, UserFinancialContext, BudgetAlert, Anomaly,
)

# ─────────────────────────────────────────────────────────────────────────────
# Mock Users
# ─────────────────────────────────────────────────────────────────────────────

MOCK_USERS: dict[str, UserProfile] = {
    "user_priya": UserProfile(
        id="user_priya",
        name="Priya",
        monthly_income=60000,
        currency="INR",
        primary_goal="save",
        tone_preference="friendly",
    ),
    "user_arjun": UserProfile(
        id="user_arjun",
        name="Arjun",
        monthly_income=45000,
        currency="INR",
        primary_goal="budget",
        tone_preference="casual",
    ),
    "user_meera": UserProfile(
        id="user_meera",
        name="Meera",
        monthly_income=15000,
        currency="INR",
        primary_goal="debt_free",
        tone_preference="formal",
    ),
}

# ─────────────────────────────────────────────────────────────────────────────
# Mock Transactions (current month)
# ─────────────────────────────────────────────────────────────────────────────

today = date.today()

MOCK_TRANSACTIONS: dict[str, list[Transaction]] = {
    "user_priya": [
        Transaction(id="t1", user_id="user_priya", amount=18000, type="income", category="Income", subcategory="Salary", description="June Salary", date=today.replace(day=1), is_recurring=True),
        Transaction(id="t2", user_id="user_priya", amount=42000, type="income", category="Income", subcategory="Salary", description="June Salary (remaining)", date=today.replace(day=1), is_recurring=True),
        Transaction(id="t3", user_id="user_priya", amount=1200, type="expense", category="Food & Dining", subcategory="Food Delivery", description="Zomato", date=today - timedelta(days=1)),
        Transaction(id="t4", user_id="user_priya", amount=850,  type="expense", category="Food & Dining", subcategory="Food Delivery", description="Swiggy", date=today - timedelta(days=2)),
        Transaction(id="t5", user_id="user_priya", amount=3200, type="expense", category="Food & Dining", subcategory="Restaurants", description="Dinner with friends", date=today - timedelta(days=4)),
        Transaction(id="t6", user_id="user_priya", amount=450,  type="expense", category="Transport",    subcategory="Cab",           description="Uber to office", date=today - timedelta(days=1)),
        Transaction(id="t7", user_id="user_priya", amount=320,  type="expense", category="Transport",    subcategory="Cab",           description="Ola",           date=today - timedelta(days=3)),
        Transaction(id="t8", user_id="user_priya", amount=6500, type="expense", category="Shopping",     subcategory="Clothing",      description="Myntra haul",   date=today - timedelta(days=5)),
        Transaction(id="t9", user_id="user_priya", amount=799,  type="expense", category="Entertainment", subcategory="Streaming",    description="Netflix",       date=today - timedelta(days=7), is_recurring=True),
        Transaction(id="t10",user_id="user_priya", amount=12000,type="expense", category="Housing",      subcategory="Rent",          description="June Rent",     date=today.replace(day=1), is_recurring=True),
        Transaction(id="t11",user_id="user_priya", amount=1800, type="expense", category="Groceries",    subcategory="Supermarket",   description="DMart groceries",date=today - timedelta(days=6)),
        Transaction(id="t12",user_id="user_priya", amount=399,  type="expense", category="Telecom",      subcategory="Mobile",        description="Jio recharge",  date=today - timedelta(days=8), is_recurring=True),
    ],
    "user_arjun": [
        Transaction(id="a1", user_id="user_arjun", amount=45000, type="income", category="Income", subcategory="Freelance", description="Client payment", date=today.replace(day=5)),
        Transaction(id="a2", user_id="user_arjun", amount=600,   type="expense", category="Food & Dining", subcategory="Restaurants", description="Lunch", date=today - timedelta(days=1)),
        Transaction(id="a3", user_id="user_arjun", amount=150,   type="expense", category="Transport",    subcategory="Metro",      description="Metro card", date=today - timedelta(days=2)),
        Transaction(id="a4", user_id="user_arjun", amount=5000,  type="expense", category="Loan EMI",     subcategory="General",    description="Personal loan EMI", date=today.replace(day=5), is_recurring=True),
        Transaction(id="a5", user_id="user_arjun", amount=8000,  type="expense", category="Housing",      subcategory="Rent",       description="Rent",          date=today.replace(day=1), is_recurring=True),
        Transaction(id="a6", user_id="user_arjun", amount=2200,  type="expense", category="Groceries",   subcategory="Online Grocery", description="BigBasket", date=today - timedelta(days=4)),
        Transaction(id="a7", user_id="user_arjun", amount=3800,  type="expense", category="Shopping",    subcategory="Online",     description="Amazon gadget", date=today - timedelta(days=6)),
    ],
    "user_meera": [
        Transaction(id="m1", user_id="user_meera", amount=15000, type="income", category="Income", subcategory="Stipend", description="Monthly stipend", date=today.replace(day=1)),
        Transaction(id="m2", user_id="user_meera", amount=500,   type="expense", category="Food & Dining", subcategory="Cafe",  description="Starbucks",     date=today - timedelta(days=1)),
        Transaction(id="m3", user_id="user_meera", amount=300,   type="expense", category="Transport",    subcategory="Bus",   description="Bus pass",      date=today - timedelta(days=2)),
        Transaction(id="m4", user_id="user_meera", amount=4000,  type="expense", category="Housing",      subcategory="PG",    description="PG rent",       date=today.replace(day=1), is_recurring=True),
        Transaction(id="m5", user_id="user_meera", amount=800,   type="expense", category="Education",    subcategory="Books", description="Reference books",date=today - timedelta(days=3)),
        Transaction(id="m6", user_id="user_meera", amount=1200,  type="expense", category="Groceries",   subcategory="Supermarket", description="Provision store", date=today - timedelta(days=5)),
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
# Mock Monthly Snapshots
# ─────────────────────────────────────────────────────────────────────────────

MOCK_SNAPSHOTS: dict[str, MonthlySnapshot] = {
    "user_priya": MonthlySnapshot(
        user_id="user_priya",
        month=today.strftime("%Y-%m"),
        total_income=60000,
        total_expenses=27519,
        by_category={
            "Food & Dining": 5250,
            "Housing": 12000,
            "Transport": 770,
            "Shopping": 6500,
            "Entertainment": 799,
            "Groceries": 1800,
            "Telecom": 399,
        },
    ),
    "user_arjun": MonthlySnapshot(
        user_id="user_arjun",
        month=today.strftime("%Y-%m"),
        total_income=45000,
        total_expenses=19750,
        by_category={
            "Food & Dining": 600,
            "Housing": 8000,
            "Transport": 150,
            "Shopping": 3800,
            "Loan EMI": 5000,
            "Groceries": 2200,
        },
    ),
    "user_meera": MonthlySnapshot(
        user_id="user_meera",
        month=today.strftime("%Y-%m"),
        total_income=15000,
        total_expenses=6800,
        by_category={
            "Food & Dining": 500,
            "Housing": 4000,
            "Transport": 300,
            "Education": 800,
            "Groceries": 1200,
        },
    ),
}

# ─────────────────────────────────────────────────────────────────────────────
# Mock Budgets
# ─────────────────────────────────────────────────────────────────────────────

MOCK_BUDGETS: dict[str, list[BudgetEntry]] = {
    "user_priya": [
        BudgetEntry(category="Food & Dining", monthly_limit=5000,  spent=5250,  pct_used=105),  # OVER!
        BudgetEntry(category="Transport",     monthly_limit=2000,  spent=770,   pct_used=38.5),
        BudgetEntry(category="Shopping",      monthly_limit=5000,  spent=6500,  pct_used=130),  # OVER!
        BudgetEntry(category="Entertainment", monthly_limit=1000,  spent=799,   pct_used=79.9), # WARNING
        BudgetEntry(category="Groceries",     monthly_limit=3000,  spent=1800,  pct_used=60),
    ],
    "user_arjun": [
        BudgetEntry(category="Food & Dining", monthly_limit=3000, spent=600,   pct_used=20),
        BudgetEntry(category="Shopping",      monthly_limit=2000, spent=3800,  pct_used=190),   # OVER!
        BudgetEntry(category="Groceries",     monthly_limit=2500, spent=2200,  pct_used=88),    # WARNING
    ],
    "user_meera": [
        BudgetEntry(category="Food & Dining", monthly_limit=800,  spent=500,   pct_used=62.5),
        BudgetEntry(category="Transport",     monthly_limit=500,  spent=300,   pct_used=60),
        BudgetEntry(category="Education",     monthly_limit=1500, spent=800,   pct_used=53.3),
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
# Mock Savings Goals
# ─────────────────────────────────────────────────────────────────────────────

MOCK_GOALS: dict[str, list[SavingsGoal]] = {
    "user_priya": [
        SavingsGoal(id="g1", goal_name="Goa Trip ✈️",       target_amount=25000, current_amount=16200, deadline=today + timedelta(days=45), category="vacation"),
        SavingsGoal(id="g2", goal_name="Emergency Fund 🏦",  target_amount=60000, current_amount=22000, deadline=None,                       category="emergency"),
    ],
    "user_arjun": [
        SavingsGoal(id="g3", goal_name="Emergency Fund 🏦",  target_amount=50000, current_amount=8000,  deadline=today + timedelta(days=180), category="emergency"),
        SavingsGoal(id="g4", goal_name="Laptop Upgrade 💻",  target_amount=80000, current_amount=35000, deadline=today + timedelta(days=90),  category="gadget"),
    ],
    "user_meera": [
        SavingsGoal(id="g5", goal_name="Exam Fees 📚",       target_amount=8000,  current_amount=3200,  deadline=today + timedelta(days=20),  category="education"),
    ],
}


# ─────────────────────────────────────────────────────────────────────────────
# Context Assembler (used by ContextBuilder in mock mode)
# ─────────────────────────────────────────────────────────────────────────────

def build_mock_context(user_id: str) -> UserFinancialContext:
    """Assemble a complete UserFinancialContext from mock data."""
    user = MOCK_USERS.get(user_id)
    if user is None:
        # Default to Priya for unknown test users
        user_id = "user_priya"
        user = MOCK_USERS["user_priya"]

    transactions = MOCK_TRANSACTIONS.get(user_id, [])
    snapshot = MOCK_SNAPSHOTS.get(user_id, MonthlySnapshot(
        user_id=user_id, month=today.strftime("%Y-%m"),
        total_income=0, total_expenses=0, by_category={}
    ))
    budgets = MOCK_BUDGETS.get(user_id, [])
    goals = MOCK_GOALS.get(user_id, [])

    # Budget alerts (> 80%)
    budget_alerts = [
        BudgetAlert(
            category=b.category,
            limit=b.monthly_limit,
            spent=b.spent,
            pct_used=b.pct_used,
        )
        for b in budgets if b.pct_used >= 80
    ]

    # Top 5 expenses
    expenses = sorted(
        [t for t in transactions if t.type == "expense"],
        key=lambda t: t.amount,
        reverse=True,
    )[:5]

    # Recent transactions (last 7 days, max 10)
    recent = sorted(
        [t for t in transactions if (today - t.date).days <= 7],
        key=lambda t: t.date,
        reverse=True,
    )[:10]

    # Anomalies (mock: Shopping > 150% of a ₹3000 assumed avg)
    anomalies: list[Anomaly] = []
    avg_baselines = {"Shopping": 3000, "Food & Dining": 3500}
    for cat, avg in avg_baselines.items():
        actual = snapshot.by_category.get(cat, 0)
        if actual > avg * 1.2:
            anomalies.append(Anomaly(
                category=cat,
                current_spend=actual,
                avg_3month=avg,
                pct_over_avg=round((actual / avg - 1) * 100, 1),
            ))

    return UserFinancialContext(
        user=user,
        current_month=snapshot,
        budget_status=budgets,
        budget_alerts=budget_alerts,
        goals=goals,
        top_expenses=expenses,
        recent_transactions=recent,
        anomalies=anomalies,
    )
