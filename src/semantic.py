import json
from pathlib import Path

import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def load_semantic():
    """Load FAISS index and the SentenceTransformer used at index time."""
    with open(PROCESSED_DIR / "semantic_meta.json") as f:
        meta = json.load(f)
    model = SentenceTransformer(meta["model_name"])
    index = faiss.read_index(str(PROCESSED_DIR / "semantic_faiss.index"))
    return model, index, meta

def semantic_search(query, model, index, df, top_k=5):
    if not query or not str(query).strip():
        raise ValueError("Query can not be empty")

    q = model.encode(
        [str(query)],
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).astype(np.float32)

    scores, idx = index.search(q, top_k)
    scores, idx = scores[0], idx[0]

    results = df.iloc[idx].copy()
    results["semantic_score"] = scores

    return results[
        [
            "product_title",
            "review_title",
            "review_text",
            "semantic_score",
            "rating",
        ]
    ]

def semantic_retriever_rag(query, model, index, df, top_k=5):
    if not query or not str(query).strip():
        raise ValueError("Query cannot be empty")

    if top_k > len(df):
        top_k = len(df)

    q = model.encode(
        [str(query)],
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).astype(np.float32)

    scores, idx = index.search(q, top_k)
    scores, idx = scores[0], idx[0]

    results = df.iloc[idx].copy()
    results["semantic_score"] = scores

    keep_cols = [
        "parent_asin",
        "product_title",
        "review_title",
        "review_text",
        "rating",
        "semantic_score",
    ]

    existing_cols = []

    for col in keep_cols:
        if col in results.columns:
            existing_cols.append(col)

    return results[existing_cols]