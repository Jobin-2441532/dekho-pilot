"""
Pydantic schemas — the full data contract between chatbot and V2 DB.
"""

from __future__ import annotations
from datetime import date, datetime
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field


# ── User / Profile ─────────────────────────────────────────────────────────────

class UserProfile(BaseModel):
    id: str
    name: str
    currency: str = "INR"
    primary_goal: Literal["save", "invest", "budget", "debt_free"] = "save"
    tone_preference: Literal["friendly", "formal", "casual"] = "friendly"


# ── Transactions ───────────────────────────────────────────────────────────────

class Transaction(BaseModel):
    id: str
    user_id: str
    amount: float
    type: str
    category: str
    subcategory: Optional[str] = None
    description: Optional[str] = None
    date: date
    is_recurring: bool = False


# ── Budgets ────────────────────────────────────────────────────────────────────

class BudgetEntry(BaseModel):
    category: str
    monthly_limit: float
    spent: float
    pct_used: float = Field(..., description="0–100 percent of budget used")

    @property
    def status(self) -> Literal["ok", "warning", "over"]:
        if self.pct_used >= 100:
            return "over"
        if self.pct_used >= 80:
            return "warning"
        return "ok"


# ── Savings Goals ──────────────────────────────────────────────────────────────

class SavingsGoal(BaseModel):
    id: str
    goal_name: str
    target_amount: float
    current_amount: float
    deadline: Optional[date] = None
    category: str = "general"

    @property
    def pct_complete(self) -> float:
        if self.target_amount == 0:
            return 0.0
        return round((self.current_amount / self.target_amount) * 100, 1)

    @property
    def amount_remaining(self) -> float:
        return max(0.0, self.target_amount - self.current_amount)

    @property
    def days_left(self) -> Optional[int]:
        if self.deadline is None:
            return None
        return (self.deadline - date.today()).days


# ── Monthly Snapshot ───────────────────────────────────────────────────────────

class MonthlySnapshot(BaseModel):
    user_id: str
    month: str                              # "2026-06"
    total_expenses: float
    by_category: dict[str, float]           # { "Food & Dining": 4200.0, ... }


# ── Assembled User Context (core chatbot input) ────────────────────────────────

class BudgetAlert(BaseModel):
    category: str
    limit: float
    spent: float
    pct_used: float

class Anomaly(BaseModel):
    category: str
    current_spend: float
    avg_3month: float
    pct_over_avg: float

class UserFinancialContext(BaseModel):
    """The complete financial snapshot injected into every LLM prompt."""
    user: UserProfile
    current_month: MonthlySnapshot
    budget_status: list[BudgetEntry]
    budget_alerts: list[BudgetAlert]        # categories > 80% used
    goals: list[SavingsGoal]
    top_expenses: list[Transaction]         # top 5 by amount this month
    recent_transactions: list[Transaction]  # last 7 days, max 10
    anomalies: list[Anomaly]               # categories > 120% of 3-month avg
    historical_months: list[MonthlySnapshot] = []
    user_stats: dict[str, Any] = {}         # dynamic calculated stats (e.g. daily avg spend, weekend vs weekday avg)


# ── Chat API ───────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    user_id: str
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None


class ChartData(BaseModel):
    type: Literal["pie", "bar", "line", "progress"]
    title: str
    data: list[dict[str, Any]]
    config: Optional[dict[str, Any]] = None  # recharts config hints


class AlertPayload(BaseModel):
    type: Literal["BUDGET_ALERT", "GOAL_URGENT", "CASHFLOW_ALERT", "ANOMALY"]
    message: str
    severity: Literal["info", "warning", "critical"]


class ChatResponse(BaseModel):
    session_id: str
    text: str
    intent: str
    chart: Optional[ChartData] = None
    quick_replies: list[str] = []
    alert: Optional[AlertPayload] = None
    latency_ms: int = 0
    is_fallback: bool = False


# ── Conversation History ───────────────────────────────────────────────────────

class ConversationMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    intent: Optional[str] = None
    timestamp: datetime


class ConversationHistory(BaseModel):
    user_id: str
    session_id: str
    messages: list[ConversationMessage]
