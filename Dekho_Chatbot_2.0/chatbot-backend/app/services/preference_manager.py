"""
Preference Manager — detects user preference signals from messages and injects
learned preferences into the LLM prompt.

Signal detection:
  - "in one line", "brief", "short" → response_style = brief
  - "in detail", "explain more", "full breakdown" → response_style = detailed
  - "show me a chart", "pie chart", "bar chart" → prefers_charts = True
  - "no chart", "without chart", "just text" → prefers_charts = False

Injection format (added to system prompt):
  ## Your learned preferences for this user
  - Prefers brief responses
  - Prefers charts: Yes
  - Recent corrections: ["that was wrong, I spent on groceries not food"]
"""

from __future__ import annotations
import logging
import re

logger = logging.getLogger("dekho.preferences")

# ── Signal patterns ───────────────────────────────────────────────────────────

BRIEF_PATTERNS = [
    r"\bin one line\b", r"\bbriefly\b", r"\bshort\b", r"\bquick\b",
    r"\bjust the number\b", r"\bsimply\b", r"\bone sentence\b",
]

DETAILED_PATTERNS = [
    r"\bin detail\b", r"\bdetailed\b", r"\bfull breakdown\b",
    r"\bexplain\b", r"\btell me more\b", r"\bbreak it down\b",
]

CHART_ON_PATTERNS = [
    r"\bshow.*chart\b", r"\bpie chart\b", r"\bbar chart\b",
    r"\bline chart\b", r"\bgraph\b", r"\bvisuali[sz]e\b",
]

CHART_OFF_PATTERNS = [
    r"\bno chart\b", r"\bwithout chart\b", r"\bjust text\b",
    r"\bno graph\b", r"\btext only\b",
]


def detect_signals(message: str) -> dict:
    """
    Scan a user message for preference signals.
    Returns a dict of detected signals (only keys that were detected).
    """
    msg = message.lower()
    signals: dict = {}

    if any(re.search(p, msg) for p in BRIEF_PATTERNS):
        signals["response_style"] = "brief"
    elif any(re.search(p, msg) for p in DETAILED_PATTERNS):
        signals["response_style"] = "detailed"

    if any(re.search(p, msg) for p in CHART_ON_PATTERNS):
        signals["prefers_charts"] = True
    elif any(re.search(p, msg) for p in CHART_OFF_PATTERNS):
        signals["prefers_charts"] = False

    return signals


def format_preferences_for_prompt(prefs: dict) -> str:
    """
    Format user preferences as a block for injection into the system prompt.
    Returns an empty string if no meaningful preferences are set.
    """
    lines = []

    style = prefs.get("response_style", "balanced")
    if style == "brief":
        lines.append("- This user prefers SHORT responses — keep answers to 1 sentence where possible.")
    elif style == "detailed":
        lines.append("- This user prefers DETAILED responses — provide more context and breakdown when relevant.")

    if not prefs.get("prefers_charts", True):
        lines.append("- This user prefers TEXT-ONLY responses — do not include charts.")

    corrections = prefs.get("corrections", [])
    if corrections:
        recent = corrections[-3:]  # inject last 3 corrections
        lines.append(f"- User has previously corrected: {'; '.join(repr(c) for c in recent)}")

    if not lines:
        return ""

    return "## User Preferences (learned over time)\n" + "\n".join(lines)
