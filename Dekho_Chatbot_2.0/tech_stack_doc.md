# Ask Dekho 2.0 — Tech Stack Documentation

> **Purpose**: A reference map of every technology currently used in Ask Dekho 2.0, what role it plays, and what areas to research for potential upgrades or alternatives.

---

## Architecture Overview

```
┌────────────────────────────┐      HTTP / SSE       ┌────────────────────────────────┐
│      Frontend (Browser)    │ ◄──────────────────── │     Backend (Python)           │
│  React 19 + Vite + Zustand │ ──────────────────────►  FastAPI + Uvicorn             │
└────────────────────────────┘                       └────────────┬───────────────────┘
                                                                  │
                         ┌────────────────────────────────────────┤
                         │                                        │
                 ┌───────▼────────┐                    ┌──────────▼──────────┐
                 │  Redis Cache   │                    │  LLM APIs            │
                 │  (Session Mem) │                    │  Gemini / OpenAI     │
                 └────────────────┘                    └─────────────────────┘
                         │
                 ┌───────▼────────┐
                 │  PostgreSQL DB │
                 │  (User Data)   │
                 └────────────────┘
```

---

## 1. Frontend

| Technology | Version | Purpose | Research Direction |
|---|---|---|---|
| **React** | 19.x | Core UI framework — component tree, rendering, hooks | Explore React Server Components for SSR; consider SolidJS/Svelte for lighter bundle |
| **TypeScript** | ~6.0 | Static typing across all frontend code | Already on latest; explore `strict` mode fully |
| **Vite** | 8.x | Build tool & dev server (ESM-native, HMR) | Alternative: Turbopack (Next.js) for monorepo scenarios |
| **Zustand** | 5.x | Lightweight global state management (chat, user, UI stores) | Alternatives: Jotai (atomic), TanStack Query (server state), Redux Toolkit |
| **Axios** | 1.x | HTTP client for non-streaming REST calls | Alternative: native `fetch` + TanStack Query for caching |
| **eventsource-parser** | 3.x | Parses SSE (Server-Sent Events) token stream from the backend | Alternative: native `EventSource` API (no parser needed if using standard SSE) |
| **Framer Motion** | 12.x | Animations — message entry, typing indicator, transitions | Alternative: React Spring (physics-based), CSS animations (zero JS) |
| **Lucide React** | 1.x | Icon library (Send, Trash2, Bug, ChevronDown icons) | Alternatives: Heroicons, Radix Icons, Phosphor Icons |
| **react-markdown** | 10.x | Renders markdown in LLM response bubbles | Alternative: marked.js (raw), MDX for interactive content |
| **Recharts** | 3.x | Data visualization — pie, bar, line, progress charts in chat | Alternatives: Victory, Chart.js, D3.js (lower-level), Nivo |
| **Vanilla CSS** | — | All styling — design tokens (`--bg-base`, etc.), layout, animations | Alternative: CSS Modules, Styled Components, Tailwind CSS |

### Frontend File Structure

```
chatbot-frontend/src/
├── App.tsx              # Root component, layout, scroll management
├── index.css            # Global styles + design token variables
├── main.tsx             # React DOM entry point
├── store/index.ts       # Zustand stores: ChatStore, UserStore, UIStore
├── api/                 # Axios / SSE API call wrappers
├── hooks/useChatStream.ts  # SSE streaming logic hook
└── components/
    ├── ChatShell.tsx    # Header, InputBar, PresetQueries, DebugPanel, AlertBanner
    ├── MessageBubble.tsx # User/assistant message rendering
    ├── ChatChart.tsx    # Recharts wrapper for inline data viz
    ├── RichComponents.tsx # Budget bars, goal cards, anomaly cards
    └── TypingIndicator.tsx # Animated "thinking" indicator
```

---

## 2. Backend

| Technology | Version | Purpose | Research Direction |
|---|---|---|---|
| **Python** | 3.13+ | Primary backend language | Explore 3.13 free-threaded mode for true async performance |
| **FastAPI** | 0.115.x | Async REST API framework — routes, request validation, CORS | Alternatives: Litestar (newer, faster), Django Ninja, Flask |
| **Uvicorn** | 0.32.x | ASGI server that runs FastAPI (`uvicorn[standard]` for WebSocket support) | Alternatives: Hypercorn (HTTP/2), Gunicorn+Uvicorn workers for production |
| **Pydantic v2** | 2.10.x | Data validation & schema enforcement for all API models and settings | Already on v2 (fast Rust core); explore `model_serializer` for custom output |
| **pydantic-settings** | 2.7.x | Loads `.env` config into typed `Settings` class | Part of Pydantic ecosystem — no direct alternative needed |
| **SQLAlchemy (async)** | 2.0.x | ORM/query layer for PostgreSQL (async mode with `asyncpg`) | Alternatives: Tortoise ORM, SQLModel (Pydantic + SQLAlchemy), raw asyncpg |
| **asyncpg** | 0.30.x | Native async PostgreSQL driver (used by SQLAlchemy[asyncio]) | Alternative: psycopg3 (newer, also async-native) |
| **redis[asyncio]** | ≥5.0 | Async Redis client (redis-py, chosen over aioredis which broke on Python 3.13) | Alternatives: Upstash SDK (serverless Redis), Valkey (open-source Redis fork) |
| **httpx** | 0.28.x | Async HTTP client (used for external API calls if needed) | Alternative: aiohttp; httpx is already the modern standard |
| **python-jose** | 3.3.x | JWT token creation/verification (auth layer) | Alternatives: PyJWT, joserfc |
| **python-dotenv** | 1.0.x | Loads `.env` file into environment (supplementary to pydantic-settings) | Already handled by pydantic-settings; this is mostly redundant |

### Backend Service Architecture

```
chatbot-backend/app/
├── main.py              # FastAPI app init, CORS, lifespan (Redis connect/disconnect)
├── config.py            # Pydantic Settings — all env vars typed & validated
├── routes/
│   └── chat.py          # All chat endpoints (POST /chat, POST /chat/stream, GET /history, DELETE /session)
├── models/
│   └── schemas.py       # All Pydantic schemas: ChatRequest, ChatResponse, UserFinancialContext, etc.
├── services/
│   ├── llm_client.py    # Unified Gemini + OpenAI wrapper (streaming + non-streaming)
│   ├── intent_detector.py  # LLM-based intent classification (10 intents, few-shot)
│   ├── prompt_engine.py # Assembles system prompt from context + intent template
│   ├── context_builder.py  # Builds UserFinancialContext from DB or mock data
│   ├── response_builder.py # Assembles final response: text + chart + quick replies + alert
│   ├── memory_store.py  # Session conversation history in Redis
│   ├── cache.py         # Redis async connection pool + get/set/lpush helpers
│   ├── response_cache.py   # Semantic response cache (intent-level caching per user)
│   ├── rate_limiter.py  # 20 requests/minute per user (Redis-based sliding window)
│   └── session_summarizer.py  # Auto-summarizes completed sessions for cross-session memory
└── utils/
    └── formatters.py    # INR formatting, percentage, days formatting helpers
```

---

## 3. AI / LLM Layer

| Technology | Version | Purpose | Research Direction |
|---|---|---|---|
| **Google Gemini 1.5 Flash** | via `google-genai ≥1.0` | Primary LLM — intent classification + response generation | Upgrade path: Gemini 2.0 Flash, Gemini 1.5 Pro (higher quality), Gemini 2.5 Pro |
| **OpenAI GPT-4o-mini** | via `openai 1.59` | Secondary/fallback LLM provider | Alternatives: GPT-4o, Claude Haiku/Sonnet, Llama 3 (self-hosted) |
| **LLM-based Intent Detection** | custom | Few-shot JSON classification of user queries into 10 financial intents | Alternatives: fine-tuned classifier (BERT/DistilBERT), rule-based NLU (Rasa), dedicated NLU service (Dialogflow, Wit.ai) |
| **Prompt Engineering** | custom | Master system prompt + 10 intent-specific sub-prompts for persona + data injection | Research: LangChain prompt templates, structured output (Pydantic + Instructor library), DSPy |
| **Streaming (SSE)** | native | Token-by-token streaming from LLM via Server-Sent Events | Alternatives: WebSockets (bidirectional), gRPC streaming |

### LLM Pipeline Flow
```
User Message
    │
    ▼
Intent Detection (LLM call — low temperature 0.1, JSON output, 200 tokens)
    │
    ▼
Context Build (UserFinancialContext from DB/mock)
    │
    ▼
Prompt Assembly (Master Prompt + intent-specific instruction + financial context + history)
    │
    ▼
LLM Generation (Gemini Flash / GPT-4o-mini — stream or non-stream)
    │
    ▼
Response Package (text + chart data + quick replies + alert)
    │
    ▼
SSE emit to frontend
```

---

## 4. Data Storage

| Technology | Deployment Target | Purpose | Research Direction |
|---|---|---|---|
| **PostgreSQL** | Neon (serverless, cloud) | Primary persistent storage — user profiles, transactions, budgets, goals, session summaries | Alternatives: PlanetScale (MySQL), Supabase (Postgres + auth), CockroachDB (distributed) |
| **Redis** | Upstash (serverless, free tier) / local | In-session conversation memory (list per session\_id), semantic response cache, rate limiting counters | Alternatives: DragonflyDB (Redis-compatible, faster), Valkey, Momento (serverless cache) |

### Memory Architecture
```
In-Session Memory (Redis list, TTL: 30 min):
  key: "sess:{session_id}:messages"
  value: JSON messages, max 20 entries (lpush + ltrim)

Response Cache (Redis, TTL: 5 min):
  key: "cache:{user_id}:{intent}"
  value: full response JSON (skips LLM for repeated queries)

Rate Limiter (Redis counter, TTL: 60s):
  key: "rl:{user_id}"
  value: request count, max 20/min

Cross-Session Memory (PostgreSQL):
  table: session_summaries
  value: LLM-generated summary per completed session
```

---

## 5. Developer Tooling

| Technology | Version | Purpose | Research Direction |
|---|---|---|---|
| **pytest** | 8.3.x | Unit/integration testing framework | Add pytest-cov for coverage, hypothesis for property-based tests |
| **pytest-asyncio** | 0.25.x | Async test support for FastAPI/asyncpg tests | Standard choice; no direct alternative needed |
| **pytest-httpx** | 0.35.x | Mock httpx calls in tests | Alternative: respx |
| **Locust** | 2.32.x | Load/performance testing (how the backend handles concurrent users) | Alternatives: k6, Artillery, Gatling |
| **Black** | 24.10.x | Python code auto-formatter | Alternative: Ruff's formatter (ruff format), which is faster |
| **Ruff** | 0.8.x | Fast Python linter (replaces Flake8 + isort + many others) | Already state-of-the-art; just keep updated |
| **ESLint** | 10.x | JavaScript/TypeScript linting | Alternative: Biome (Rust-based, faster, also formats) |
| **TypeScript ESLint** | 8.x | TypeScript-specific ESLint rules | Standard pairing with ESLint |

---

## 6. Communication Protocols

| Protocol | Used For | Research Direction |
|---|---|---|
| **REST (HTTP/JSON)** | Non-streaming chat (`POST /api/chat`), history, session management | Standard; no change needed |
| **Server-Sent Events (SSE)** | Token streaming from LLM (`POST /api/chat/stream`) | Alternative: WebSockets (bidirectional, but more complex); GraphQL subscriptions |
| **CORS** | Cross-origin requests from frontend (localhost:5173) to backend (localhost:8001) | Production: lock down `allowed_origins` to specific domains |

---

## 7. Configuration & Environment

| Item | Tech Used | Details |
|---|---|---|
| **Backend config** | pydantic-settings + `.env` | Typed settings: LLM provider/model/keys, DB URL, Redis URL, rate limits, TTLs |
| **Frontend config** | `.env` (Vite) | `VITE_API_URL` — backend base URL |
| **Feature flags** | `USE_MOCK_DATA=true` in `.env` | Bypasses real DB; uses hardcoded mock financial data for chatbot-only dev |
| **LLM provider toggle** | `LLM_PROVIDER=gemini\|openai` | Switches between Gemini Flash and GPT-4o-mini at runtime |

---

## 8. Key Patterns & Design Decisions

| Pattern | Implementation | Why It Matters |
|---|---|---|
| **Intent-based routing** | LLM classifies into 10 fixed intents → maps to specific prompt template | Gives the LLM a narrow, well-defined task per query; improves accuracy |
| **Context injection** | `UserFinancialContext` struct serialized into every LLM prompt | LLM never "hallucinates" numbers — all ₹ figures come from real DB data |
| **Streaming UX** | SSE token-by-token delivery; frontend accumulates in Zustand message state | Perceived performance — user sees response immediately, not after full generation |
| **Semantic caching** | Responses cached by `{user_id}:{intent}` for 5 minutes | Saves LLM API cost for repeated queries like "show my balance" |
| **Rate limiting** | Redis sliding window, 20 req/min per user | Protects LLM quota and backend from abuse |
| **Session auto-summary** | Background `asyncio.create_task` summarizes session after completion | Enables cross-session memory without storing full history indefinitely |
| **Fallback responses** | Per-intent static fallback text on LLM timeout/error | Prevents blank/error screens; maintains conversational UX |
| **Mock data mode** | `USE_MOCK_DATA=true` serves hardcoded user financial profiles | Enables full frontend/chatbot development without a live DB |

---

## 9. Current Gaps / Areas to Research

> [!IMPORTANT]
> These are areas where the current stack has known limitations worth researching.

| Gap | Current State | Research Directions |
|---|---|---|
| **No vector DB / semantic search** | Keyword/intent matching only | Pinecone, Weaviate, pgvector (Postgres extension), ChromaDB for semantic transaction search |
| **LLM intent detection latency** | ~300–700ms per classification call | Fine-tuned small classifier (DistilBERT), local model (Ollama + Llama 3), or rule-based pre-filter |
| **No authentication system** | `user_id` is hardcoded in frontend (mock users) | JWT + refresh tokens (python-jose already installed), Supabase Auth, Auth0, Firebase Auth |
| **No real DB integration** | `USE_MOCK_DATA=true` in `.env`; `DataLayer` class stub exists | Connect Neon PostgreSQL; implement SQLAlchemy async queries for transactions, budgets, goals |
| **No observability / monitoring** | Python `logging` only | OpenTelemetry + Jaeger/Grafana, Sentry (errors), Langfuse (LLM tracing), Prometheus metrics |
| **Cross-session memory is stub** | `session_summarizer.py` exists but may not persist to DB | Implement summary storage in PostgreSQL; retrieve on session start |
| **No CI/CD pipeline** | Manual `uvicorn` + `npm run dev` | GitHub Actions, Docker + docker-compose, Railway/Render/Fly.io deployment |
| **No WebSocket support** | SSE is one-directional | Consider WebSockets for bidirectional features (typing indicators, push alerts) |
| **Bundle size** | Framer Motion is large (~100KB gzipped) | Consider Motion One (lighter), or CSS-only animations for simple effects |

---

## 10. Dependency Quick Reference

### Backend (`requirements.txt`)
```
fastapi==0.115.6          # API framework
uvicorn[standard]==0.32.1 # ASGI server
pydantic==2.10.4          # Data validation
pydantic-settings==2.7.0  # Env config
sqlalchemy[asyncio]==2.0.36 # ORM
asyncpg==0.30.0           # PostgreSQL async driver
redis[asyncio]>=5.0.0     # Redis async client
google-genai>=1.0.0       # Gemini LLM SDK
openai==1.59.7            # OpenAI LLM SDK
python-dotenv==1.0.1      # .env loader
httpx==0.28.1             # Async HTTP client
python-jose[cryptography]==3.3.0 # JWT auth
pytest==8.3.4             # Testing
pytest-asyncio==0.25.0    # Async test support
pytest-httpx==0.35.0      # HTTP mock for tests
locust==2.32.4            # Load testing
black==24.10.0            # Code formatter
ruff==0.8.6               # Linter
```

### Frontend (`package.json`)
```json
"dependencies": {
  "axios": "^1.17.0",           // HTTP client
  "eventsource-parser": "^3.1.0", // SSE stream parsing
  "framer-motion": "^12.40.0",  // Animations
  "lucide-react": "^1.18.0",    // Icons
  "react": "^19.2.6",           // UI framework
  "react-dom": "^19.2.6",       // DOM renderer
  "react-markdown": "^10.1.0",  // Markdown rendering
  "recharts": "^3.8.1",         // Data charts
  "zustand": "^5.0.14"          // State management
},
"devDependencies": {
  "typescript": "~6.0.2",       // Type system
  "vite": "^8.0.12",            // Build tool
  "@vitejs/plugin-react": "^6.0.1", // Vite React plugin
  "eslint": "^10.3.0"           // Linter
}
```
