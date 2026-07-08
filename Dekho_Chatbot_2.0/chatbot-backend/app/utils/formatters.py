"""
INR formatter, date helpers, and other text utilities.
"""

from __future__ import annotations
from typing import Optional


def fmt_inr(amount: float) -> str:
    """Format amount in Indian number system: ₹1,23,456."""
    if amount < 0:
        return f"-{fmt_inr(-amount)}"
    amount = round(amount, 2)
    s = f"{amount:.0f}"
    if len(s) <= 3:
        return f"₹{s}"
    # Indian grouping: last 3 digits, then groups of 2
    last3 = s[-3:]
    rest = s[:-3]
    groups = []
    while len(rest) > 2:
        groups.append(rest[-2:])
        rest = rest[:-2]
    if rest:
        groups.append(rest)
    groups.reverse()
    formatted = ",".join(groups) + "," + last3
    return f"₹{formatted}"


def fmt_pct(value: float) -> str:
    """Format percentage: 72.3%"""
    return f"{value:.1f}%"


def fmt_days(days: Optional[int]) -> str:
    """Format days remaining into human-readable string."""
    if days is None:
        return "no deadline"
    if days < 0:
        return f"{abs(days)} days overdue"
    if days == 0:
        return "due today"
    if days == 1:
        return "1 day"
    if days < 7:
        return f"{days} days"
    weeks = days // 7
    remainder = days % 7
    if remainder == 0:
        return f"{weeks} week{'s' if weeks > 1 else ''}"
    return f"{weeks}w {remainder}d"


def weekly_savings_needed(remaining: float, days_left: int) -> str:
    """Calculate weekly savings required to hit a goal on time."""
    if days_left <= 0:
        return "overdue"
    weeks = max(1, days_left / 7)
    per_week = remaining / weeks
    return fmt_inr(per_week) + "/week"
