"""
Response Package Builder — assembles chart data, quick replies, and proactive alerts
to accompany the LLM text response.
"""

from __future__ import annotations
import json
import logging
import re
from app.models.schemas import (
    UserFinancialContext, ChartData, AlertPayload,
    ChatResponse, SavingsGoal,
)
from app.services.prompt_engine import QUICK_REPLIES, should_include_chart, build_quick_replies_prompt
from app.services.intent_detector import IntentResult
from app.utils.formatters import fmt_inr

logger = logging.getLogger("dekho.response_builder")


# Phrases that indicate the LLM couldn't find the data — suppress chart in these cases
_NO_DATA_PHRASES = [
    "don't have that",
    "don't have that information",
    "no information",
    "try adding",
    "add some transactions",
    "i don't have",
    "not available",
    "no data",
    "couldn't find",
    "can't find",
    "no savings target",
    "no goal set",
    "haven't set",
    "no bike goal",
    "no specific goal",
    "don't see a",
    "you don't have a",
    "no matching goal",
]


def _is_chart_eligible(intent: str, llm_text: str) -> bool:
    """Return False if the LLM indicated it has no data, or intent is out of scope."""
    if intent in ("OUT_OF_SCOPE", "GENERAL_CHAT"):
        return False
    text_lower = llm_text.lower()
    return not any(phrase in text_lower for phrase in _NO_DATA_PHRASES)


# ── Chart Builders ─────────────────────────────────────────────────────────────

def build_pie_chart(ctx: UserFinancialContext) -> ChartData:
    """Spending by category — pie chart."""
    data = [
        {"name": cat, "value": round(amt, 2), "label": fmt_inr(amt)}
        for cat, amt in sorted(ctx.current_month.by_category.items(), key=lambda x: x[1], reverse=True)
        if amt > 0
    ]
    return ChartData(
        type="pie",
        title=f"Spending Breakdown — {ctx.current_month.month}",
        data=data,
        config={"colors": ["#F4A261", "#E76F51", "#52B788", "#5C3D2E", "#8D99AE", "#457B9D", "#A8DADC"]},
    )


def build_bar_chart(ctx: UserFinancialContext) -> ChartData:
    """Current vs last month total comparison using real database totals."""
    from datetime import datetime
    now = datetime.now()
    curr_month_name = now.strftime("%B")
    
    last_month_name = "Last Month"
    last_month_total = 0.0
    
    # Try to find the snapshot for 1 month ago
    # June is 2026-06, July is 2026-07
    curr_m_num = now.month
    curr_y_num = now.year
    last_m_num = curr_m_num - 1 if curr_m_num > 1 else 12
    last_y_num = curr_y_num if curr_m_num > 1 else curr_y_num - 1
    last_m_code = f"{last_y_num}-{str(last_m_num).zfill(2)}"
    
    for m in ctx.historical_months:
        if m.month == last_m_code:
            try:
                m_dt = datetime.strptime(m.month, "%Y-%m")
                last_month_name = m_dt.strftime("%B")
            except:
                last_month_name = m.month
            last_month_total = m.total_expenses
            break
    else:
        # Fallback to the first historical month that is not the current month
        curr_m_code = now.strftime("%Y-%m")
        other_months = [m for m in ctx.historical_months if m.month != curr_m_code]
        if other_months:
            try:
                m_dt = datetime.strptime(other_months[0].month, "%Y-%m")
                last_month_name = m_dt.strftime("%B")
            except:
                last_month_name = other_months[0].month
            last_month_total = other_months[0].total_expenses

    data = [
        {"name": last_month_name, "value": round(last_month_total, 2)},
        {"name": curr_month_name, "value": round(ctx.current_month.total_expenses, 2)}
    ]
    return ChartData(
        type="bar",
        title="Monthly Spending Comparison",
        data=data,
    )


def build_line_chart(ctx: UserFinancialContext) -> ChartData:
    """Monthly spend trend — bar chart comparing past months' real totals."""
    from datetime import datetime
    data = []
    
    # Loop through historical months in reverse (oldest first)
    for m in reversed(ctx.historical_months[:4]):
        try:
            m_dt = datetime.strptime(m.month, "%Y-%m")
            m_name = m_dt.strftime("%B")
        except:
            m_name = m.month
        data.append({
            "name": m_name,
            "value": round(m.total_expenses, 2)
        })
        
    curr_month_code = datetime.now().strftime("%Y-%m")
    if not any(m.month == curr_month_code for m in ctx.historical_months):
        curr_name = datetime.now().strftime("%B")
        data.append({
            "name": curr_name,
            "value": round(ctx.current_month.total_expenses, 2)
        })
        
    return ChartData(
        type="bar",
        title="Monthly Spending Trend",
        data=data,
    )


def build_goal_progress_chart(goal: SavingsGoal) -> ChartData:
    """Single goal progress — donut/progress chart."""
    return ChartData(
        type="progress",
        title=goal.goal_name,
        data=[{
            "name": goal.goal_name,
            "current": goal.current_amount,
            "target": goal.target_amount,
            "pct": goal.pct_complete,
            "remaining": goal.amount_remaining,
            "daysLeft": goal.days_left,
        }],
    )


# ── Proactive Alerts ───────────────────────────────────────────────────────────

def check_proactive_alerts(ctx: UserFinancialContext) -> AlertPayload | None:
    """
    Check if any proactive alerts should fire at session start.
    Returns the highest-priority alert, or None.
    """
    # Cashflow alert (> 90% of income spent)
    spend_ratio = ctx.current_month.total_expenses / max(ctx.current_month.total_income, 1)
    if spend_ratio > 0.90:
        return AlertPayload(
            type="CASHFLOW_ALERT",
            message=f"⚠️ You've spent {fmt_inr(ctx.current_month.total_expenses)} this month — "
                    f"that's {round(spend_ratio * 100, 1)}% of your income. "
                    f"Want tips to stay on track?",
            severity="critical",
        )

    # Goal urgent (< 7 days, < 90% complete)
    for goal in ctx.goals:
        if goal.days_left is not None and 0 < goal.days_left < 7 and goal.pct_complete < 90:
            return AlertPayload(
                type="GOAL_URGENT",
                message=f"⏰ Your '{goal.goal_name}' goal deadline is in {goal.days_left} day(s)! "
                        f"You're at {goal.pct_complete}% — {fmt_inr(goal.amount_remaining)} still to go.",
                severity="warning",
            )

    # Budget alert (any category > 80%)
    if ctx.budget_alerts:
        top = max(ctx.budget_alerts, key=lambda a: a.pct_used)
        return AlertPayload(
            type="BUDGET_ALERT",
            message=f"🔴 {top.category} is at {top.pct_used:.0f}% of your budget "
                    f"({fmt_inr(top.spent)} of {fmt_inr(top.limit)}). "
                    "Want some tips to cut back?",
            severity="warning",
        )

    # Anomaly alert
    if ctx.anomalies:
        a = ctx.anomalies[0]
        return AlertPayload(
            type="ANOMALY",
            message=f"🔍 Unusual spending in {a.category}: {fmt_inr(a.current_spend)} this month "
                    f"(typically around {fmt_inr(a.avg_3month)}). Everything okay?",
            severity="info",
        )

    return None


# ── Quick Reply Generator ─────────────────────────────────────────────────────

async def generate_quick_replies(llm_text: str, intent: str) -> list[str]:
    """
    Ask the LLM for 3 contextual follow-up suggestions based on the actual response.
    Falls back to static quick replies if LLM fails or returns invalid JSON.
    """
    from app.services.llm_client import LLMClient
    static_fallback = QUICK_REPLIES.get(intent, ["Show my summary", "Check my budget", "View my goals"])
    try:
        system_prompt, user_msg = build_quick_replies_prompt(llm_text, intent)
        client = LLMClient()
        raw = await client.generate(
            system_prompt=system_prompt,
            user_message=user_msg,
            max_tokens=120,
            temperature=0.4,
        )
        # Strip markdown fences if model adds them
        raw = re.sub(r"```(?:json)?", "", raw).strip()
        suggestions = json.loads(raw)
        if isinstance(suggestions, list) and len(suggestions) >= 2:
            return [str(s)[:60] for s in suggestions[:3]]
    except Exception as e:
        logger.debug("Quick reply generation failed, using static: %s", e)
    return static_fallback


# ── Main Assembler ─────────────────────────────────────────────────────────────

async def build_response_package(
    ctx: UserFinancialContext,
    intent_result: IntentResult,
    llm_text: str,
    is_session_start: bool = False,
) -> dict:
    """
    Assemble the full response package: text + chart + quick replies + alert.
    Returns a dict ready to serialize as ChatResponse.
    """
    # Chart — only if LLM actually has relevant data to show
    chart_type = should_include_chart(intent_result.intent, intent_result.slots)
    chart = None
    if chart_type and _is_chart_eligible(intent_result.intent, llm_text):
        if chart_type == "pie":
            chart = build_pie_chart(ctx)
        elif chart_type == "bar":
            chart = build_bar_chart(ctx)
        elif chart_type == "line":
            chart = build_line_chart(ctx)
        elif chart_type == "progress" and ctx.goals:
            goal_name = intent_result.slots.get("goal_name", "").lower()
            # Only show a goal chart if we can find a matching goal
            # Do NOT fall back to goals[0] — that causes irrelevant charts
            if goal_name:
                target_goal = next(
                    (g for g in ctx.goals if goal_name in g.goal_name.lower()),
                    None,
                )
            else:
                # No goal name specified — show first goal only if LLM confirmed it
                target_goal = ctx.goals[0] if ctx.goals else None
            if target_goal:
                chart = build_goal_progress_chart(target_goal)

    # Quick replies — LLM-generated for context-relevance, static fallback
    quick_replies = await generate_quick_replies(llm_text, intent_result.intent)

    # Proactive alert (only on session start)
    alert = check_proactive_alerts(ctx) if is_session_start else None

    return {
        "text": llm_text,
        "chart": chart,
        "quick_replies": quick_replies,
        "alert": alert,
        "intent": intent_result.intent,
        "is_fallback": False,
    }
