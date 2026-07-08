# Ask Dekho 2.0 — Chatbot Integration Guide

> **For:** The main V2 app team integrating this chatbot module  
> **Version:** 2.0.0  
> **Last Updated:** June 2026

---

## 1. What This Module Is

A standalone FastAPI chatbot service that:
- Accepts a user's natural language message
- Reads their financial data (read-only)
- Returns a personalized AI response with optional charts, quick-reply chips, and proactive alerts
- Streams responses token-by-token via SSE for a live typing effect

The chatbot **does not own any data** — it reads from the same Neon PostgreSQL DB the main app writes to.

---

## 2. Running Locally

```bash
# Backend (dev mode)
cd chatbot-backend
pip install -r requirements.txt
cp .env.example .env           # fill in GEMINI_API_KEY
uvicorn app.main:app --reload --port 8001

# Backend (production — 4 workers)
python run.py

# Frontend test harness
cd chatbot-frontend
npm install
npm run dev                    # http://localhost:5173
```

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | `AIza...` |
| `LLM_PROVIDER` | `gemini` or `openai` | `gemini` |
| `LLM_MODEL` | Model name | `gemini-1.5-flash` |
| `DATABASE_URL` | Neon PostgreSQL connection string | `postgresql+asyncpg://...` |
| `REDIS_URL` | Redis connection string (optional) | `redis://localhost:6379` |
| `USE_MOCK_DATA` | `true` = use mock data, `false` = real DB | `false` |
| `ALLOWED_ORIGINS` | CORS origins (JSON array) | `["https://yourapp.com"]` |

---

## 3. API Reference

### Base URL
`http://localhost:8001` (dev) · TBD (prod after integration)

---

### `POST /api/chat` — Full Response

Returns a complete response in one JSON object.

**Request:**
```json
{
  "user_id": "user_123",
  "message": "How am I doing this month?",
  "session_id": "session_abc",        // optional, generated if omitted
  "is_session_start": false            // set true on first message of session
}
```

**Response:**
```json
{
  "text": "Hey Priya! You've spent ₹27,450 this month out of ₹60,000 income...",
  "intent": "BALANCE_OVERVIEW",
  "chart": {
    "type": "pie",
    "title": "Spending by Category — June",
    "data": [
      { "name": "Food & Dining", "value": 7200 },
      { "name": "Housing", "value": 12000 }
    ]
  },
  "quick_replies": ["Check my budget", "See my goals", "Give me tips"],
  "alert": null,
  "session_id": "session_abc",
  "latency_ms": 843,
  "is_fallback": false
}
```

---

### `POST /api/chat/stream` — SSE Streaming ⚡

Streams the response token-by-token. Use this for the production chat UI.

**Request:** Same as `/api/chat`

**Response:** `text/event-stream`

**Event Types:**

| Event | Data Format | When |
|-------|-------------|------|
| `intent` | `{"intent": "BALANCE_OVERVIEW", "confidence": 0.95}` | Immediately after intent detection |
| `token` | `{"text": "Hey "}` | Each token as LLM generates it |
| `chart_data` | `{type, title, data, config}` | After full text is generated |
| `quick_replies` | `{"items": ["...", "..."]}` | After chart |
| `alert` | `{type, message, severity}` | If proactive alert triggered |
| `done` | `{"latency_ms": 1234, "session_id": "..."}` | Stream complete |
| `error` | `{"message": "..."}` | On error |
| `fallback` | `{"reason": "timeout"}` | If LLM timed out |

**Example stream:**
```
event: intent
data: {"intent": "BALANCE_OVERVIEW", "confidence": 0.95}

event: token
data: {"text": "Hey "}

event: token
data: {"text": "Priya! "}

event: chart_data
data: {"type": "pie", "title": "Spending by Category", "data": [...]}

event: quick_replies
data: {"items": ["Check budget", "View goals"]}

event: done
data: {"latency_ms": 1240, "session_id": "session_abc"}
```

---

### `GET /api/chat/history/{user_id}?session_id=<id>`

Returns message history for a session.

**Response:**
```json
{
  "user_id": "user_123",
  "session_id": "session_abc",
  "messages": [
    {
      "role": "user",
      "content": "How am I doing?",
      "intent": null,
      "timestamp": "2026-06-16T10:00:00Z"
    },
    {
      "role": "assistant",
      "content": "Hey Priya! You've spent...",
      "intent": "BALANCE_OVERVIEW",
      "timestamp": "2026-06-16T10:00:02Z"
    }
  ]
}
```

---

### `DELETE /api/chat/session/{session_id}`

Clears a session (use for "New Chat" button).

---

### `GET /health`

```json
{
  "status": "ok",
  "version": "2.0.0",
  "db": "ok",
  "redis": "ok",
  "llm": "ok"
}
```

---

## 4. Database Tables (Read-Only Access Required)

The chatbot needs **read-only** access to these tables:

| Table | Columns Used |
|-------|-------------|
| `users` | `id`, `name`, `monthly_income`, `primary_goal`, `tone_preference` |
| `transactions` | `id`, `user_id`, `amount`, `type`, `category`, `subcategory`, `date`, `description` |
| `budgets` | `user_id`, `category`, `monthly_limit`, `month_year` |
| `savings_goals` | `user_id`, `goal_name`, `target_amount`, `current_amount`, `deadline` |
| `monthly_snapshots` | `user_id`, `month`, `total_income`, `total_expenses`, `by_category` (JSONB) |

**Recommended DB indexes** (if not already present):
```sql
CREATE INDEX IF NOT EXISTS idx_transactions_user_date ON transactions(user_id, date);
CREATE INDEX IF NOT EXISTS idx_budgets_user_month ON budgets(user_id, month_year);
CREATE INDEX IF NOT EXISTS idx_goals_user ON savings_goals(user_id);
CREATE INDEX IF NOT EXISTS idx_snapshots_user_month ON monthly_snapshots(user_id, month);
```

---

## 5. Chart Data Payload Format

Chart data is returned in the `chart` field. The frontend team should render based on `type`:

```typescript
interface ChartData {
  type: 'pie' | 'bar' | 'line' | 'progress'
  title: string
  data: Record<string, unknown>[]
  config?: Record<string, unknown>
}
```

**Pie chart data:**
```json
[{ "name": "Food & Dining", "value": 7200 }, ...]
```

**Bar chart data:**
```json
[{ "category": "Food & Dining", "thisMonth": 7200, "lastMonth": 5800 }, ...]
```

**Line chart data:**
```json
[{ "date": "2026-06-01", "spend": 1200 }, ...]
```

**Progress chart data:**
```json
[{ "name": "Vacation Fund", "pct": 64, "current": 32000, "target": 50000, "remaining": 18000, "daysLeft": 45 }]
```

---

## 6. Switching from Mock to Real DB

1. Set `USE_MOCK_DATA=false` in `.env`
2. Set `DATABASE_URL` to your Neon PostgreSQL connection string
3. Ensure the tables above exist with the correct schema
4. Restart the backend

The chatbot will automatically use the real `DataLayer` instead of `MockDataLayer`.

---

## 7. Performance Characteristics

- **p95 first token latency:** < 1 second (cached contexts + Gemini Flash)
- **p95 full response:** < 5 seconds
- **Concurrent users:** Tested up to 100 VU with Locust
- **Rate limit:** 20 LLM requests/minute per user (configurable)
- **Context cache TTL:** 5 minutes (Redis)
- **Response cache TTL:** 5 minutes per intent (avoids duplicate LLM calls)

---

## 8. Intent Taxonomy

| Intent | Triggers Chart? | Example Queries |
|--------|----------------|-----------------|
| `BALANCE_OVERVIEW` | Pie chart | "How am I doing?", "Financial summary" |
| `SPENDING_QUERY` | Bar chart | "How much on food?", "Transport spend" |
| `BUDGET_STATUS` | None | "Am I over budget?" |
| `GOAL_PROGRESS` | Progress ring | "How's my savings goal?" |
| `ANOMALY_ALERT` | None | "Anything unusual?" |
| `ADVICE_REQUEST` | None | "How to save more?" |
| `COMPARISON_QUERY` | Bar chart | "This month vs last month" |
| `TREND_ANALYSIS` | Line chart | "Spending trend" |
| `ADD_TRANSACTION` | None | "Spent ₹500 at Zomato" |
| `GENERAL_CHAT` | None | Greetings, "Who are you?" |
