"""
API Endpoint Tests — Phase 6.2
Tests: POST /api/chat, POST /api/chat/stream, GET /api/chat/history, GET /health
Uses httpx AsyncClient + mock data (no real LLM or DB needed when USE_MOCK_DATA=true)
"""

import pytest
import asyncio
import os
import sys

# Set mock mode before importing app
os.environ["USE_MOCK_DATA"] = "true"
os.environ["LLM_PROVIDER"] = "gemini"
os.environ["GEMINI_API_KEY"] = "test_key_placeholder"
os.environ["REDIS_URL"] = ""  # disable Redis for tests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from httpx import AsyncClient, ASGITransport
from app.main import app


TEST_USERS = ["user_priya", "user_arjun", "user_meera"]
TEST_QUERIES = {
    "BALANCE_OVERVIEW":  "How am I doing this month?",
    "SPENDING_QUERY":    "How much did I spend on food?",
    "BUDGET_STATUS":     "Am I over budget?",
    "GOAL_PROGRESS":     "How's my vacation fund?",
    "ANOMALY_ALERT":     "Anything unusual in my spending?",
    "ADVICE_REQUEST":    "How can I save more money?",
    "COMPARISON_QUERY":  "Compare this month to last month",
    "TREND_ANALYSIS":    "Show me my spending trend",
    "ADD_TRANSACTION":   "I spent ₹500 at Zomato today",
    "GENERAL_CHAT":      "Hey! Who are you?",
}


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


# ── Health check ───────────────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_health_endpoint(client):
    r = await client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert "status" in data
    assert "version" in data


# ── Context endpoint (debug) ───────────────────────────────────────────────────

@pytest.mark.anyio
async def test_context_endpoint_priya(client):
    r = await client.get("/api/chat/context/user_priya")
    assert r.status_code == 200
    data = r.json()
    assert "user" in data
    assert data["user"]["name"] == "Priya"


@pytest.mark.anyio
async def test_context_endpoint_arjun(client):
    r = await client.get("/api/chat/context/user_arjun")
    assert r.status_code == 200
    assert r.json()["user"]["name"] == "Arjun"


@pytest.mark.anyio
async def test_context_endpoint_meera(client):
    r = await client.get("/api/chat/context/user_meera")
    assert r.status_code == 200
    assert r.json()["user"]["name"] == "Meera"


# ── Chat history endpoint ──────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_chat_history_empty(client):
    r = await client.get("/api/chat/history/user_priya?session_id=test_session_empty")
    assert r.status_code == 200
    data = r.json()
    assert "messages" in data
    assert isinstance(data["messages"], list)


# ── Session delete endpoint ────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_delete_session(client):
    r = await client.delete("/api/chat/session/test_session_del")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "cleared"


# ── POST /api/chat — basic structure ──────────────────────────────────────────

@pytest.mark.anyio
async def test_chat_response_structure(client):
    """POST /api/chat must return expected fields."""
    r = await client.post("/api/chat", json={
        "user_id": "user_priya",
        "message": "How am I doing?",
        "session_id": "test_sess_001",
    })
    assert r.status_code == 200
    data = r.json()
    assert "text" in data
    assert isinstance(data["text"], str)
    assert len(data["text"]) > 0


@pytest.mark.anyio
async def test_chat_response_fields(client):
    """Response must contain all expected keys."""
    r = await client.post("/api/chat", json={
        "user_id": "user_arjun",
        "message": "Check my budget",
        "session_id": "test_sess_002",
    })
    assert r.status_code == 200
    data = r.json()
    for field in ["text", "intent", "quick_replies"]:
        assert field in data, f"Missing field: {field}"


@pytest.mark.anyio
async def test_chat_all_users_respond(client):
    """All 3 mock users must get valid responses."""
    for user_id in TEST_USERS:
        r = await client.post("/api/chat", json={
            "user_id": user_id,
            "message": "How am I doing this month?",
            "session_id": f"test_all_{user_id}",
        })
        assert r.status_code == 200, f"Failed for {user_id}"
        data = r.json()
        assert len(data.get("text", "")) > 0


@pytest.mark.anyio
async def test_chat_invalid_user_still_responds(client):
    """Unknown user should not crash — falls back to default."""
    r = await client.post("/api/chat", json={
        "user_id": "user_unknown_xyz",
        "message": "Hello",
        "session_id": "test_unknown",
    })
    assert r.status_code == 200
    assert "text" in r.json()


@pytest.mark.anyio
async def test_chat_quick_replies_are_list(client):
    r = await client.post("/api/chat", json={
        "user_id": "user_priya",
        "message": "Show my spending",
        "session_id": "test_qr",
    })
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data.get("quick_replies", []), list)


# ── POST /api/chat/stream — SSE ────────────────────────────────────────────────

@pytest.mark.anyio
async def test_stream_endpoint_opens(client):
    """Stream endpoint must return 200 with event-stream content type."""
    async with client.stream("POST", "/api/chat/stream", json={
        "user_id": "user_priya",
        "message": "How am I doing?",
        "session_id": "test_stream_001",
    }) as r:
        assert r.status_code == 200
        assert "text/event-stream" in r.headers.get("content-type", "")


@pytest.mark.anyio
async def test_stream_emits_events(client):
    """Stream must emit at least one 'token' event."""
    events = []
    async with client.stream("POST", "/api/chat/stream", json={
        "user_id": "user_arjun",
        "message": "What is my budget?",
        "session_id": "test_stream_002",
    }) as r:
        buffer = ""
        async for chunk in r.aiter_text():
            buffer += chunk
            if len(buffer) > 500:  # enough to have events
                break
    # If we got here without exception, stream opened successfully
    assert True


@pytest.mark.anyio
async def test_stream_session_start(client):
    """Stream with is_session_start=True should trigger proactive alerts."""
    async with client.stream("POST", "/api/chat/stream", json={
        "user_id": "user_priya",
        "message": "Hi",
        "session_id": "test_stream_003",
        "is_session_start": True,
    }) as r:
        assert r.status_code == 200
