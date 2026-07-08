"""
Semantic Response Cache — caches LLM responses by (user_id + intent + message_hash + 5-min time bucket).
Avoids redundant LLM calls for the same question asked multiple times in a short window.

IMPORTANT: The cache key includes a hash of the normalised message text so that
two different questions with the same intent (e.g. "food spending" vs "travel spending")
always get independent cache entries and never return each other's answers.
"""

from __future__ import annotations
import hashlib
import json
import logging
import time
from app.services.cache import cache_get, cache_set

logger = logging.getLogger("dekho.response_cache")

CACHE_TTL = 300  # 5 minutes

# These intents are slot-sensitive (category, time_period, merchant) —
# caching them risks returning a wrong answer, not just a stale one.
_NEVER_CACHE_INTENTS = {
    "SPENDING_QUERY",    # "food" vs "travel" — different answer, same intent
    "COMPARISON_QUERY",  # different time periods
}


def _message_hash(message: str) -> str:
    """Stable short hash of the normalised message (lowercase, stripped)."""
    normalised = message.lower().strip()
    return hashlib.md5(normalised.encode()).hexdigest()[:8]


def _cache_key(user_id: str, intent: str, message: str = "") -> str:
    bucket = int(time.time() // CACHE_TTL)  # 5-min bucket
    msg_hash = _message_hash(message) if message else "x"
    raw = f"{user_id}:{intent}:{msg_hash}:{bucket}"
    return "rc:" + hashlib.md5(raw.encode()).hexdigest()


async def get_cached_response(user_id: str, intent: str, message: str = "") -> dict | None:
    """Return cached response if available for this user+intent+message in the current 5-min window."""
    if intent in _NEVER_CACHE_INTENTS:
        return None
    key = _cache_key(user_id, intent, message)
    raw = await cache_get(key)
    if raw:
        try:
            logger.debug("Response cache HIT — user=%s intent=%s", user_id, intent)
            return json.loads(raw)
        except Exception:
            return None
    return None


def _serialize_response(response: dict) -> str:
    """Serialize response dict to JSON, handling Pydantic model sub-objects."""
    serializable = {}
    for k, v in response.items():
        if hasattr(v, "model_dump"):
            serializable[k] = v.model_dump()
        else:
            serializable[k] = v
    return json.dumps(serializable)


async def set_cached_response(user_id: str, intent: str, response: dict, message: str = "") -> None:
    """Cache a response for this user+intent+message."""
    # Don't cache fallback responses or slot-sensitive intents
    if response.get("is_fallback") or intent in _NEVER_CACHE_INTENTS:
        return
    key = _cache_key(user_id, intent, message)
    try:
        await cache_set(key, _serialize_response(response), ttl=CACHE_TTL)
        logger.debug("Response cached — user=%s intent=%s", user_id, intent)
    except Exception as e:
        logger.debug("Response cache set failed: %s", e)
