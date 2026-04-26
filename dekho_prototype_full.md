Dekho Prototype – Backend Architecture & ML Integration Document
1. Objective

This document defines the complete backend workflow, database design, ML integration strategy, SMS parsing flow, security framework, and tech stack for the Dekho prototype.

The goal is to transform the current system (frontend + chatbot + isolated ML model + dummy data) into a fully integrated prototype that:

Works with financial data in PDF/CSV format
Also supports SMS-based financial inputs
Supports multiple ML models
Feeds real data into UI + chatbot
Maintains clean architecture, security, and scalability
2. Core Design Philosophy

The system must follow this strict separation:

Raw Data → What the user provides
Structured Data → What actually happened
Feature Layer → Patterns derived from data
ML Models → Interpretations & predictions
Outputs → Insights shown to user

Critical Rule:
The database must NOT be designed around ML models.
ML models must adapt to the data layer, not the other way around.

3. End-to-End System Workflow
Step 1: Data Ingestion
User uploads financial data in PDF/CSV
User can also paste an SMS message in the frontend for prototype demonstration
Files and SMS inputs are stored as raw inputs
Metadata is stored in the database
Step 2: Parsing & Extraction
Extract transaction rows from PDF/CSV
Parse pasted SMS messages into transaction-like records
Handle multiple formats such as:
bank statements
UPI exports
salary credits
debit/credit SMS alerts
Store extracted raw rows
Step 3: Data Normalization

Convert raw extracted data into a standard financial schema.

Example:

Zomato | ₹450 | 8:30 PM
→ standardized transaction record

Example SMS:

Your A/C X1234 is debited by INR 500 at ZOMATO.
→ standardized transaction record
Step 4: Store in Canonical Database
Transactions
Accounts
Categories
Goals
Assets
Parsed SMS records

This becomes the single source of truth

Step 5: Feature Generation

Compute reusable financial metrics:

Monthly spend
Category distribution
Recurring expenses
Savings rate
Spending patterns
SMS-derived transaction patterns
Step 6: ML Model Processing

Each ML model:

Requests only required features
Does NOT access the full database directly
Step 7: Store Model Outputs
Predictions
Insights
Recommendations
Parsed SMS classification results
Step 8: Serve Frontend & Chatbot
APIs feed UI
Chatbot pulls structured insights + summaries
SMS input immediately updates the same backend workflow
4. Frontend Provision for SMS Parsing

A dedicated frontend input area should be added for prototype demonstration.

Suggested UI behavior
Add a “Paste SMS” input box in the upload / input screen
User pastes one SMS message at a time, or multiple SMS lines
On submit:
SMS is stored in the database
SMS parsing service extracts transaction details
Normalized transaction is created
Existing ML and insight pipelines run on it
Why this is important

This allows the prototype to show that Dekho can work not only with PDFs/CSVs but also with transaction SMS messages, which are common in the Indian financial context.

5. Backend Architecture
High-Level Structure
Frontend (React + Zustand + React Query)
        ↓
FastAPI Backend
        ↓
--------------------------------------
| PostgreSQL (structured data)       |
| MinIO (PDF/CSV storage)            |
| Redis (cache + queue)              |
| Celery (background jobs)           |
--------------------------------------
        ↓
ML Models (Feature-based access)
6. Tech Stack (Recommended)
Backend
FastAPI (Python)
Async support
Clean API routing
Easy ML integration
Database
PostgreSQL
Accurate financial storage (NUMERIC)
Strong relational structure
JSON support for flexibility
ORM / Validation
SQLAlchemy (async)
Pydantic v2
File Storage
MinIO (local) → S3 later
Background Processing
Celery + Redis
Parsing
Feature generation
ML inference
SMS processing
Frontend
React + TypeScript
Zustand
TanStack React Query
Framer Motion
7. Database Design
7.1 Raw Data Layer

Tables:

uploaded_files
raw_records
raw_sms_messages

Purpose:

Store original uploads
Maintain audit trail
Preserve SMS inputs in raw form
7.2 Canonical Finance Layer
transactions
id
user_id
account_id
amount
direction (credit/debit)
merchant_name
description
category_id
timestamp
payment_mode
source_type (pdf, csv, sms)
source_reference_id
accounts
id
user_id
bank_name
account_type
balance
categories
id
name
parent_category
goals
id
user_id
target_amount
progress
assets
id
user_id
type
value
sms_parsed_transactions
id
user_id
raw_sms_id
extracted_amount
extracted_merchant
extracted_timestamp
extracted_direction
mapped_transaction_id
parse_confidence
7.3 Feature Layer

Reusable aggregated data:

monthly_features
weekly_features
user_financial_profile

Examples:

total_spend
category_ratio
recurring_expenses
savings_rate
income_estimate
7.4 Output Layer
model_predictions
insights
recommendations
chat_context
8. ML Model Integration Strategy
Key Concept: Feature Contracts

Each model defines required inputs.

8.1 Auto-Categorization Model

Inputs:

merchant_name
description
amount
timestamp
historical category patterns

Output:

predicted category
8.2 Behavior Model (Monthly Wrap)

This model powers the Monthly Wrap feature, inspired by Spotify Wrapped. It generates a visually engaging summary of the user's financial behavior on a monthly basis.

Inputs:

category spend distribution
weekly/monthly trends
recurring transactions
spending spikes

Output:

curated monthly insights highlighting patterns, habits, and behavioral summaries designed for aesthetic presentation in the Monthly Wrap UI

Additional Notes:

Outputs are structured for storytelling-style visualization rather than raw analytics
Each insight can include a reference link/button to navigate to detailed analysis pages
Designed to integrate seamlessly with the existing frontend Monthly Wrap UI implementation
8.3 Opportunity / Recommendation Model

Inputs:

income estimate
savings rate
expense ratio
goal progress
asset data

Output:

investment suggestions
savings recommendations
8.4 Chatbot (Ask Dekho)

Inputs:

summarized financial profile
recent insights
selected transactions
optional knowledge base via RAG
9. Feature Access Pattern

Models do NOT query the database directly.

Instead:

Model → Feature Service → Database

Backend:

filters required fields
prepares input payload
ensures consistency
10. API Layer Design
Core Endpoints

File Handling

POST /upload
GET /files

SMS Handling

POST /sms/paste
GET /sms/history
POST /sms/parse

Transactions

GET /transactions
GET /transactions/summary

Features

GET /features/monthly
GET /features/profile

ML Models

POST /ml/categorize
POST /ml/behavior
POST /ml/recommend

Chatbot

POST /chat
11. Security Architecture

Because the app handles financial data, security must be treated as a core part of the design, not an afterthought.

11.1 Data Protection Principles
Collect only the data needed for the prototype
Separate raw financial inputs from processed outputs
Restrict access by user identity
Keep audit logs for sensitive operations
11.2 Storage Security
Store raw files in protected object storage
Encrypt sensitive fields at rest where possible
Never expose raw financial files publicly
Mask sensitive identifiers such as account numbers
11.3 API Security
Use authentication for all user data endpoints
Enforce authorization so one user cannot access another user’s records
Validate all uploaded files and pasted SMS input
Rate-limit upload and parsing endpoints
11.4 Input Security
Sanitize PDF/CSV parsing inputs
Validate SMS text format before processing
Reject malformed or suspicious files
Prevent injection risks in parsing and logging
11.5 Model & Chat Security
Do not allow models to access unrestricted database tables
Pass only minimal required fields to ML services
Keep chatbot responses limited to authorized user data
Avoid returning raw sensitive data unless explicitly needed in the UI
11.6 Audit & Monitoring
Log upload events
Log parsing success/failure
Log model execution history
Log access to sensitive endpoints
11.7 Prototype Safety Note

Even in prototype stage, the app should behave like a real financial product:

secure by default
minimal exposure
controlled access
traceable actions
12. Development Roadmap
Phase 1: Data Ingestion
File upload
SMS paste input
Storage in MinIO and database
Basic parsing
Phase 2: Database Setup
Create canonical schema
Insert parsed data
Add raw SMS storage
Phase 3: Feature Layer
Build aggregation queries
Store reusable metrics
Phase 4: ML Integration
Connect categorization model
Add behavior model
Add recommendation model
Phase 5: Frontend Integration
Replace dummy data
Connect APIs via React Query
Add SMS paste UI flow
Phase 6: Chatbot Integration
Connect to real data
Add contextual responses
Phase 7: Security Hardening
Add authentication
Add authorization
Add validation and logging
Add field masking and safe access controls
13. Key Architectural Rules
Single Source of Truth
All financial data stored once in the canonical DB
No Model-Specific Databases
Models use shared features
Reusable Feature Layer
Avoid duplicate computations
Async Processing
Heavy tasks handled by Celery
Loose Coupling
Frontend, backend, and ML remain independent but connected
Secure by Design
Financial data must remain protected at every layer
14. Final System Understanding
PDFs/CSVs → Input layer
SMS paste input → Input layer
PostgreSQL → Truth layer
Feature tables → Intelligence layer
ML models → Decision layer
API → Communication layer
Frontend + Chatbot → Experience layer
Security controls → Protection layer
15. Outcome

With this architecture, the prototype will:

Work with real financial data simulated via PDF/CSV/SMS
Support multiple ML models without conflict
Provide consistent insights across UI and chatbot
Demonstrate SMS parsing in the frontend
Keep financial data protected and controlled
Be scalable for future production-level development

End of Document
