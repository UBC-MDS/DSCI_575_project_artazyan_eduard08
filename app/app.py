import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Ensure project root is on sys.path when Streamlit runs app/app.py
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.bm25 import bm25_search, load_bm25
from src.semantic import load_semantic, semantic_search

PROCESSED = ROOT / "data" / "processed"


@st.cache_resource
def resources():
    df = pd.read_parquet(PROCESSED / "merged.parquet")
    bm25 = load_bm25()
    model, index, meta = load_semantic()
    return {"df": df, "bm25": bm25, "semantic_model": model, "semantic_index": index, "meta": meta}


st.set_page_config(page_title="Book review search", layout="wide")
st.title("Query book reviews")

data = resources()

method = st.radio("Retrieval method", ("BM25", "Semantic"), horizontal=True)
query = st.text_input("Query", placeholder="e.g. weight loss cookbook")
top_k = st.slider("Top k", min_value=1, max_value=20, value=5)

if st.button("Search", type="primary"):
    q = (query or "").strip()
    if not q:
        st.warning("Enter a non-empty query.")
    else:
        try:
            if method == "BM25":
                out = bm25_search(q, data["bm25"], data["df"], top_k=top_k)
            else:
                out = semantic_search(
                    q,
                    data["semantic_model"],
                    data["semantic_index"],
                    data["df"],
                    top_k=top_k,
                )
            st.dataframe(out, use_container_width=True)
        except Exception as e:
            st.error(str(e))