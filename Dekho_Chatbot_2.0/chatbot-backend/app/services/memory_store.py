"""
Memory Store — manages conversation history per session.
- In-session: Redis list (fast, ephemeral)
- Cross-session: PostgreSQL summaries (persistent)
"""

from __future__ import annotations
import json
import logging
import uuid
from datetime import datetime

from app.services.cache import cache_lpush, cache_lrange
from app.config import settings
from app.services import db_store

logger = logging.getLogger("dekho.memory")


def _session_key(session_id: str) -> str:
    return f"sess:{session_id}:messages"


def new_session_id() -> str:
    return str(uuid.uuid4())


async def store_message(session_id: str, role: str, content: str, intent: str | None = None, user_id: str | None = None) -> None:
    """Append a message to session history in Redis AND persist to SQLite DB."""
    msg = {
        "role": role,
        "content": content,
        "intent": intent,
        "timestamp": datetime.utcnow().isoformat(),
    }
    # Fast in-session store (Redis / in-memory)
    await cache_lpush(
        _session_key(session_id),
        json.dumps(msg),
        max_len=settings.in_session_message_limit * 2,
        ttl=settings.session_ttl_seconds,
    )
    # Persistent store (SQLite)
    if user_id:
        await db_store.save_message(user_id, session_id, role, content, intent)


async def get_history(session_id: str) -> list[dict]:
    """Return conversation history for a session (most recent first → reversed for LLM)."""
    raw_messages = await cache_lrange(_session_key(session_id))
    messages = []
    for raw in raw_messages:
        try:
            messages.append(json.loads(raw))
        except json.JSONDecodeError:
            pass
    # Redis lpush → newest first; reverse to chronological order
    messages.reverse()
    return messages


async def get_llm_history(session_id: str) -> list[dict]:
    """
    Return history in LLM-ready format: [{"role": "user"|"assistant", "content": "..."}]
    Limited to last N turns for context window efficiency.
    Both OpenRouter and Groq use the OpenAI-compatible "assistant" role.
    """
    history = await get_history(session_id)
    return [
        {"role": msg["role"], "content": msg["content"]}
        for msg in history[-settings.in_session_message_limit:]
    ]


async def clear_session(session_id: str) -> None:
    """Clear all messages for a session (e.g. user hits 'New Chat')."""
    from app.services.cache import cache_delete
    await cache_delete(_session_key(session_id))
    logger.info("Session %s cleared", session_id)
