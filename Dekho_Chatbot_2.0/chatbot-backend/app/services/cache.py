"""
Redis cache service — async connection pool.
Uses redis.asyncio (redis-py >= 5.0) — compatible with Python 3.13.
aioredis is NOT used (broken on Python 3.13 due to TimeoutError MRO conflict).
"""

from __future__ import annotations
import logging
import redis.asyncio as aioredis
from redis.asyncio import Redis
from app.config import settings

logger = logging.getLogger("dekho.cache")

_redis: Redis | None = None


async def init_redis() -> None:
    global _redis
    if not settings.redis_url:
        logger.info("No REDIS_URL set — cache disabled")
        return
    try:
        _redis = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
        )
        await _redis.ping()
        logger.info("Redis connected at %s", settings.redis_url)
    except Exception as e:
        logger.warning("Redis unavailable (%s) — cache will be skipped", e)
        _redis = None


async def close_redis() -> None:
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None


async def get_redis() -> Redis | None:
    return _redis


async def cache_get(key: str) -> str | None:
    if _redis is None:
        return None
    try:
        return await _redis.get(key)
    except Exception:
        return None


async def cache_set(key: str, value: str, ttl: int = 300) -> None:
    if _redis is None:
        return
    try:
        await _redis.set(key, value, ex=ttl)
    except Exception as e:
        logger.debug("Cache set failed: %s", e)


async def cache_delete(key: str) -> None:
    if _redis is None:
        return
    try:
        await _redis.delete(key)
    except Exception:
        pass


async def cache_lpush(key: str, value: str, max_len: int = 10, ttl: int = 1800) -> None:
    """Push to a Redis list, trim to max_len, reset TTL."""
    if _redis is None:
        return
    try:
        pipe = _redis.pipeline()
        pipe.lpush(key, value)
        pipe.ltrim(key, 0, max_len - 1)
        pipe.expire(key, ttl)
        await pipe.execute()
    except Exception as e:
        logger.debug("Cache lpush failed: %s", e)


async def cache_lrange(key: str, start: int = 0, end: int = -1) -> list[str]:
    """Get all items from a Redis list."""
    if _redis is None:
        return []
    try:
        return await _redis.lrange(key, start, end)
    except Exception:
        return []
