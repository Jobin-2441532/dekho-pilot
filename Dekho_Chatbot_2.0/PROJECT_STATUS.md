# Ask Dekho 2.0 — Project Status & Progress

> **Last updated:** 29 June 2026  
> **Module:** Chatbot (standalone AI engine for the Dekho V2 personal finance app)

---

## 1. Project Objective

**Ask Dekho 2.0** is an AI-powered personal finance chatbot built specifically for Indian users. It serves as a standalone, plug-in module that integrates with the main Dekho V2 application.

### Core Goal
Provide users with a conversational, warm, and intelligent financial companion — "Dekho" — that can:
- Summarise monthly spending and financial health
- Answer queries about individual spending categories and budgets
- Track and report progress on savings goals
- Detect and surface unusual/anomalous spending patterns
- Log new transactions via natural language
- Offer personalised, data-driven financial observations (never prescriptive advice)
- Remember user preferences and past sessions across conversations

### Target Audience
Indian consumers using the Dekho V2 personal finance app. The chatbot uses Indian currency formatting (₹), Indian merchant categories (Zomato, Swiggy, IRCTC, Blinkit, etc.), and communicates in a casual, text-message-like tone in English.

### Design Philosophy
- **Observe, don't direct** — Dekho surfaces insights and possibilities. It never tells users what to do.
- **Warm and personal** — Like texting a trusted friend who is good with numbers.
- **Finance-only scope** — Strictly limited to the user's own personal financial data.
- **Progressive disclosure** — Short, clear responses; offers to go deeper on request.

---

## 2. Architecture Overview

```
User message
     │
     ▼
Rate Limiter (20 req/min/user)
     │
     ▼
Response Cache check (5-min TTL per intent)
     │  ← cache hit → return instantly
     ▼
Context Builder → Redis/in-memory (5-min TTL)
     │
     ▼
Intent Detector (LLM few-shot, returns JSON: intent + confidence + slots)
     │
     ▼
Prompt Engine (Master prompt + intent sub-template + cross-session memory + user prefs)
     │
     ▼
LLM Client (Groq primary → OpenRouter fallback → static fallback, streaming, retries)
     │
     ▼
Response Builder (chart data + LLM quick replies + proactive alerts)
     │
     ▼
SSE stream or JSON → React Frontend
```

---

## 3. Tech Stack

### Backend
| Layer | Technology |
|---|---|
| Web Framework | FastAPI 0.115.6 (Python) |
| ASGI Server | Uvicorn (standard) |
| Data Validation | Pydantic v2 + pydantic-settings |
| Primary LLM | Groq (llama-3.1-8b-instant) |
| Fallback LLM | OpenRouter (meta-llama/llama-3.2-3b-instruct:free) |
| LLM SDK | OpenAI Python SDK (openai-compatible API) |
| Session Cache | Redis (optional, gracefully disabled if unavailable) |
| Persistent Storage | SQLite via aiosqlite (production-ready swap to PostgreSQL/asyncpg) |
| Rate Limiting | In-memory token bucket (Redis-backed when available) |
| HTTP Client | httpx |
| Testing | pytest + pytest-asyncio + pytest-httpx |
| Load Testing | Locust (100 VU target) |
| Linting/Format | Ruff + Black |

### Frontend (Test UI)
| Layer | Technology |
|---|---|
| Framework | React 19 + TypeScript |
| Build Tool | Vite 8 |
| State Management | Zustand |
| Streaming | SSE via eventsource-parser |
| Charts | Recharts |
| Animations | Framer Motion |
| Markdown | react-markdown |
| Icons | Lucide React |
| HTTP | Axios |

---

## 4. What Is Built — Detailed Progress

### ✅ 4.1 Backend — Core Pipeline

#### Intent Detection (app/services/intent_detector.py)
- **Status: COMPLETE**
- Classifies user messages into **11 intents** using LLM few-shot prompting:
  - `BALANCE_OVERVIEW`, `SPENDING_QUERY`, `BUDGET_STATUS`, `GOAL_PROGRESS`
  - `ANOMALY_ALERT`, `ADVICE_REQUEST`, `COMPARISON_QUERY`, `TREND_ANALYSIS`
  - `ADD_TRANSACTION`, `OUT_OF_SCOPE`, `GENERAL_CHAT`
- Returns JSON: `{intent, confidence, slots}`
- Extracts **slots** per intent (category, time_period, amount, merchant, goal name)
- Auto-enriches `ADD_TRANSACTION` with merchant-to-category mapping (Zomato → Food & Dining, Uber → Transport, etc.)
- Graceful fallback to `GENERAL_CHAT` on parse error or LLM failure

#### LLM Client (app/services/llm_client.py)
- **Status: COMPLETE**
- Multi-provider waterfall: **Groq (primary) → OpenRouter (fallback)**
- Both providers accessed via the OpenAI-compatible SDK
- Supports **non-streaming** (`generate()`) and **streaming** (`stream()` → AsyncGenerator)
- Per-provider retry logic: up to 2 retries with exponential back-off (1s, 2s)
- Detailed structured logging: provider, model, latency, token count
- Raises `RuntimeError` only when both providers are exhausted (caller handles static fallback)

#### Prompt Engine (app/services/prompt_engine.py)
- **Status: COMPLETE**
- **Master system prompt** encodes the Dekho persona, tone rules, scope boundaries, language rules (₹ formatting, no fabrication), and response format guidelines
- **11 intent-specific sub-instructions** injected per request
- Cross-session memory block (past session summaries from Redis) injected into every prompt
- User preference block injected when available (response style, interests, corrections)
- Conversation history (last 3 turns) injected for continuity
- **Quick Reply Generator**: separate LLM call to generate 3 contextual follow-up suggestions per response (static fallback if LLM fails)
- Chart trigger mapping: intent → chart type (pie / bar / line / progress)

#### Context Builder (app/services/context_builder.py)
- **Status: COMPLETE**
- Assembles `UserFinancialContext` (user profile, monthly snapshot, budgets, goals, anomalies, top expenses)
- **Dual mode**: Mock data (default, USE_MOCK_DATA=true) or live PostgreSQL via async DataLayer
- Result cached per user in Redis (5-minute TTL) to avoid repeated DB reads per session
- Cache invalidation method available for post-transaction refresh

#### Response Builder (app/services/response_builder.py)
- **Status: COMPLETE**
- Assembles the full response package: `text + chart + quick_replies + alert`
- **Chart builders**: pie (spending by category), bar (this month vs last month), line (daily spend trend), progress (goal donut)
- Smart chart suppression: if LLM response indicates "no data available", chart is not attached
- **Proactive alerts** triggered at session start: cashflow alert (>90% income spent), goal deadline urgent (<7 days), budget overrun (>80%), spending anomaly

#### Chat Routes (app/routes/chat.py)
- **Status: COMPLETE**
- `POST /api/chat` — full synchronous response (JSON)
- `POST /api/chat/stream` — SSE streaming response (emits: intent, token, chart_data, quick_replies, alert, done, error events)
- `GET /api/chat/history/{user_id}` — session conversation history
- `GET /api/chat/context/{user_id}` — debug: full user financial context
- `DELETE /api/chat/session/{session_id}` — clear a session (new chat)
- `GET /api/chat/db-history/{user_id}` — full persistent history from SQLite
- `GET /api/chat/last-session/{user_id}` — restore last session on re-login
- `POST /api/chat/feedback` — thumbs up/down + optional correction text
- `GET /api/chat/preferences/{user_id}` — view learned user preferences
- Rate limiting (20 req/min/user) with friendly error message
- Semantic response cache (5-min TTL, skipped for ADD_TRANSACTION)
- Graceful static fallbacks per intent if all LLM providers fail

#### Memory & Session (app/services/memory_store.py, session_summarizer.py)
- **Status: COMPLETE**
- **In-session memory**: stores messages in Redis (or in-memory fallback) with configurable TTL (30 min default)
- **Cross-session memory**: after ≥10 messages, LLM generates a 2–3 sentence session summary stored in Redis (last 3 summaries, 30-day TTL)
- **Pattern extraction**: after summarisation, a second LLM call extracts `topics_of_interest`, `preferred_style`, `common_corrections` and persists to user preferences
- Session summaries are injected into the master prompt for context continuity across logins

#### User Preferences (app/services/preference_manager.py, db_store.py)
- **Status: COMPLETE**
- Auto-detects preference signals from user messages (e.g., "keep it short" → brief style)
- Persists: `response_style` (brief/balanced/detailed), `prefers_charts`, `top_interests`, `corrections`, `disliked_intents`
- Thumbs-down feedback updates `disliked_intents`; correction text is stored and re-injected into future prompts
- Stored in SQLite `user_preferences` table (UPSERT on each session)

#### Persistence — SQLite (app/services/db_store.py)
- **Status: COMPLETE**
- Three tables: `conversations`, `user_preferences`, `feedback`
- Full async reads/writes via `aiosqlite`
- Messages persisted with `user_id`, `session_id`, `role`, `content`, `intent`, `timestamp`
- Architecture comment: designed for easy swap to PostgreSQL/asyncpg in production

#### Caching (app/services/cache.py, response_cache.py)
- **Status: COMPLETE**
- Redis client initialised at startup (gracefully disabled if REDIS_URL not set)
- Helpers: `cache_get`, `cache_set`, `cache_delete`, `cache_lpush`, `cache_lrange`
- Semantic response cache keyed by `user_id + intent` (5-min TTL); skipped for unique intents
- In-memory fallback for all cache operations when Redis is unavailable

#### Rate Limiter (app/services/rate_limiter.py)
- **Status: COMPLETE**
- Token bucket, 20 requests/minute/user
- Redis-backed (sliding window); in-memory fallback

---

### ✅ 4.2 Backend — Data & Schemas

#### Schemas (app/models/schemas.py)
- **Status: COMPLETE**
- Pydantic v2 models: `ChatRequest`, `ChatResponse`, `UserFinancialContext`, `MonthlySnapshot`, `SavingsGoal`, `BudgetAlert`, `SpendingAnomaly`, `TopExpense`, `ChartData`, `AlertPayload`, `ConversationMessage`, `ConversationHistory`

#### Mock Data (data/mock_data.py)
- **Status: COMPLETE**
- Rich mock profiles for 3 test users: Priya, Arjun, Meera
- Each user has: monthly income, spending by category, budgets with alerts, savings goals with deadlines, spending anomalies, top expenses, and 3-month history for trend analysis
- Covers all 11 intent scenarios for testing

---

### ✅ 4.3 Backend — API & Health

#### Health Check (GET /health)
- **Status: COMPLETE**
- Checks Redis connectivity (ping)
- Validates OpenRouter API key is configured
- Validates Groq API key is configured
- Checks DB (or reports mock mode)
- Returns `{ status: "healthy" | "degraded", version, services }`

#### Configuration (app/config.py)
- **Status: COMPLETE**
- All settings via .env (pydantic-settings)
- Key flags: `USE_MOCK_DATA`, `LLM_PROVIDER_PRIMARY`, `LLM_PROVIDER_SECONDARY`
- TTL and rate-limit values configurable without code changes

---

### ✅ 4.4 Frontend — Test UI

#### Chat Shell (src/components/ChatShell.tsx)
- **Status: COMPLETE**
- Header with Dekho branding, user switcher (Priya/Arjun/Meera), debug panel toggle, preset queries toggle, clear chat
- Preset query bar with 8 common finance questions
- Auto-expanding textarea input with Enter-to-send (Shift+Enter for newline)
- Empty state with 4 starter chips
- Alert banner for proactive alerts (dismissible, severity-coloured)

#### Message Bubble (src/components/MessageBubble.tsx)
- **Status: COMPLETE**
- User and bot bubbles with avatar icons
- Bot responses rendered as Markdown via react-markdown
- Streaming cursor animation while tokens arrive
- Transaction confirm card for ADD_TRANSACTION intent
- Inline chart rendering (after streaming completes)
- Quick reply chips (animated in after response)
- Thumbs up / thumbs down feedback bar on every non-fallback bot message
- Correction text input on thumbs-down (sends to backend /feedback endpoint)
- Raw JSON viewer in debug mode

#### Charts (src/components/ChatChart.tsx)
- **Status: COMPLETE**
- Pie chart (spending by category) via Recharts
- Bar chart (this month vs last month comparison)
- Line chart (daily spend trend)
- Progress/donut chart (savings goal completion)

#### State Management (src/store/index.ts)
- **Status: COMPLETE**
- Three Zustand stores: `useChatStore`, `useUserStore`, `useUIStore`
- Per-user conversation persistence in localStorage (serialise/deserialise with timestamp rehydration)
- Session restore from backend DB on user switch (fallback to /last-session)
- Streaming message state: `isStreaming`, `streamingId`, token accumulation

#### SSE / API Client (src/api/)
- **Status: COMPLETE**
- SSE streaming consumer: parses intent, token, chart_data, quick_replies, alert, done, error events
- Feedback submission via REST

---

### ✅ 4.5 Testing

| Test File | Coverage |
|---|---|
| `tests/test_unit.py` | 50+ unit tests — intent detector, prompt engine, response builder, context formatter, rate limiter, cache utilities |
| `tests/test_api.py` | API endpoint tests — /health, /api/chat, /api/chat/stream, /api/chat/history, /api/chat/feedback, session clear |
| `tests/locustfile.py` | Locust load test — 100 VU, 10 VU/s ramp, 5-minute duration, exercises all endpoints |
| `smoke_test.py` | Quick real-API smoke test (requires running server + API keys) |
| `quick_test.py` | Rapid local sanity check |

---

### ✅ 4.6 Documentation

| Document | Status |
|---|---|
| `README.md` | ✅ Quick-start, architecture diagram, test commands |
| `docs/integration-guide.md` | ✅ Full API reference for the main Dekho V2 team |
| `Tech Stack Options.md` | ✅ LLM provider evaluation and selection rationale |
| `ask_dekho_llm_transition_openrouter_groq.md` | ✅ Migration notes (Gemini → OpenRouter/Groq transition) |
| `Response representation.md` | ✅ Detailed response format spec and examples |
| `tech_stack_doc.md` | ✅ Full tech stack documentation |
| `Dekho_Updated_Product_Definition.pdf` | ✅ Product definition source document |

---

## 5. Current State Summary

| Component | Status | Notes |
|---|---|---|
| Intent Detection | ✅ Complete | 11 intents, slot extraction, merchant category mapping |
| LLM Client | ✅ Complete | Groq primary, OpenRouter fallback, streaming + non-streaming |
| Prompt Engine | ✅ Complete | Persona, 11 sub-prompts, memory injection, preferences |
| Context Builder | ✅ Complete | Mock mode + live DB mode stub, Redis cache |
| Response Builder | ✅ Complete | 4 chart types, proactive alerts, LLM quick replies |
| Chat Routes | ✅ Complete | 9 REST endpoints + SSE stream |
| Memory (in-session) | ✅ Complete | Redis / in-memory, last 6 turns injected |
| Memory (cross-session) | ✅ Complete | LLM summarisation, 3 sessions stored in Redis |
| User Preferences | ✅ Complete | Auto-detected + feedback-updated + prompt-injected |
| SQLite Persistence | ✅ Complete | Conversations + preferences + feedback tables |
| Caching | ✅ Complete | Redis + in-memory fallback |
| Rate Limiting | ✅ Complete | 20 req/min/user |
| Mock Data | ✅ Complete | 3 users, all intent scenarios covered |
| Frontend Test UI | ✅ Complete | SSE streaming, charts, feedback, user switcher, debug panel |
| Unit Tests | ✅ Complete | 50+ tests |
| API Tests | ✅ Complete | All endpoints covered |
| Load Tests | ✅ Complete | 100 VU Locust script |
| Health Endpoint | ✅ Complete | Redis + LLM + DB checks |
| Documentation | ✅ Complete | README, integration guide, product docs |

---

## 6. Known Limitations / What Is Not Yet Done

| Item | Detail |
|---|---|
| **Live DB integration** | `USE_MOCK_DATA=true` by default. The `DataLayer` class stub exists and `context_builder.py` has the live path wired, but the actual Neon PostgreSQL schema and queries need connecting to the real V2 app database. |
| **Bar chart "last month" data** | Currently mocked as 90% of this month's values. Real historical data from the V2 DB is needed for accurate comparison. |
| **Line chart daily data** | Daily spend trend uses random simulation around the monthly average. Real per-day transaction aggregates are needed. |
| **Authentication / JWT** | The chatbot accepts `user_id` as a plain string. JWT-based auth (via `python-jose`, already in requirements.txt) is not yet wired into middleware. The main V2 app is expected to pass a validated `user_id` during integration. |
| **Redis in production** | Redis is optional (graceful in-memory fallback). A production Redis instance should be configured for cross-session memory and response caching at scale. |
| **ADD_TRANSACTION persistence** | The chatbot confirms transactions in conversation but does not write new transactions back to the V2 main database. This is intentional (read-only architecture); the V2 app handles writes. |
| **Preference signal coverage** | `preference_manager.py` detects a small set of keywords. This can be expanded as real usage patterns are observed. |

---

## 7. Next Steps / Roadmap

1. **Live DB Connection** — Wire `DataLayer` to the Neon PostgreSQL schema used by the main V2 app. Set `USE_MOCK_DATA=false` in production.
2. **Authentication Middleware** — Validate JWT tokens passed from the V2 app; map token claims to `user_id`.
3. **Real Historical Data** — Replace the bar and line chart mock data with real aggregated queries.
4. **Transaction Write-back** — Decide whether the chatbot should write `ADD_TRANSACTION` entries directly or delegate to the V2 API.
5. **Production Redis** — Configure a managed Redis instance (e.g., Upstash) for persistent caching and cross-session memory at scale.
6. **CI/CD Pipeline** — Set up GitHub Actions for automated test runs on push.
7. **Observability** — Integrate structured logging with a platform (e.g., Datadog, Sentry) for production monitoring.
8. **Embedding in Main V2 App** — Follow the integration guide in `docs/integration-guide.md` to embed the chatbot widget into the main Dekho V2 React application.
