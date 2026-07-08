"""
Context Builder — assembles UserFinancialContext for a given user.
In mock mode: reads from mock_data.py
In live mode: queries Neon PostgreSQL (async)
"""

from __future__ import annotations
import json
import logging
from app.config import settings
from app.models.schemas import UserFinancialContext
from app.services.cache import cache_get, cache_set

logger = logging.getLogger("dekho.context")


def _context_cache_key(user_id: str) -> str:
    return f"ctx:{user_id}"


async def build_context(user_id: str) -> UserFinancialContext:
    """
    Main entry point. Returns a cached context if available,
    otherwise builds it from DB/mock and caches it.
    """
    cache_key = _context_cache_key(user_id)

    # Try cache first
    cached = await cache_get(cache_key)
    if cached:
        logger.debug("Context cache HIT for %s", user_id)
        return UserFinancialContext.model_validate_json(cached)

    logger.debug("Context cache MISS for %s — building...", user_id)

    if settings.use_mock_data:
        context = _build_mock_context(user_id)
    else:
        context = await _build_live_context(user_id)

    # Cache it
    await cache_set(
        cache_key,
        context.model_dump_json(),
        ttl=settings.context_cache_ttl_seconds,
    )
    return context


def _build_mock_context(user_id: str) -> UserFinancialContext:
    """Build context from mock data (no DB needed)."""
    from data.mock_data import build_mock_context
    return build_mock_context(user_id)


async def _build_live_context(user_id: str) -> UserFinancialContext:
    """
    Build context by querying the real Neon PostgreSQL database.
    The V2 main app owns writes; this service is READ-ONLY.
    """
    from app.services.data_layer import DataLayer

    async with DataLayer() as dl:
        user = await dl.get_user_profile(user_id)
        snapshot = await dl.get_monthly_snapshot(user_id)
        budgets = await dl.get_budget_status(user_id)
        goals = await dl.get_goals(user_id)
        top_expenses = await dl.get_top_expenses(user_id, limit=5)
        recent_txns = await dl.get_recent_transactions(user_id, days=7, limit=10)
        anomalies = await dl.get_anomalies(user_id, threshold_pct=120)
        historical_months = await dl.get_monthly_snapshots(user_id)
        user_stats = await dl.get_user_stats(user_id)

    from app.models.schemas import BudgetAlert
    budget_alerts = [
        BudgetAlert(
            category=b.category,
            limit=b.monthly_limit,
            spent=b.spent,
            pct_used=b.pct_used,
        )
        for b in budgets if b.pct_used >= 80
    ]

    return UserFinancialContext(
        user=user,
        current_month=snapshot,
        budget_status=budgets,
        budget_alerts=budget_alerts,
        goals=goals,
        top_expenses=top_expenses,
        recent_transactions=recent_txns,
        anomalies=anomalies,
        historical_months=historical_months,
        user_stats=user_stats,
    )


async def invalidate_context(user_id: str) -> None:
    """Call this when a new transaction is added to clear stale cache."""
    from app.services.cache import cache_delete
    await cache_delete(_context_cache_key(user_id))
    logger.info("Context cache invalidated for %s", user_id)
