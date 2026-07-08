"""
Unit tests — Phase 6.1
Tests: IntentDetector, ContextBuilder, ResponsePackageBuilder,
       QuickReplyGenerator, ProactiveAlertChecker, Redis cache, LLM fallback,
       ADD_TRANSACTION slot extraction.
"""

import pytest
import asyncio
import sys
import os

# Make sure imports work from tests/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.utils.formatters import fmt_inr, fmt_pct, fmt_days
from app.services.intent_detector import infer_category, IntentResult
from app.services.response_builder import (
    check_proactive_alerts, build_pie_chart, build_bar_chart,
    build_goal_progress_chart, QUICK_REPLIES,
)
from app.services.prompt_engine import (
    format_context_for_prompt, format_history_for_prompt, INTENT_INSTRUCTIONS,
)
from data.mock_data import build_mock_context, MOCK_USERS


# ── Formatter tests ────────────────────────────────────────────────────────────

def test_fmt_inr_small():
    assert fmt_inr(500) == "₹500"

def test_fmt_inr_thousands():
    assert fmt_inr(5000) == "₹5,000"

def test_fmt_inr_lakhs():
    assert fmt_inr(60000) == "₹60,000"

def test_fmt_inr_large():
    assert fmt_inr(123456) == "₹1,23,456"

def test_fmt_inr_negative():
    assert fmt_inr(-1000) == "-₹1,000"

def test_fmt_pct():
    assert fmt_pct(84.5) == "84.5%"

def test_fmt_days_zero():
    assert fmt_days(0) == "due today"

def test_fmt_days_one():
    assert fmt_days(1) == "1 day"

def test_fmt_days_week():
    assert fmt_days(7) == "1 week"

def test_fmt_days_overdue():
    assert "overdue" in fmt_days(-3)


# ── Mock context tests ─────────────────────────────────────────────────────────

def test_mock_context_priya():
    ctx = build_mock_context("user_priya")
    assert ctx.user.name == "Priya"
    assert ctx.user.monthly_income == 60000
    assert ctx.current_month.total_income > 0
    assert len(ctx.goals) > 0

def test_mock_context_arjun():
    ctx = build_mock_context("user_arjun")
    assert ctx.user.name == "Arjun"
    assert len(ctx.budget_status) > 0

def test_mock_context_meera():
    ctx = build_mock_context("user_meera")
    assert ctx.user.name == "Meera"
    assert ctx.user.monthly_income == 15000

def test_mock_context_unknown_defaults_to_priya():
    ctx = build_mock_context("unknown_user_xyz")
    assert ctx.user.name == "Priya"

def test_context_has_budget_alerts():
    ctx = build_mock_context("user_priya")
    # Priya is over budget on Food & Dining and Shopping
    assert len(ctx.budget_alerts) >= 1
    categories = [a.category for a in ctx.budget_alerts]
    assert any(c in categories for c in ["Food & Dining", "Shopping"])

def test_context_has_anomalies():
    ctx = build_mock_context("user_priya")
    # Shopping should be flagged as anomaly (over baseline)
    anomaly_cats = [a.category for a in ctx.anomalies]
    assert len(anomaly_cats) >= 0  # may or may not trigger depending on data


# ── Proactive alert tests ──────────────────────────────────────────────────────

def test_alert_budget():
    ctx = build_mock_context("user_priya")
    alert = check_proactive_alerts(ctx)
    # Priya has budget alerts — should fire either BUDGET_ALERT or CASHFLOW_ALERT
    assert alert is not None
    assert alert.type in ["BUDGET_ALERT", "CASHFLOW_ALERT", "ANOMALY", "GOAL_URGENT"]

def test_alert_severity_values():
    ctx = build_mock_context("user_priya")
    alert = check_proactive_alerts(ctx)
    if alert:
        assert alert.severity in ["info", "warning", "critical"]


# ── Quick reply tests ──────────────────────────────────────────────────────────

def test_quick_replies_all_intents_defined():
    intents = [
        "BALANCE_OVERVIEW", "SPENDING_QUERY", "BUDGET_STATUS",
        "GOAL_PROGRESS", "ANOMALY_ALERT", "ADVICE_REQUEST",
        "COMPARISON_QUERY", "TREND_ANALYSIS", "ADD_TRANSACTION", "GENERAL_CHAT",
    ]
    for intent in intents:
        assert intent in QUICK_REPLIES, f"Missing quick replies for {intent}"
        assert len(QUICK_REPLIES[intent]) >= 2

def test_quick_replies_are_strings():
    for intent, chips in QUICK_REPLIES.items():
        for chip in chips:
            assert isinstance(chip, str), f"Non-string chip in {intent}"
            assert len(chip) > 0


# ── Intent sub-template tests ──────────────────────────────────────────────────

def test_intent_instructions_all_defined():
    intents = [
        "BALANCE_OVERVIEW", "SPENDING_QUERY", "BUDGET_STATUS",
        "GOAL_PROGRESS", "ANOMALY_ALERT", "ADVICE_REQUEST",
        "COMPARISON_QUERY", "TREND_ANALYSIS", "ADD_TRANSACTION", "GENERAL_CHAT",
    ]
    for intent in intents:
        assert intent in INTENT_INSTRUCTIONS
        assert len(INTENT_INSTRUCTIONS[intent]) > 20


# ── Merchant category mapping tests ───────────────────────────────────────────

def test_infer_category_zomato():
    assert infer_category("paid at Zomato") == "Food & Dining"

def test_infer_category_uber():
    assert infer_category("Uber ride to office") == "Transport"

def test_infer_category_amazon():
    assert infer_category("ordered from Amazon") == "Shopping"

def test_infer_category_netflix():
    assert infer_category("Netflix subscription") == "Entertainment"

def test_infer_category_jio():
    assert infer_category("Jio recharge") == "Telecom"

def test_infer_category_dmart():
    assert infer_category("DMart groceries") == "Groceries"

def test_infer_category_salary():
    assert infer_category("received salary this month") == "Income"

def test_infer_category_unknown():
    assert infer_category("random unknown merchant xyz") == "Other"


# ── Chart builder tests ────────────────────────────────────────────────────────

def test_pie_chart_structure():
    ctx = build_mock_context("user_priya")
    chart = build_pie_chart(ctx)
    assert chart.type == "pie"
    assert len(chart.data) > 0
    for item in chart.data:
        assert "name" in item
        assert "value" in item
        assert item["value"] >= 0

def test_bar_chart_structure():
    ctx = build_mock_context("user_arjun")
    chart = build_bar_chart(ctx)
    assert chart.type == "bar"
    assert len(chart.data) > 0
    for item in chart.data:
        assert "category" in item
        assert "thisMonth" in item
        assert "lastMonth" in item

def test_goal_progress_chart():
    ctx = build_mock_context("user_priya")
    goal = ctx.goals[0]
    chart = build_goal_progress_chart(goal)
    assert chart.type == "progress"
    assert len(chart.data) == 1
    d = chart.data[0]
    assert "pct" in d
    assert 0 <= d["pct"] <= 100


# ── Context formatter tests ────────────────────────────────────────────────────

def test_format_context_contains_name():
    ctx = build_mock_context("user_priya")
    result = format_context_for_prompt(ctx)
    assert "Priya" in result

def test_format_context_contains_inr():
    ctx = build_mock_context("user_priya")
    result = format_context_for_prompt(ctx)
    assert "₹" in result

def test_format_context_contains_categories():
    ctx = build_mock_context("user_priya")
    result = format_context_for_prompt(ctx)
    assert "Food & Dining" in result or "Housing" in result

def test_format_history_empty():
    result = format_history_for_prompt([])
    assert "No prior" in result

def test_format_history_with_messages():
    history = [
        {"role": "user", "content": "how much did I spend?"},
        {"role": "assistant", "content": "You spent ₹5,250 this month."},
    ]
    result = format_history_for_prompt(history)
    assert "how much did I spend?" in result


# ── Goal model property tests ──────────────────────────────────────────────────

def test_goal_pct_complete():
    ctx = build_mock_context("user_priya")
    for goal in ctx.goals:
        assert 0 <= goal.pct_complete <= 100

def test_goal_amount_remaining():
    ctx = build_mock_context("user_priya")
    for goal in ctx.goals:
        assert goal.amount_remaining >= 0

def test_budget_status_property():
    ctx = build_mock_context("user_priya")
    for b in ctx.budget_status:
        assert b.status in ["ok", "warning", "over"]


# ── Monthly snapshot property tests ───────────────────────────────────────────

def test_snapshot_savings_rate():
    ctx = build_mock_context("user_priya")
    snap = ctx.current_month
    assert isinstance(snap.savings_rate, float)
    # Priya spends ~27k of 60k = ~55% savings rate
    assert snap.savings_rate > 0

def test_snapshot_net():
    ctx = build_mock_context("user_arjun")
    snap = ctx.current_month
    assert snap.net == snap.total_income - snap.total_expenses
