"""
retriever.py
────────────
FAISS-based semantic retriever for Dekho's RAG pipeline.

Usage:
    from app.services.retriever import Retriever
    r = Retriever()
    results = r.search("How much did I spend on food?", top_k=5)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Any

# Index location — backend/data/vector_store/
STORE_DIR = Path(__file__).parent.parent.parent / 'data' / 'vector_store'


class Retriever:
    """Singleton-friendly semantic retriever over the Dekho FAISS index."""

    _instance: 'Retriever | None' = None

    def __new__(cls) -> 'Retriever':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._loaded = False
        return cls._instance

    def load(self) -> None:
        """Load index and model on first use."""
        if self._loaded:
            return

        faiss_path  = STORE_DIR / 'faiss.index'
        chunks_path = STORE_DIR / 'chunks.json'

        if not faiss_path.exists() or not chunks_path.exists():
            raise FileNotFoundError(
                f'Vector store not found at {STORE_DIR}. '
                'Run the ingestion pipeline first:\n'
                '  python backend/scripts/run_ingest.py'
            )

        import faiss
        from sentence_transformers import SentenceTransformer
        import numpy as np

        self._index  = faiss.read_index(str(faiss_path))
        self._chunks: List[Dict[str, Any]] = json.loads(chunks_path.read_text(encoding='utf-8'))
        self._model  = SentenceTransformer('all-MiniLM-L6-v2')
        self._np     = np
        self._loaded = True

    def search(
        self,
        query: str,
        top_k: int = 6,
        chunk_type_filter: str | None = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve the top-k most semantically similar chunks.

        Args:
            query: Natural language question from the user.
            top_k: Number of results to return.
            chunk_type_filter: Optional filter — 'knowledge' | 'data_summary' | 'transaction'.

        Returns:
            List of chunk dicts with added 'score' field (0–1, higher is better).
        """
        self.load()

        # Embed + normalise query
        q_vec = self._model.encode([query], convert_to_numpy=True)
        norm  = self._np.linalg.norm(q_vec, axis=1, keepdims=True)
        q_vec = (q_vec / self._np.maximum(norm, 1e-10)).astype('float32')

        # Search index — fetch 2x to allow filtering
        k_search = min(top_k * 2, self._index.ntotal)
        scores, indices = self._index.search(q_vec, k_search)

        results: List[Dict[str, Any]] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self._chunks):
                continue
            chunk = dict(self._chunks[idx])
            chunk['score'] = float(score)

            if chunk_type_filter and chunk.get('chunk_type') != chunk_type_filter:
                continue

            results.append(chunk)
            if len(results) >= top_k:
                break

        return results

    def search_data(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """Retrieve only data (transaction/profile/goals) chunks."""
        self.load()
        all_results = self.search(query, top_k=top_k * 3)
        data_results = [r for r in all_results if r.get('chunk_type') in ('data_summary', 'transaction')]
        return data_results[:top_k]

    def search_knowledge(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve only knowledge-base chunks."""
        return self.search(query, top_k=top_k, chunk_type_filter='knowledge')

    def search_hybrid(
        self,
        query: str,
        data_k: int = 3,
        knowledge_k: int = 2,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve a mix of data and knowledge chunks.
        Data chunks ground the response in user's actual finances.
        Knowledge chunks provide contextual finance information.
        """
        data      = self.search_data(query, top_k=data_k)
        knowledge = self.search_knowledge(query, top_k=knowledge_k)
        return data + knowledge

    @property
    def is_ready(self) -> bool:
        """Check if the index is loaded and ready to serve."""
        return self._loaded and (STORE_DIR / 'faiss.index').exists()

    @property
    def chunk_count(self) -> int:
        """Number of chunks in the loaded index."""
        if not self._loaded:
            return 0
        return len(self._chunks)


# Module-level singleton
retriever = Retriever()
