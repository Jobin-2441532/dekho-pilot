"""
run_ingest.py
-------------
CLI wrapper to run the full Dekho ingestion pipeline.

Steps:
  1. Generate synthetic data (if not already present)
  2. Run the RAG ingestion pipeline
  3. Report results

Usage (from project root):
    python backend/scripts/run_ingest.py

Requirements:
    pip install sentence-transformers faiss-cpu numpy
"""

import sys
import os
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / 'backend'))

DATA_DIR  = ROOT / 'data'
TX_CSV    = DATA_DIR / 'transactions' / 'transactions.csv'


def ensure_data_exists():
    """Run the data generator if CSV files don't exist yet."""
    if not TX_CSV.exists():
        print('\n[INFO] Data files not found. Running data generator...\n')
        import subprocess
        result = subprocess.run(
            [sys.executable, str(ROOT / 'backend' / 'scripts' / 'generate_data.py')],
            check=True
        )
    else:
        row_count = sum(1 for _ in open(TX_CSV)) - 1  # minus header
        print(f'[INFO] Found existing transaction data ({row_count} rows)')


def check_dependencies():
    """Check that required packages are installed."""
    missing = []
    for pkg in ['sentence_transformers', 'faiss', 'numpy']:
        try:
            __import__(pkg if pkg != 'faiss' else 'faiss')
        except ImportError:
            missing.append(pkg)

    if missing:
        print('\n[ERROR] Missing required packages:')
        for pkg in missing:
            print(f'  - {pkg}')
        print('\nInstall with:')
        print('  pip install sentence-transformers faiss-cpu numpy\n')
        sys.exit(1)


if __name__ == '__main__':
    print('\n' + '-' * 60)
    print('  Dekho - Data Ingestion Runner')
    print('-' * 60)

    print('\n[Step 1] Checking dependencies...')
    check_dependencies()
    print('  [OK] All dependencies found')

    print('\n[Step 2] Ensuring data files exist...')
    ensure_data_exists()

    print('\n[Step 3] Running ingestion pipeline...')
    from app.services.ingest import run_ingestion
    run_ingestion()

    print('\n[Step 4] Verifying index...')
    from app.services.retriever import retriever
    retriever.load()
    print(f'  [OK] Index ready with {retriever.chunk_count} chunks')

    # Quick test search
    print('\n[Step 5] Running test query...')
    results = retriever.search('How much did I spend on food?', top_k=3)
    print(f'  Test query returned {len(results)} results:')
    for r in results:
        score_str = f'{r["score"]:.3f}'
        print(f'    [{score_str}] [{r["chunk_type"]}] {r["text"][:80].replace(chr(10), " ")}...')

    print('\n' + '-' * 60)
    print('  Phase 3 ingestion complete! Ready for Phase 4 (RAG API).')
    print('-' * 60 + '\n')
