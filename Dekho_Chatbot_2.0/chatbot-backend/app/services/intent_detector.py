"""
Intent Detector — classifies user messages into one of 10 defined intents
using LLM few-shot classification. Returns JSON: {intent, confidence, slots}.

Compatible with any OpenAI-compatible provider (OpenRouter, Groq, etc.).
The system prompt is written to elicit plain JSON from open-source models
that may otherwise wrap output in markdown fences.
"""

from __future__ import annotations
import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any

from app.services.llm_client import LLMClient

logger = logging.getLogger("dekho.intent")

# ── Intent definitions ────────────────────────────────────────────────────────

INTENTS = [
    "BALANCE_OVERVIEW",
    "SPENDING_QUERY",
    "BUDGET_STATUS",
    "GOAL_PROGRESS",
    "ANOMALY_ALERT",
    "ADVICE_REQUEST",
    "COMPARISON_QUERY",
    "TREND_ANALYSIS",
    "OUT_OF_SCOPE",
    "GENERAL_CHAT",
]

INTENT_EXAMPLES = """
BALANCE_OVERVIEW: "what's my financial status", "how am I doing this month", "give me a summary", "financial overview"
SPENDING_QUERY: "how much did I spend on food", "show transport expenses", "what did I spend last month", "how much on groceries this week"
BUDGET_STATUS: "am I over budget", "budget check", "how's my grocery budget", "am I within limits"
GOAL_PROGRESS: "how's my vacation fund", "savings update", "goal progress", "how close am I to my goal", "Goa trip progress", "I am planning to buy a bike in 6 months create a plan", "help me save for a bike", "I want to buy a car next year", "can I set a target for a specific bike model", "how long will it take to save for a bike"
ANOMALY_ALERT: "anything unusual", "flag weird expenses", "show suspicious spending", "what's different this month"
ADVICE_REQUEST: "how can I save more", "tips to cut spending", "how to budget better", "help me spend less on food"
COMPARISON_QUERY: "this month vs last month", "am I spending more", "compare to previous month", "how does this week compare"
TREND_ANALYSIS: "show my spending trend", "am I improving", "spending over time", "monthly trend"
OUT_OF_SCOPE: "where is the backend stored", "what is your gender", "who made you", "what is the weather", "tell me a joke", "what is 2+2", "how much did Arjun spend", "show me other user's data", "what technology are you built on", "are you ChatGPT", "what is your source code", "what's the average cost of a bike", "what is the price of a Royal Enfield", "how much does a car cost", "what is inflation", "how do I invest in stocks", "what is the stock market doing", "what is SIP", "I spent 500 at Zomato", "log 200 metro", "paid 800 for groceries", "add expense 1000 shopping", "received 5000 from client"
GENERAL_CHAT: "hi", "hello", "who are you", "thanks", "what can you do", "good morning", "hows life", "what's up", "how are you", "hey there", "can you talk in general", "ok", "got it", "interesting", "that's cool"
"""

INTENT_SYSTEM_PROMPT = f"""You are an intent classifier for a personal finance chatbot called "Dekho".

Classify the user's message into EXACTLY ONE of these intents:
{', '.join(INTENTS)}

Examples:
{INTENT_EXAMPLES}

Important classification rules:
- Use GOAL_PROGRESS for: questions about saving toward a purchase (bike, car, house, trip), planning to buy something, setting a savings target for a specific item, asking how long to save for X. These are about the USER'S savings plan, not about external product prices.
- Use OUT_OF_SCOPE for: questions about external prices or market costs ("what does a bike cost", "average price of X"), general knowledge, anything not about the user's own financial data, jokes, weather, code/tech questions, other users' data. ALSO classify as OUT_OF_SCOPE if the user is trying to LOG a transaction (e.g. "I spent ₹500 at Zomato", "paid ₹800 for groceries", "log 200 for metro") — Dekho cannot log transactions.
- Use GENERAL_CHAT for: greetings, casual conversation, thanks, social exchanges, non-finance small talk, questions like "hows life", "what's up", "can you talk in general".
- Do NOT use GENERAL_CHAT for out-of-scope questions — use OUT_OF_SCOPE instead.
- Key distinction: "I want to save for a bike" = GOAL_PROGRESS. "What does a bike cost?" = OUT_OF_SCOPE. "I spent ₹3000 on a bike" = OUT_OF_SCOPE (transaction logging).

Also extract relevant slots from the message:
- For SPENDING_QUERY: extract "category" (e.g. "Food & Dining") and "time_period" (e.g. "this month", "last week")
- For GOAL_PROGRESS: extract "goal_name" if mentioned

Your response MUST be a single raw JSON object. Rules:
- No markdown, no code fences, no backticks, no explanation.
- Start your response with {{ and end with }}
- Do not add any text before or after the JSON.

Required format:
{{"intent": "INTENT_NAME", "confidence": 0.0-1.0, "slots": {{}}}}
"""


@dataclass
class IntentResult:
    intent: str
    confidence: float
    slots: dict[str, Any] = field(default_factory=dict)

    @property
    def is_low_confidence(self) -> bool:
        return self.confidence < 0.6


# ── Detector ───────────────────────────────────────────────────────────────────

async def detect_intent(message: str) -> IntentResult:
    """
    Classify user message into an intent using LLM few-shot classification.
    Falls back to GENERAL_CHAT on any error.
    """
    client = LLMClient()

    try:
        raw = await client.generate(
            system_prompt=INTENT_SYSTEM_PROMPT,
            user_message=f'Classify this message: "{message}"',
            max_tokens=200,
            temperature=0.1,  # low temperature for classification
        )

        # Strip markdown fences if present
        raw = re.sub(r"```(?:json)?", "", raw).strip()
        data = json.loads(raw)

        intent = data.get("intent", "GENERAL_CHAT")
        if intent not in INTENTS:
            intent = "GENERAL_CHAT"

        slots = data.get("slots", {})

        return IntentResult(
            intent=intent,
            confidence=float(data.get("confidence", 0.8)),
            slots=slots,
        )

    except json.JSONDecodeError as e:
        logger.warning("Intent JSON parse error: %s | raw: %s", e, raw[:200])
        return IntentResult(intent="GENERAL_CHAT", confidence=0.4)
    except Exception as e:
        logger.error("Intent detection failed: %s", e)
        return IntentResult(intent="GENERAL_CHAT", confidence=0.3)
