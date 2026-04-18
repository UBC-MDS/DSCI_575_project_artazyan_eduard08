"""
Hybrid retriever: BM25 (sparse) + dense semantic (FAISS), fused with Reciprocal Rank Fusion (RRF).

Use row positions (iloc indices) into ``df`` as stable document IDs so BM25 and semantic
lists dedupe correctly even when column subsets differ between search helpers.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Sequence

import numpy as np
import pandas as pd

from src.utils import tokenize


def _bm25_ranked_positions(query: str, bm25, df: pd.DataFrame, top_k: int) -> list[int]:
    tokenized_query = tokenize(query)
    scores = bm25.get_scores(tokenized_query)
    sorted_indices = np.argsort(scores)
    top = sorted_indices[-top_k:][::-1]
    return [int(i) for i in top]


def _semantic_ranked_positions(
    query: str, semantic_model, semantic_index, df: pd.DataFrame, top_k: int
) -> list[int]:
    if top_k > len(df):
        top_k = len(df)
    q = semantic_model.encode(
        [str(query)],
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).astype(np.float32)
    _scores, idx = semantic_index.search(q, top_k)
    return [int(i) for i in idx[0]]


def reciprocal_rank_fusion(
    ranked_id_lists: Sequence[Sequence[int]],
    *,
    rrf_k: int = 60,
) -> dict[int, float]:
    """
    RRF score for each document ID that appears in any ranked list.

    ``ranked_id_lists``: each inner list is best-first (rank 1 = first element).
    """
    scores: dict[int, float] = defaultdict(float)
    for ids in ranked_id_lists:
        for rank, doc_id in enumerate(ids, start=1):
            scores[int(doc_id)] += 1.0 / (rrf_k + rank)
    return scores


def hybrid_retriever(
    query: str,
    bm25,
    semantic_model,
    semantic_index,
    df: pd.DataFrame,
    top_k: int = 5,
    *,
    per_source_k: int | None = None,
    rrf_k: int = 60,
) -> pd.DataFrame:
    """
    Return top-``top_k`` rows from ``df`` using RRF over BM25 and semantic rankings.

    ``per_source_k``: candidates taken from each retriever before fusion
    (default ``max(top_k * 2, 10)`` so the two lists overlap enough for RRF).
    """
    if not query or not str(query).strip():
        raise ValueError("Query cannot be empty")
    q = str(query).strip()
    if per_source_k is None:
        per_source_k = max(top_k * 2, 10)

    bm25_ids = _bm25_ranked_positions(q, bm25, df, per_source_k)
    sem_ids = _semantic_ranked_positions(q, semantic_model, semantic_index, df, per_source_k)

    fused = reciprocal_rank_fusion([bm25_ids, sem_ids], rrf_k=rrf_k)
    ordered = sorted(fused.keys(), key=lambda i: fused[i], reverse=True)[:top_k]

    out = df.iloc[ordered].copy()
    out["hybrid_rrf_score"] = [fused[i] for i in ordered]

    preferred = [
        "parent_asin",
        "product_title",
        "review_title",
        "review_text",
        "rating",
        "hybrid_rrf_score",
    ]
    cols = [c for c in preferred if c in out.columns]
    return out[cols]


class HybridRetriever:
    """BM25 + semantic FAISS, RRF-fused (optional wrapper for apps / notebooks)."""

    def __init__(
        self,
        bm25,
        semantic_model,
        semantic_index,
        df: pd.DataFrame,
        *,
        per_source_k: int | None = None,
        rrf_k: int = 60,
    ):
        self.bm25 = bm25
        self.semantic_model = semantic_model
        self.semantic_index = semantic_index
        self.df = df
        self.per_source_k = per_source_k
        self.rrf_k = rrf_k

    def invoke(self, query: str, top_k: int = 5) -> pd.DataFrame:
        return hybrid_retriever(
            query,
            self.bm25,
            self.semantic_model,
            self.semantic_index,
            self.df,
            top_k,
            per_source_k=self.per_source_k,
            rrf_k=self.rrf_k,
        )
