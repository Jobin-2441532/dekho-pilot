"""
Ask Dekho 2.0 — Chatbot Backend
================================
Standalone FastAPI chatbot service.
This service is the AI engine for the Ask Dekho conversational chatbot.

Endpoints:
    GET  /health                          — service health check
    POST /api/chat                        — single-shot chat response
    POST /api/chat/stream                 — streaming chat response (SSE)
    GET  /api/chat/history/{user_id}      — conversation history
    GET  /api/chat/context/{user_id}      — debug: show user's financial context

Run locally:
    uvicorn app.main:app --reload --port 8002
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.chat import router as chat_router
from app.config import settings
from app.services.cache import init_redis, close_redis
from app.services.db_pool import init_pool, close_pool
from app.services.db_store import init_db

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s %(name)s: %(message)s",
)
logger = logging.getLogger("dekho.chatbot")


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Dekho Chatbot Backend starting up...")
    await init_redis()
    await init_pool()
    await init_db()
    yield
    logger.info("👋 Shutting down...")
    await close_redis()
    await close_pool()


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Ask Dekho Chatbot API",
    description="AI-powered personal finance chatbot for Dekho V2",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])


@app.get("/health", tags=["health"])
async def health():
    """Service health check — checks DB, Redis, OpenRouter, and Groq connectivity."""
    from app.services.cache import get_redis
    from openai import AsyncOpenAI

    statuses: dict[str, str] = {}

    # Redis
    try:
        r = await get_redis()
        if r is None:
            statuses["redis"] = "disabled (no REDIS_URL)"
        else:
            await r.ping()
            statuses["redis"] = "ok"
    except Exception as e:
        statuses["redis"] = f"error: {e}"

    # OpenRouter — check key is configured (lightweight; no API call to avoid quota use)
    try:
        if not settings.openrouter_api_key:
            statuses["llm_openrouter"] = "error: OPENROUTER_API_KEY not set"
        else:
            AsyncOpenAI(
                api_key=settings.openrouter_api_key,
                base_url=settings.openrouter_base_url,
                default_headers={"HTTP-Referer": "https://askdekho.app", "X-Title": "Ask Dekho"},
            )
            statuses["llm_openrouter"] = f"ok (model: {settings.openrouter_model})"
    except Exception as e:
        statuses["llm_openrouter"] = f"error: {e}"

    # Groq — check key is configured
    try:
        if not settings.groq_api_key:
            statuses["llm_groq"] = "error: GROQ_API_KEY not set"
        else:
            AsyncOpenAI(
                api_key=settings.groq_api_key,
                base_url=settings.groq_base_url,
            )
            statuses["llm_groq"] = f"ok (model: {settings.groq_model})"
    except Exception as e:
        statuses["llm_groq"] = f"error: {e}"

    # DB (skipped if USE_MOCK_DATA=true)
    if settings.use_mock_data:
        statuses["db"] = "mock (USE_MOCK_DATA=true)"
    else:
        try:
            from app.services.data_layer import DataLayer
            async with DataLayer() as dl:
                await dl.ping()
            statuses["db"] = "ok"
        except Exception as e:
            statuses["db"] = f"error: {e}"

    overall = "healthy" if all(
        v.startswith("ok") or "mock" in v or "disabled" in v
        for v in statuses.values()
    ) else "degraded"
    return {"status": overall, "version": "2.0.0", "services": statuses}

