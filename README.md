# Dekho — Habit-First Personal Finance Companion

> AI-powered personal finance chatbot built with React + FastAPI + Ollama + FAISS

---

## Project Structure

```
Ask_dekho/
├── frontend/          # React + Vite + TypeScript UI
├── backend/           # Python + FastAPI + Ollama backend
│   ├── app/
│   │   ├── api/       # Route handlers
│   │   ├── core/      # Config, database, settings
│   │   └── services/  # Business logic (RAG, ingestion, etc.)
│   ├── .env
│   ├── requirements.txt
│   └── run.py
├── data/
│   ├── transactions/  # Synthetic transaction CSVs
│   ├── profiles/      # User profile data
│   └── goals/         # Savings goal data
└── knowledge-base/    # Finance knowledge documents
```

---

## Quick Start

### 1. Backend

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate          # Windows
pip install -r requirements.txt
python run.py
```
Backend runs at: http://localhost:8000

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```
Frontend runs at: http://localhost:5173

### 3. Ollama (required for Ask Dekho)

```bash
ollama pull llama3.2
ollama serve
```

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | React + Vite + TypeScript |
| Backend | Python + FastAPI |
| LLM Runtime | Ollama (local) |
| Embeddings | SentenceTransformers |
| Vector Search | FAISS |
| Storage | SQLite (MVP) |
| Data Parsing | Pandas, python-docx, pdfplumber |

---

## Design Philosophy

- Calm editorial aesthetic — not a dense banking dashboard
- Warm cream surfaces, generous spacing, soft shadows
- Habit-first, behavior-first, not product-push-first
- Ask Dekho chatbot as the primary experience
