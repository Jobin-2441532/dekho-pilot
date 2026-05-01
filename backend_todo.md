# Dekho Backend — Architecture TODO List

> Based on `dekho_architecture.md` gap analysis (2026-04-29). ~65% aligned.

---

## Current State Summary

| Layer | Status |
|---|---|
| FastAPI + Uvicorn | ✅ Running |
| PostgreSQL (via Docker) | ✅ Running |
| MinIO (file storage) | ✅ Running |
| Redis + Celery | ✅ Set up |
| JWT Auth (register/login/refresh) | ✅ Implemented |
| File Upload (PDF/CSV parsing) | ✅ Implemented |
| SMS Paste & Parsing | ✅ Implemented |
| Normalization Service | ✅ Implemented |
| Feature Layer (monthly/weekly/profile) | ✅ Implemented |
| Chatbot (Gemini + FAISS RAG) | ✅ Implemented |
| User Isolation (JWT on data endpoints) | ❌ Built but NOT wired |
| Transactions table (ML-ready schema) | ❌ Thin — missing 15+ columns |
| merchant_mappings table | ❌ Missing |
| feedback_logs table | ❌ Missing |
| ML Models (Categorize, Behavior, Recommend) | ⏳ Parked (Phase 5) |
| Frontend Integration | ❌ Not started |

---

## Phase 0 — Architecture Gap Fixes (from gap_analysis.md)

> These gaps were identified by comparing the running backend to `dekho_architecture.md`.
> Execute in priority order before resuming Phase 11 onwards.

### 0.1 — 🔴 Critical: Wire User Isolation (JWT) on All Data Endpoints
- `[x]` Import `get_current_user` into `dashboard.py` — protect all routes
- `[x]` Import `get_current_user` into `features.py` — protect all routes
- `[ ]` Import `get_current_user` into `ingestion.py` — protect all routes
- `[x]` Replace all `db.query(User).first()` with `current_user` from JWT dependency
- `[x]` Replace all hardcoded `user_id=1` with `current_user.id`
- `[x]` Wire user isolation into `chat.py` chatbot endpoint

### 0.2 — 🔴 Critical: Expand Transactions Table Schema
- `[x]` Add `vpa` column (UPI VPA e.g. `zomato@upi`)
- `[x]` Add `bank` column
- `[x]` Add `account_ref` column
- `[x]` Add `sub_category` column
- `[x]` Add `confidence` column (ML confidence score 0.0–1.0)
- `[x]` Add `review_status` column (`pending` / `reviewed` / `auto_assigned`)
- `[x]` Add `is_recurring` boolean column
- `[x]` Add `is_refund` boolean column
- `[x]` Add `is_cashback` boolean column
- `[x]` Add `is_income` boolean column
- `[x]` Add `net_amount` column (amount after refund/cashback)
- `[x]` Add `tags` column (comma-separated: recurring, refund, p2p)
- `[x]` Add `currency` column (default `INR`)
- `[x]` Run Alembic migration

### 0.3 — 🔴 Critical: Fix raw_records Table
- `[x]` Add `user_id` FK column to `raw_records`
- `[x]` Add `parsed_status` column (`pending` / `processed` / `unrecognised`)
- `[x]` Add `raw_data` column (for SMS text — currently only `raw_text`)
- `[x]` Run Alembic migration

### 0.4 — 🟡 Important: Add merchant_mappings Table (needed for Phase 5 ML)
- `[x]` Create `merchant_mappings` model (user_id, merchant_key, category, sub_category, confidence_override, usage_count)
- `[x]` Add UNIQUE constraint on (user_id, merchant_key)
- `[x]` Run Alembic migration
- `[x]` Expose `GET /api/v1/feedback/merchant-mappings` endpoint

### 0.5 — 🟡 Important: Add feedback_logs Table (needed for Phase 5 ML)
- `[x]` Create `feedback_logs` model (user_id, transaction_id, original_category, corrected_category, original_confidence)
- `[x]` Run Alembic migration
- `[x]` Expose `POST /api/v1/feedback/correct` endpoint (user corrects a category)
- `[x]` Expose `GET /api/v1/feedback/stats` endpoint

### 0.6 — 🟡 Important: Missing Write Endpoints
- `[x]` `POST /api/v1/dashboard/goals` — create a new savings goal
- `[x]` `POST /api/v1/dashboard/profile/budget` — update monthly budget limit
- `[x]` `GET /api/v1/review/queue` — transactions pending user review

### 0.7 — 🟢 Nice-to-have: Missing User Columns
- `[ ]` Add `phone` to `users` table
- `[ ]` Add `is_active` boolean to `users` table
- `[ ]` Add `user_type` (student/working/freelancer/business) to `users`
- `[ ]` Add `shopping_behavior` and `food_habit` to `users`
- `[ ]` Run Alembic migration

### 0.8 — 🟢 Nice-to-have: Insights Endpoints
- `[ ]` `GET /api/v1/insights/recurring` — recurring expenses list from FeatureService
- `[ ]` `GET /api/v1/insights/top-merchants` — top merchants by spend
- `[ ]` `GET /api/v1/insights/monthly-summary` — income/expense/savings for month

### 0.9 — 🟢 Post Phase 5: Advanced Tables
- `[ ]` Create `recurring_expenses` table (detected subscription/EMI patterns)
- `[ ]` Create `split_groups` table (bill splitting)
- `[ ]` Create `wallet_floats` table (digital wallet tracking)
- `[ ]` Create `social_contacts` table (known UPI VPAs)
- `[ ]` Create `user_salary_profiles` table

---


## Phase 1 — Data Ingestion

### 1.1 Upload API
- `[x]` Create `POST /upload` endpoint accepting `multipart/form-data`
- `[ ]` Store uploaded files in MinIO (or local folder for prototype)
- `[x]` Save file metadata to `uploaded_files` table in DB(filename, size, type, upload time, user_id)
- `[ ]` Return a file ID on successful upload

### 1.2 PDF Parsing
- `[x]` Implement a PDF parser using `pdfplumber` to extract transaction rows
- `[x]` Handle common Indian bank statement formats (HDFC, SBI, ICICI)
- `[x]` Extract: date, merchant/description, amount, debit/credit direction

### 1.3 CSV Parsing
- `[x]` Implement a CSV parser using `pandas`
- `[x]` Handle multiple column formats (UPI exports, bank statement CSVs)
- `[x]` Extract same fields as PDF parser

### 1.4 SMS Paste Input
- `[x]` Create `POST /sms/paste` endpoint to accept raw SMS text
- `[x]` Store raw SMS in `raw_sms_messages` table
- `[x]` Create `POST /sms/parse` endpoint to trigger parsing
- `[x]` Create `GET /sms/history` endpoint
- `[x]` Build SMS regex parser for common Indian bank SMS formats:
  - `[x]` Debit alerts: `debited by INR X at MERCHANT`
  - `[x]` Credit alerts: `credited with INR X`
  - `[x]` UPI: `UPI payment of INR X to MERCHANT`

### 1.5 Raw Records Storage
- `[x]` Store all parsed rows in `raw_records` table before normalization
- `[x]` Each raw record links back to its source file or SMS ID

---

## Phase 2 — Database Overhaul

### 2.1 Schema Migration (SQLite → PostgreSQL)
- `[x]` Install and configure PostgreSQL locally
- `[x]` Install `psycopg2` and `SQLAlchemy` (async) and add to `requirements.txt`
- `[x]` Install `Alembic` for migrations
- `[x]` Create `alembic.ini` and migration environment

### 2.2 Raw Data Layer Tables
- `[x]` Create `uploaded_files` table
- `[x]` Create `raw_records` table (links to uploaded file, stores unparsed row)
- `[ ]` Create `raw_sms_messages` table (stores raw SMS text with timestamp)

### 2.3 Canonical Finance Layer Tables
- `[/]` Expand `transactions` table with new columns:
  - `[x]` `direction` (credit/debit)
  - `[x]` `payment_mode`
  - `[x]` `source_type` (pdf, csv, sms)
  - `[x]` `source_reference_id`
  - `[ ]` `category_id` (FK to categories)
- `[ ]` Create `accounts` table (id, user_id, bank_name, account_type, balance)
- `[ ]` Create `categories` table (id, name, parent_category)
- `[x]` Create `assets` table (id, user_id, type, value) — replace hardcoded mock
- `[ ]` Create `sms_parsed_transactions` table (id, raw_sms_id, extracted fields, parse_confidence, mapped_transaction_id)

### 2.4 Feature Layer Tables
- `[ ]` Create `monthly_features` table (user_id, month, total_spend, category_ratio JSON, savings_rate, income_estimate)
- `[ ]` Create `weekly_features` table (user_id, week, spend JSON)
- `[ ]` Create `user_financial_profile` table (user_id, recurring_expenses JSON, spending_pattern JSON)

### 2.5 Output Layer Tables
- `[ ]` Create `model_predictions` table (user_id, model_name, output JSON, created_at)
- `[ ]` Create `insights` table (user_id, type, text, created_at)
- `[x]` Create `recommendations` table (user_id, title, description, cta, tag, created_at)
- `[ ]` Create `chat_context` table (user_id, session_id, context_snapshot JSON)

---

## Phase 3 — Data Normalization

- `[x]` Build a `NormalizationService` that converts raw parsed rows into canonical `transactions` records
- `[x]` Normalize merchant names (strip UPI IDs, standardize vendor names)
- `[x]` Map transaction direction from raw text (`debited` → debit, `credited` → credit)
- `[x]` Normalize timestamps to a standard UTC format
- `[x]` Auto-assign a default `category_id` during normalization (pre-ML fallback)
- `[ ]` Trigger normalization automatically after parsing (via Celery task or inline call)

---

## Phase 4 — Feature Layer

- `[x]` Create `FeatureService` class to compute and store reusable metrics
- `[x]` Implement `compute_monthly_features(user_id, month)`:
  - `[x]` Total spend
  - `[x]` Category distribution ratios
  - `[x]` Savings rate
  - `[x]` Income estimate
  - `[x]` Recurring expense list
- `[x]` Implement `compute_weekly_features(user_id, week)`
- `[x]` Implement `compute_user_profile(user_id)`:
  - `[x]` Spending patterns over time
  - `[x]` SMS-derived transaction patterns
- `[ ]` Schedule feature recomputation after every new batch of transactions
- `[x]` Expose `GET /features/monthly` and `GET /features/profile` endpoints

---

## Phase 5 — ML Model Integration

### 5.1 Auto-Categorization Model
- `[ ]` Build `POST /ml/categorize` endpoint
- `[ ]` Define feature contract: merchant_name, description, amount, timestamp, historical_category_patterns
- `[ ]` Implement rule-based categorization as baseline (keyword matching on merchant names)
- `[ ]` Add ML-based categorization (zero-shot or fine-tuned classifier) as upgrade path
- `[ ]` Store predicted category back into the `transactions` table
- `[ ]` Allow user override of predicted category

### 5.2 Behavior Model (Monthly Wrap)
- `[ ]` Build `POST /ml/behavior` endpoint
- `[ ]` Define feature contract: category_spend_distribution, weekly/monthly trends, recurring transactions, spending spikes
- `[ ]` Generate curated narrative insights from behavior analysis
- `[ ]` Structure outputs for storytelling-style Monthly Wrap UI visualization
- `[ ]` Each insight to include a reference/navigation link for drill-down pages

### 5.3 Opportunity / Recommendation Model
- `[ ]` Build `POST /ml/recommend` endpoint
- `[ ]` Define feature contract: income_estimate, savings_rate, expense_ratio, goal_progress, asset_data
- `[ ]` Generate: investment suggestions, savings recommendations
- `[ ]` Replace hardcoded `/opportunities` mock data with dynamic model outputs
- `[ ]` Store recommendations in `recommendations` table

### 5.4 Feature Access Pattern — Enforce "No Direct DB Access" Rule
- `[ ]` Refactor all ML endpoints to fetch data exclusively via `FeatureService`
- `[ ]` Never pass raw DB rows directly to ML models
- `[ ]` Validate model input payload against Pydantic schemas before inference

---

## Phase 6 — Background Job Infrastructure

- `[x]` Install `Celery` and `Redis`, add to `requirements.txt`
- `[x]` Create `celery_app.py` with broker configuration
- `[x]` Move parsing tasks to Celery background jobs:
  - `[x]` PDF/CSV parsing task
  - `[x]` SMS parsing task
  - `[x]` Feature recomputation task
  - `[ ]` ML inference task (deferred — Phase 5)
- `[x]` Add job status tracking (PENDING, RUNNING, DONE, FAILED)
- `[x]` Expose `GET /jobs/{job_id}/status` endpoint for frontend polling

---

## Phase 7 — File Storage (MinIO)

- `[x]` Install and run MinIO locally (Docker)
- `[x]` Install `minio` Python SDK, add to `requirements.txt`
- `[x]` Create `FileStorageService` to handle upload/download/delete
- `[x]` Store all uploaded PDFs/CSVs in MinIO (with local filesystem fallback)
- `[x]` Never expose raw file URLs publicly — generate signed URLs with expiry
- `[x]` Design storage path: `user_{id}/uploads/{file_id}.pdf`

---

## Phase 8 — Chatbot Integration

- `[x]` Refactor `chat.py` to pull data from feature layer (not isolated mock)
- `[x]` Build `ChatContextService`:
  - `[x]` Pull user's financial profile from feature layer
  - `[x]` Attach recent insights and recommendations
  - `[x]` Include recent transaction summary
- `[x]` Pass enriched context to Gemini in the system prompt
- `[ ]` Ensure chatbot only accesses the requesting user's data (blocked on Phase 10)
- `[ ]` Store each chat session's context snapshot in `chat_context` table

---

## Phase 9 — API Layer Completion

- `[x]` Review all existing endpoints for hardcoded mock data and replace with DB queries:
  - `[x]` `/assets` — DB-backed
  - `[x]` `/opportunities` — DB-backed
  - `[x]` `/profile` — `monthlyIncome` derived from `income_range` band
- `[x]` Add missing endpoints per architecture spec:
  - `[x]` `GET /files` — list uploaded files for a user
  - `[x]` `GET /transactions/summary` — period-based aggregate
  - `[x]` `GET /features/monthly`
  - `[x]` `GET /features/profile`
  - `[ ]` `POST /ml/categorize` — deferred (Phase 5)
  - `[ ]` `POST /ml/behavior` — deferred (Phase 5)
  - `[ ]` `POST /ml/recommend` — deferred (Phase 5)
  - `[x]` `POST /sms/paste`
  - `[x]` `GET /sms/history`
  - `[x]` `POST /sms/parse`
- `[x]` Add pagination to `GET /transactions`
- `[x]` Add date range filtering to `GET /transactions`

---

## Phase 10 — Authentication & Authorization

- `[x]` Install `python-jose` and `passlib`, add to `requirements.txt`
- `[x]` Implement JWT-based auth:
  - `[x]` `POST /auth/register`
  - `[x]` `POST /auth/login` — returns access token
  - `[x]` `POST /auth/refresh`
- `[x]` Create `get_current_user` dependency for protected routes
- `[ ]` Enforce `user_id` filtering on ALL data endpoints (next step)
- `[x]` Hash passwords with bcrypt before storing

---

## Phase 11 — Security Hardening

- `[x]` Add input validation for all upload endpoints (file type whitelist: PDF/CSV only, 10 MB size limit)
- `[x]` Sanitize SMS text before parsing (strips HTML tags, scripts, control characters, truncates to 2000 chars)
- `[x]` Mask sensitive identifiers in API responses (account numbers → `XXXX1234`, VPAs → `j*****e@okaxis`)
- `[x]` Rate-limit upload and parsing endpoints (10 uploads/min, 20 SMS/min per IP via `slowapi`)
- `[x]` Tighten CORS policy — explicit origin whitelist, explicit method and header lists
- `[x]` Never return raw file paths or MinIO bucket keys in API responses
- `[x]` Feature contract enforcement utility (`build_ml_payload`) strips internal fields before ML consumption
- `[x]` Wire JWT `get_current_user` into all ingestion endpoints (upload, SMS paste/parse/history)
- `[x]` JSON 429 error handler — rate limit errors return JSON (not raw HTML)

---

## Phase 12 — Audit & Monitoring

- `[x]` Create structured logging with Python `logging`
- `[x]` Log upload events (user_id, file_id, timestamp, status)
- `[x]` Log parsing success/failure (file_id, rows extracted, errors)
- `[ ]` Log ML model execution (deferred — Phase 5)
- `[x]` Log access to sensitive endpoints (chat, transactions, profile)
- `[x]` Add a `GET /health` endpoint for backend status (with MinIO check)

---

## Phase 13 — Frontend Integration

- `[ ]` Replace all frontend mock/dummy data with real API calls via React Query:
  - `[ ]` Transactions list and summary
  - `[ ]` Goals
  - `[ ]` Assets (Savings, Investments, Liabilities)
  - `[ ]` Opportunities / Recommendations
  - `[ ]` Profile data
- `[ ]` Add **SMS Paste UI** to the upload/onboarding screen:
  - `[ ]` Textarea to paste one or multiple SMS lines
  - `[ ]` Submit button triggers `POST /sms/paste` + `POST /sms/parse`
  - `[ ]` Show parsing result feedback (merchant, amount detected)
- `[ ]` Show upload progress indicator for PDF/CSV uploads
- `[ ]` Poll job status via `GET /jobs/{id}/status` for async tasks
- `[ ]` Handle auth token storage and refresh in the frontend

---

## Quick Wins (Do First)

- `[x]` Replace hardcoded `/assets` mock data with a real DB-backed table + endpoint
- `[x]` Replace hardcoded `/opportunities` with DB-backed `recommendations` table
- `[x]` Fix hardcoded `monthlyIncome: 75000` in `/profile` to use actual income data
- `[x]` Add `direction` (credit/debit) column to `transactions` table
- `[x]` Add `source_type` column to `transactions` to track PDF/CSV/SMS origin
