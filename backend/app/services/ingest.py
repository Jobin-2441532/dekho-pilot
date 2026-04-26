"""
ingest.py
─────────
RAG ingestion pipeline for Dekho.

Responsibilities:
1. Load structured data (transactions CSV, profile JSON, goals JSON)
2. Load knowledge-base markdown documents
3. Chunk all content into ≤300-token segments with overlap
4. Generate embeddings using sentence-transformers (all-MiniLM-L6-v2)
5. Build and persist a FAISS vector index
6. Save chunk metadata as JSON for retrieval

Output:
    backend/data/vector_store/faiss.index
    backend/data/vector_store/chunks.json
"""

from __future__ import annotations

import csv
import json
import os
import re
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional

# ── Paths ──────────────────────────────────────────────────────────────────
ROOT          = Path(__file__).parent.parent.parent.parent  # Ask_dekho/ project root
KB_DIR        = ROOT / 'knowledge-base'
DATA_DIR      = ROOT / 'data'
TX_CSV        = DATA_DIR / 'transactions' / 'transactions.csv'
INCOME_CSV    = DATA_DIR / 'transactions' / 'income.csv'
PROFILE_JSON  = DATA_DIR / 'profiles' / 'user_profile.json'
GOALS_JSON    = DATA_DIR / 'goals' / 'savings_goals.json'
BUDGETS_JSON  = DATA_DIR / 'goals' / 'budgets.json'
STORE_DIR     = Path(__file__).parent.parent.parent / 'data' / 'vector_store'  # backend/data/vector_store


# ── Data classes ────────────────────────────────────────────────────────────
@dataclass
class Chunk:
    id: str
    text: str
    source: str          # file name or 'transactions' / 'profile' / 'goals'
    chunk_type: str      # 'knowledge' | 'data_summary' | 'transaction'
    category: Optional[str] = None
    metadata: Optional[dict] = None


# ── 1. Text chunker ─────────────────────────────────────────────────────────
def split_into_chunks(
    text: str,
    max_tokens: int = 280,
    overlap_tokens: int = 40,
) -> List[str]:
    """
    Naive token-approximate chunker.
    Splits on double-newlines (paragraphs), accumulates until max_tokens,
    then starts a new chunk with overlap from the previous paragraph.
    """
    paragraphs = [p.strip() for p in re.split(r'\n\n+', text) if p.strip()]
    chunks: List[str] = []
    current: List[str] = []
    current_tokens = 0

    for para in paragraphs:
        # Approximate token count: words * 1.3
        para_tokens = int(len(para.split()) * 1.3)

        if current_tokens + para_tokens > max_tokens and current:
            chunks.append('\n\n'.join(current))
            # Overlap: keep last paragraph from previous chunk
            overlap = current[-1:] if overlap_tokens > 0 else []
            current = overlap
            current_tokens = int(len(overlap[0].split()) * 1.3) if overlap else 0

        current.append(para)
        current_tokens += para_tokens

    if current:
        chunks.append('\n\n'.join(current))

    return chunks


# ── 2. Knowledge-base loader ─────────────────────────────────────────────────
def load_knowledge_base() -> List[Chunk]:
    chunks: List[Chunk] = []
    kb_files = sorted(KB_DIR.glob('*.md'))

    if not kb_files:
        print(f'  [WARN] No markdown files found in {KB_DIR}')
        return chunks

    for kb_file in kb_files:
        text = kb_file.read_text(encoding='utf-8')

        # Strip frontmatter-style metadata header
        lines = text.splitlines()
        content_start = 0
        for i, line in enumerate(lines):
            if line.startswith('#') and i > 0:
                content_start = i
                break

        # Extract topic from header
        topic = 'general'
        for line in lines[:10]:
            if line.startswith('topic:'):
                topic = line.split(':', 1)[1].strip()
                break

        body = '\n'.join(lines[content_start:])
        text_chunks = split_into_chunks(body)

        for j, chunk_text in enumerate(text_chunks):
            chunks.append(Chunk(
                id=f'kb_{kb_file.stem}_{j:03d}',
                text=chunk_text,
                source=kb_file.name,
                chunk_type='knowledge',
                category=topic,
                metadata={'file': kb_file.name, 'chunk_index': j},
            ))

    print(f'  [OK] Loaded {len(chunks)} knowledge chunks from {len(kb_files)} files')
    return chunks


# ── 3. Transaction data loader ───────────────────────────────────────────────
def load_transactions() -> List[Chunk]:
    chunks: List[Chunk] = []

    if not TX_CSV.exists():
        print(f'  [WARN] Transaction CSV not found: {TX_CSV}')
        return chunks

    rows: list[dict] = []
    with open(TX_CSV, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            rows.append(row)

    # ── Per-month summary chunks ─────────────────────────────────────────
    months: dict[str, list[dict]] = {}
    for row in rows:
        month_key = row['date'][:7]   # YYYY-MM
        months.setdefault(month_key, []).append(row)

    for month, txns in sorted(months.items()):
        total = sum(float(t['amount']) for t in txns)
        cat_totals: dict[str, float] = {}
        for t in txns:
            cat_totals[t['category']] = cat_totals.get(t['category'], 0) + float(t['amount'])

        top_cats = sorted(cat_totals.items(), key=lambda x: x[1], reverse=True)[:5]
        top_cats_str = ', '.join(f'{cat} ₹{int(amt):,}' for cat, amt in top_cats)

        # Common merchants
        merchants: dict[str, int] = {}
        for t in txns:
            merchants[t['merchant']] = merchants.get(t['merchant'], 0) + 1
        top_merchants = sorted(merchants.items(), key=lambda x: x[1], reverse=True)[:4]
        top_merchants_str = ', '.join(f'{m} ({c} times)' for m, c in top_merchants)

        summary = (
            f"Month: {month}\n"
            f"Total spend: ₹{int(total):,} across {len(txns)} transactions.\n"
            f"Top categories: {top_cats_str}.\n"
            f"Most frequent merchants: {top_merchants_str}.\n"
            f"Payment modes: {', '.join(set(t['payment_mode'] for t in txns))}."
        )

        chunks.append(Chunk(
            id=f'tx_month_{month}',
            text=summary,
            source='transactions.csv',
            chunk_type='data_summary',
            category='transactions',
            metadata={'month': month, 'transaction_count': len(txns), 'total': total},
        ))

    # ── Individual large transactions as chunks ─────────────────────────
    LARGE_TX_THRESHOLD = 2000
    for row in rows:
        if float(row['amount']) >= LARGE_TX_THRESHOLD:
            chunk_text = (
                f"Transaction on {row['date']}: {row['merchant']} — ₹{int(float(row['amount'])):,}. "
                f"Category: {row['category']}. Payment: {row['payment_mode']}."
                + (f" Note: {row['notes']}." if row.get('notes') else '')
            )
            chunks.append(Chunk(
                id=f'tx_large_{row["id"]}',
                text=chunk_text,
                source='transactions.csv',
                chunk_type='transaction',
                category=row['category'],
                metadata={
                    'date': row['date'], 'merchant': row['merchant'],
                    'amount': float(row['amount']), 'payment_mode': row['payment_mode'],
                },
            ))

    print(f'  [OK] Created {len(chunks)} transaction chunks ({len(months)} monthly summaries + large transactions)')
    return chunks


# ── 4. Profile + goals loader ────────────────────────────────────────────────
def load_profile_and_goals() -> List[Chunk]:
    chunks: List[Chunk] = []

    # Profile
    if PROFILE_JSON.exists():
        profile = json.loads(PROFILE_JSON.read_text(encoding='utf-8'))
        text = (
            f"User profile: {profile.get('name')} from {profile.get('city', 'India')}. "
            f"Age group: {profile.get('age_group')}. "
            f"Monthly income: ₹{profile.get('monthly_income', 0):,}. "
            f"Income range: {profile.get('income_range')}. "
            f"Financial stage: {profile.get('financial_stage')}. "
            f"Monthly budget: ₹{profile.get('monthly_budget', 0):,}. "
            f"Risk comfort: {profile.get('risk_comfort')}. "
            f"Financial goals: {', '.join(profile.get('purposes', []))}."
        )
        chunks.append(Chunk(
            id='profile_main',
            text=text,
            source='user_profile.json',
            chunk_type='data_summary',
            category='profile',
            metadata=profile,
        ))
        print(f'  [OK] Loaded user profile')

    # Savings goals
    if GOALS_JSON.exists():
        goals = json.loads(GOALS_JSON.read_text(encoding='utf-8'))
        for goal in goals:
            pct = round((goal['current_amount'] / goal['target_amount']) * 100)
            remaining = goal['target_amount'] - goal['current_amount']
            text = (
                f"Savings goal: {goal['name']}. "
                f"Target: ₹{goal['target_amount']:,}. "
                f"Current amount saved: ₹{goal['current_amount']:,} ({pct}% complete). "
                f"Remaining: ₹{remaining:,}. "
                f"Monthly contribution: ₹{goal.get('monthly_contribution', 0):,}. "
                f"Deadline: {goal.get('deadline', 'Not set')}. "
                f"Priority: {goal.get('priority', 'medium')}. "
                f"Notes: {goal.get('notes', '')}."
            )
            chunks.append(Chunk(
                id=f'goal_{goal["id"]}',
                text=text,
                source='savings_goals.json',
                chunk_type='data_summary',
                category='goals',
                metadata=goal,
            ))
        print(f'  [OK] Loaded {len(goals)} savings goals')

    # Budgets
    if BUDGETS_JSON.exists():
        budgets = json.loads(BUDGETS_JSON.read_text(encoding='utf-8'))
        budget_lines = '\n'.join(
            f"- {b['category']}: monthly limit ₹{b['monthly_limit']:,}"
            for b in budgets
        )
        total_budget = sum(b['monthly_limit'] for b in budgets)
        text = (
            f"Monthly budget limits:\n{budget_lines}\n"
            f"Total budgeted spend: ₹{total_budget:,}/month."
        )
        chunks.append(Chunk(
            id='budgets_summary',
            text=text,
            source='budgets.json',
            chunk_type='data_summary',
            category='budgets',
            metadata={'budgets': budgets},
        ))
        print(f'  [OK] Loaded {len(budgets)} budget categories')

    return chunks


# ── 5. Embedder + FAISS builder ──────────────────────────────────────────────
def build_index(chunks: List[Chunk], store_dir: Path) -> None:
    if not chunks:
        print('  [WARN] No chunks to index — skipping FAISS build.')
        return

    try:
        from sentence_transformers import SentenceTransformer
        import faiss
        import numpy as np
    except ImportError as e:
        print(f'\n  [ERROR] Missing dependency: {e}')
        print('  Install with: pip install sentence-transformers faiss-cpu numpy')
        raise

    print(f'\n  Loading embedding model (all-MiniLM-L6-v2)...')
    model = SentenceTransformer('all-MiniLM-L6-v2')

    print(f'  Generating embeddings for {len(chunks)} chunks...')
    t0 = time.time()
    texts = [c.text for c in chunks]
    embeddings = model.encode(texts, batch_size=32, show_progress_bar=True, convert_to_numpy=True)
    print(f'  Embeddings done in {time.time() - t0:.1f}s')

    # Normalise for cosine similarity
    import numpy as np
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    embeddings = embeddings / np.maximum(norms, 1e-10)

    # Build FAISS index (inner product = cosine similarity after normalisation)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings.astype('float32'))

    # Persist
    store_dir.mkdir(parents=True, exist_ok=True)
    faiss_path = store_dir / 'faiss.index'
    faiss.write_index(index, str(faiss_path))
    print(f'  [OK] FAISS index saved to {faiss_path}')

    # Save chunk metadata
    chunks_path = store_dir / 'chunks.json'
    chunks_data = [asdict(c) for c in chunks]
    chunks_path.write_text(json.dumps(chunks_data, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'  [OK] Chunk metadata saved to {chunks_path}')
    print(f'  [OK] Index contains {index.ntotal} vectors of dimension {dim}')


# ── Main ─────────────────────────────────────────────────────────────────────
def run_ingestion(store_dir: Path = STORE_DIR) -> None:
    print('\n' + '=' * 60)
    print('  Dekho - RAG Ingestion Pipeline')
    print('=' * 60)

    all_chunks: List[Chunk] = []

    print('\n[1/4] Loading knowledge base...')
    all_chunks.extend(load_knowledge_base())

    print('\n[2/4] Loading transaction data...')
    all_chunks.extend(load_transactions())

    print('\n[3/4] Loading profile and goals...')
    all_chunks.extend(load_profile_and_goals())

    print(f'\n[4/4] Building FAISS index ({len(all_chunks)} total chunks)...')
    build_index(all_chunks, store_dir)

    print('\n' + '=' * 60)
    print('  Ingestion complete!')
    print(f'  Total chunks indexed: {len(all_chunks)}')
    print('=' * 60 + '\n')


if __name__ == '__main__':
    run_ingestion()
