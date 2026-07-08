"""
Session Summarizer — generates cross-session memory via LLM.
Also extracts user behavior patterns (topics, style, interests) for auto-learning.
"""

from __future__ import annotations
import json
import logging
from datetime import datetime

from app.services.cache import cache_lrange, cache_get, cache_set
from app.config import settings

logger = logging.getLogger("dekho.summarizer")

SUMMARIZE_PROMPT = """You are a memory assistant for a personal finance chatbot called Dekho.

Summarize the following conversation in 2-3 concise sentences. Focus on:
- What financial questions the user asked
- Key insights or numbers discussed
- Any actions the user mentioned taking

Be brief and factual. This summary will be injected into future sessions to maintain context.

Conversation:
{conversation}

Summary:"""


PATTERN_EXTRACT_PROMPT = """You are an analyst for a personal finance chatbot called Dekho.

Analyze the following conversation and extract user behavior patterns as a JSON object.

Return ONLY a raw JSON object (no markdown, no explanation) with these exact keys:
- "topics_of_interest": array of up to 3 financial topics the user asked about most (e.g. ["Food & Dining", "Goals", "Budget"])
- "preferred_style": "brief" | "balanced" | "detailed" — based on how detailed their questions are
- "common_corrections": array of up to 2 correction strings if the user corrected the chatbot

Example output:
{{"topics_of_interest": ["Food & Dining", "Goals"], "preferred_style": "brief", "common_corrections": []}}

Conversation:
{conversation}"""


async def maybe_summarize_session(session_id: str, user_id: str, force: bool = False) -> str | None:
    """
    Summarize the session if it has >= 10 messages or force=True.
    Also triggers pattern extraction for auto-learning.
    Returns the summary string if generated, else None.
    """
    from app.services.memory_store import get_history
    from app.services.llm_client import LLMClient

    history = await get_history(session_id)
    if not history:
        return None

    # Only summarize if enough messages or forced
    if not force and len(history) < 10:
        return None

    # Build conversation text
    lines = []
    for msg in history:
        role = "User" if msg["role"] == "user" else "Dekho"
        lines.append(f"{role}: {msg['content'][:300]}")
    conversation_text = "\n".join(lines)

    try:
        client = LLMClient()
        summary = await client.generate(
            system_prompt="You are a concise memory assistant for a finance chatbot.",
            user_message=SUMMARIZE_PROMPT.format(conversation=conversation_text),
            max_tokens=150,
            temperature=0.3,
        )

        # Cache the summary keyed by user_id (last 3 sessions)
        await _store_session_summary(user_id, session_id, summary.strip())
        logger.info("Session %s summarized for user %s", session_id, user_id)

        # Extract patterns for auto-learning (non-blocking)
        import asyncio
        asyncio.create_task(_extract_and_store_patterns(client, user_id, conversation_text))

        return summary.strip()

    except Exception as e:
        logger.warning("Session summarization failed: %s", e)
        return None


async def _extract_and_store_patterns(client, user_id: str, conversation_text: str) -> None:
    """
    Extract behavioral patterns from conversation and persist to user_preferences.
    Runs non-blocking after the main summary is stored.
    """
    import re
    from app.services import db_store

    try:
        raw = await client.generate(
            system_prompt="You extract user behavior patterns from chat conversations. Output only raw JSON.",
            user_message=PATTERN_EXTRACT_PROMPT.format(conversation=conversation_text),
            max_tokens=120,
            temperature=0.2,
        )
        raw = re.sub(r"```(?:json)?", "", raw).strip()
        patterns = json.loads(raw)

        updates: dict = {}

        topics = patterns.get("topics_of_interest", [])
        if isinstance(topics, list) and topics:
            updates["top_interests"] = topics[:3]

        style = patterns.get("preferred_style", "")
        if style in ("brief", "balanced", "detailed"):
            updates["response_style"] = style

        corrections = patterns.get("common_corrections", [])
        if isinstance(corrections, list) and corrections:
            prefs = await db_store.get_user_preferences(user_id)
            existing = prefs.get("corrections", [])
            updates["corrections"] = (existing + corrections)[-10:]

        if updates:
            await db_store.upsert_user_preferences(user_id, updates)
            logger.info("Patterns extracted + stored for user %s: %s", user_id, updates)

    except Exception as e:
        logger.debug("Pattern extraction failed (non-critical): %s", e)


async def _store_session_summary(user_id: str, session_id: str, summary: str) -> None:
    """Store summary in Redis list (last 3 summaries per user)."""
    from app.services.cache import cache_lpush
    key = f"summaries:{user_id}"
    record = json.dumps({
        "session_id": session_id,
        "summary": summary,
        "timestamp": datetime.utcnow().isoformat(),
    })
    await cache_lpush(key, record, max_len=3, ttl=60 * 60 * 24 * 30)  # 30 days


async def get_session_summaries(user_id: str) -> list[str]:
    """
    Return last 3 session summaries for injection into master prompt.
    Used for cross-session memory.
    """
    from app.services.cache import cache_lrange
    key = f"summaries:{user_id}"
    raw = await cache_lrange(key, 0, 2)
    summaries = []
    for r in raw:
        try:
            data = json.loads(r)
            summaries.append(data["summary"])
        except Exception:
            pass
    return summaries
