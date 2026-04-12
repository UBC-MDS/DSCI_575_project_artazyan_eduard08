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

