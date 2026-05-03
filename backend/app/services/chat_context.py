"""
ChatContextService -- builds an enriched context string for the Gemini
chatbot by pulling from the FeatureService instead of raw DB queries.

This replaces the old inline extract_global_context() in chat.py.
"""
from __future__ import annotations

from datetime import date
from sqlalchemy.orm import Session

from app.services.feature_service import feature_service
from app.models import Transaction, SavingsGoal


def _check_data_completeness(db: Session, user_id: int) -> dict:
    """
    Counts available data for a user.
    Returns a dict with counts and a boolean 'is_sparse' flag.
    """
    transaction_count = db.query(Transaction).filter(
        Transaction.user_id == user_id
    ).count()

    goal_count = db.query(SavingsGoal).filter(
        SavingsGoal.user_id == user_id,
        SavingsGoal.status == 'active'
    ).count()

    # Sparse = fewer than 5 transactions (new user or very little data)
    is_sparse = transaction_count < 5

    return {
        'transaction_count': transaction_count,
        'goal_count': goal_count,
        'is_sparse': is_sparse,
    }


def build_chat_context(db: Session, user_id: int) -> str:
    """
    Returns a richly formatted context string for the chatbot system prompt.
    Pulls profile, monthly features, and goals from the FeatureService.
    Includes a data completeness check to prevent hallucination on sparse data.
    NOTE: Uses Rs instead of the rupee symbol to avoid Windows cp1252 encoding crashes.
          The AI prompt instructs Gemini to display rupees as Rs in responses.
    """
    today = date.today()
    current_month = today.strftime("%Y-%m")

    # --- Phase 5: Data completeness check ---
    try:
        completeness = _check_data_completeness(db, user_id)
    except Exception:
        completeness = {'transaction_count': 0, 'goal_count': 0, 'is_sparse': True}

    try:
        profile = feature_service.compute_user_profile(db, user_id, months=3)
    except Exception:
        profile = {}

    try:
        monthly = feature_service.compute_monthly_features(db, user_id, current_month)
    except Exception:
        monthly = {}

    ctx_lines = []

    # Inject sparse data warning FIRST so the AI reads it before any numbers
    if completeness['is_sparse']:
        ctx_lines.append("=== DATA WARNING ===")
        ctx_lines.append(
            f"This user has only {completeness['transaction_count']} transaction(s) on record. "
            "Financial data is limited. Do not make confident statements about spending patterns. "
            "Do not invent numbers or trends. If asked about spending history, say clearly that "
            "there is not enough data to give a reliable answer yet."
        )
        ctx_lines.append("")

    # --- User Overview ---
    ctx_lines.append("=== USER FINANCIAL PROFILE ===")
    ctx_lines.append(f"Lookback Period: {profile.get('lookback_months', 3)} months")
    ctx_lines.append(f"Avg Monthly Spend: Rs{profile.get('avg_monthly_spend', 0):,.0f}")
    ctx_lines.append(f"Avg Monthly Income (credit): Rs{profile.get('avg_monthly_credit', 0):,.0f}")
    ctx_lines.append(f"Avg Savings Rate: {profile.get('avg_savings_rate', 0) * 100:.1f}%")

    # --- Dominant Categories ---
    dominant = profile.get("dominant_categories", [])
    if dominant:
        ctx_lines.append("\nTop Spending Categories (3-month avg):")
        for cat in dominant:
            ctx_lines.append(
                f"  - {cat['category']}: Rs{cat['amount']:,.0f} ({cat['pct']:.1f}% of spend)"
            )

    # --- Recurring Merchants ---
    recurring = profile.get("recurring_merchants", [])
    if recurring:
        ctx_lines.append("\nRecurring Merchants:")
        for m in recurring[:5]:
            ctx_lines.append(
                f"  - {m['merchant']}: {m['count']}x @ avg Rs{m['avg_amount']:,.0f}"
            )

    # --- This Month's Snapshot ---
    ctx_lines.append(f"\n=== THIS MONTH ({current_month}) ===")
    ctx_lines.append(f"Total Spend: Rs{monthly.get('total_spend', 0):,.0f}")
    ctx_lines.append(f"Total Credit: Rs{monthly.get('total_credit', 0):,.0f}")
    ctx_lines.append(f"Savings Rate: {monthly.get('savings_rate', 0) * 100:.1f}%")
    ctx_lines.append(f"Transactions: {monthly.get('transaction_count', 0)}")

    top_cats = monthly.get("top_categories", [])
    if top_cats:
        ctx_lines.append("\nCategory Breakdown (This Month):")
        for cat in top_cats:
            ctx_lines.append(f"  - {cat['category']}: Rs{cat['amount']:,.0f}")

    # Budget utilization
    budget_util = monthly.get("budget_utilization", {})
    if budget_util:
        ctx_lines.append("\nBudget Utilization:")
        for cat, data in budget_util.items():
            status = "Over budget" if data["pct"] > 100 else "On track"
            ctx_lines.append(
                f"  - {cat}: Rs{data['spent']:,.0f} / Rs{data['budget']:,.0f} "
                f"({data['pct']:.0f}%) -- {status}"
            )

    # --- Goals ---
    goals = profile.get("goals_summary", [])
    if goals:
        ctx_lines.append("\n=== ACTIVE SAVINGS GOALS ===")
        for g in goals:
            ctx_lines.append(
                f"  - {g['name']}: Rs{g['current']:,.0f} / Rs{g['target']:,.0f} "
                f"({g['progress_pct']:.0f}%) -- Deadline: {g['deadline']}"
            )
    else:
        ctx_lines.append("\n=== ACTIVE SAVINGS GOALS ===")
        ctx_lines.append("  No active savings goals yet.")

    # --- Spending Trend ---
    trend = profile.get("spending_trend", [])
    if trend:
        ctx_lines.append("\nMonthly Spend Trend:")
        for t in trend:
            ctx_lines.append(f"  {t['month']}: Rs{t['total_spend']:,.0f}")

    return "\n".join(ctx_lines)
