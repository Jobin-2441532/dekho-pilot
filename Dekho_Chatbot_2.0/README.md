# Ask Dekho 2.0 — Chatbot Module

> Personalized AI finance chatbot for Indian users. Standalone module, integrates with the main V2 app.

## Quick Start

### Backend
```bash
cd chatbot-backend
pip install -r requirements.txt
cp .env.example .env      # add OPENROUTER_API_KEY and GROQ_API_KEY
uvicorn app.main:app --reload --port 8001
```

### Frontend (test UI)
```bash
cd chatbot-frontend
npm install
npm run dev               # opens at http://localhost:5173
```

## What's Built

| Component | Description |
|-----------|-------------|
| `chatbot-backend/` | FastAPI service — intent detection, LLM client, context builder, Redis cache, SSE streaming |
| `chatbot-frontend/` | React + Vite test UI — dark theme, streaming bubbles, inline charts, debug panel |
| `docs/integration-guide.md` | Full API reference for the main V2 team |
| `tests/test_unit.py` | 50+ unit tests |
| `tests/test_api.py` | API endpoint tests |
| `tests/locustfile.py` | Locust load test (100 VU) |

## Running Tests

```bash
cd chatbot-backend
pip install pytest pytest-anyio httpx
pytest tests/test_unit.py -v
```

## Load Testing

```bash
pip install locust
locust -f tests/locustfile.py --host=http://localhost:8001 -u 100 -r 10 -t 5m
```

## Architecture

```
User message
     │
     ▼
Rate Limiter (20 req/min/user)
     │
     ▼
Response Cache check (5-min TTL per intent)
     │  ← cache hit? return instantly
     ▼
Context Builder → Redis (5-min TTL)
     │
     ▼
Intent Detector (LLM few-shot, returns JSON)
     │
     ▼
Prompt Engine (Master prompt + intent sub-template + cross-session memory)
     │
     ▼
LLM Client (OpenRouter primary → Groq fallback → static fallback, streaming, retries)
     │
     ▼
Response Builder (chart + quick replies + proactive alerts)
     │
     ▼
SSE stream → Frontend
```

## See Also

- [Integration Guide](docs/integration-guide.md) — for the main V2 app team
- [Task Checklist](..) — full progress tracker
