"""
ChatContextService — builds an enriched context string for the Gemini
chatbot by pulling from the FeatureService instead of raw DB queries.

This replaces the old inline extract_global_context() in chat.py.
"""
from __future__ import annotations

from datetime import date
from sqlalchemy.orm import Session

from app.services.feature_service import feature_service


def build_chat_context(db: Session, user_id: int) -> str:
    """
    Returns a richly formatted context string for the chatbot system prompt.
    Pulls profile, monthly features, and goals from the FeatureService.
    """
    today = date.today()
    current_month = today.strftime("%Y-%m")

    try:
        profile = feature_service.compute_user_profile(db, user_id, months=3)
    except Exception as e:
        profile = {}

    try:
        monthly = feature_service.compute_monthly_features(db, user_id, current_month)
    except Exception as e:
        monthly = {}

    ctx_lines = []

    # --- User Overview ---
    ctx_lines.append("=== USER FINANCIAL PROFILE ===")
    ctx_lines.append(f"Lookback Period: {profile.get('lookback_months', 3)} months")
    ctx_lines.append(f"Avg Monthly Spend: ₹{profile.get('avg_monthly_spend', 0):,.0f}")
    ctx_lines.append(f"Avg Monthly Income (credit): ₹{profile.get('avg_monthly_credit', 0):,.0f}")
    ctx_lines.append(f"Avg Savings Rate: {profile.get('avg_savings_rate', 0) * 100:.1f}%")

    # --- Dominant Categories ---
    dominant = profile.get("dominant_categories", [])
    if dominant:
        ctx_lines.append("\nTop Spending Categories (3-month avg):")
        for cat in dominant:
            ctx_lines.append(
                f"  • {cat['category']}: ₹{cat['amount']:,.0f} ({cat['pct']:.1f}% of spend)"
            )

    # --- Recurring Merchants ---
    recurring = profile.get("recurring_merchants", [])
    if recurring:
        ctx_lines.append("\nRecurring Merchants:")
        for m in recurring[:5]:
            ctx_lines.append(
                f"  • {m['merchant']}: {m['count']}x @ avg ₹{m['avg_amount']:,.0f}"
            )

    # --- This Month's Snapshot ---
    ctx_lines.append(f"\n=== THIS MONTH ({current_month}) ===")
    ctx_lines.append(f"Total Spend: ₹{monthly.get('total_spend', 0):,.0f}")
    ctx_lines.append(f"Total Credit: ₹{monthly.get('total_credit', 0):,.0f}")
    ctx_lines.append(f"Savings Rate: {monthly.get('savings_rate', 0) * 100:.1f}%")
    ctx_lines.append(f"Transactions: {monthly.get('transaction_count', 0)}")

    top_cats = monthly.get("top_categories", [])
    if top_cats:
        ctx_lines.append("\nCategory Breakdown (This Month):")
        for cat in top_cats:
            ctx_lines.append(f"  • {cat['category']}: ₹{cat['amount']:,.0f}")

    # Budget utilization
    budget_util = monthly.get("budget_utilization", {})
    if budget_util:
        ctx_lines.append("\nBudget Utilization:")
        for cat, data in budget_util.items():
            status = "⚠️ Over" if data["pct"] > 100 else "✅ OK"
            ctx_lines.append(
                f"  • {cat}: ₹{data['spent']:,.0f} / ₹{data['budget']:,.0f} "
                f"({data['pct']:.0f}%) {status}"
            )

    # --- Goals ---
    goals = profile.get("goals_summary", [])
    if goals:
        ctx_lines.append("\n=== ACTIVE SAVINGS GOALS ===")
        for g in goals:
            ctx_lines.append(
                f"  • {g['name']}: ₹{g['current']:,.0f} / ₹{g['target']:,.0f} "
                f"({g['progress_pct']:.0f}%) — Deadline: {g['deadline']}"
            )

    # --- Spending Trend ---
    trend = profile.get("spending_trend", [])
    if trend:
        ctx_lines.append("\nMonthly Spend Trend:")
        for t in trend:
            ctx_lines.append(f"  {t['month']}: ₹{t['total_spend']:,.0f}")

    return "\n".join(ctx_lines)
