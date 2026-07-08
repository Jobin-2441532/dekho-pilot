"""
Rate Limiter — per-user sliding window rate limiting for LLM requests.
Uses Redis to track request counts (degrades gracefully if Redis is down).
"""

from __future__ import annotations
import time
import logging
from app.services.cache import get_redis
from app.config import settings

logger = logging.getLogger("dekho.ratelimit")


async def check_rate_limit(user_id: str) -> tuple[bool, int]:
    """
    Check if user is within LLM rate limit.
    Returns (allowed: bool, remaining: int)
    Uses a sliding 60-second window.
    """
    r = await get_redis()
    if r is None:
        # Redis down — allow request (degrade gracefully)
        return True, settings.llm_rate_limit_per_minute

    key = f"rl:{user_id}:{int(time.time() // 60)}"  # per-minute bucket
    try:
        count = await r.incr(key)
        if count == 1:
            await r.expire(key, 60)

        remaining = max(0, settings.llm_rate_limit_per_minute - count)
        allowed = count <= settings.llm_rate_limit_per_minute
        return allowed, remaining
    except Exception as e:
        logger.warning("Rate limit check failed: %s — allowing request", e)
        return True, settings.llm_rate_limit_per_minute
