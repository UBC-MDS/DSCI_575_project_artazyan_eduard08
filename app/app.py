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

# Amazon Reviews 2023 — Kindle Store subset (McAuley Lab, UCSD)
DATASET_SOURCE_URL = (
    "https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/"
)

SUGGESTED_QUERIES = [
    "books about animals for kids",
    "best books for relaxing before sleep",
    "stories about friendship and growth",
    "good books for beginners learning investing",
    "novels for long flights",
]


@st.cache_resource
def resources():
    df = pd.read_parquet(PROCESSED / "merged.parquet")
    bm25 = load_bm25()
    model, index, meta = load_semantic()
    return {"df": df, "bm25": bm25, "semantic_model": model, "semantic_index": index, "meta": meta}


APP_TITLE = "Information Retrieval with BM25 and Embeddings"

st.set_page_config(page_title=APP_TITLE, layout="wide")
st.title(APP_TITLE)
st.caption("Query the merged book-review corpus; compare sparse (BM25) vs dense (embedding + FAISS) retrieval.")

st.info(
    f"This app searches **Kindle Store** customer reviews and product metadata from the "
    f"**Amazon Reviews 2023** benchmark ([McAuley Lab / UCSD]({DATASET_SOURCE_URL})). "
    f"Data is preprocessed into a single table for retrieval experiments."
)

if "query_input" not in st.session_state:
    st.session_state.query_input = ""

st.caption("Suggested queries — click to fill the search box:")
_n = len(SUGGESTED_QUERIES)
_cols_per_row = 5
for row_start in range(0, _n, _cols_per_row):
    chunk = SUGGESTED_QUERIES[row_start : row_start + _cols_per_row]
    cols = st.columns(len(chunk))
    for j, (col, suggestion) in enumerate(zip(cols, chunk)):
        idx = row_start + j
        if col.button(suggestion, key=f"suggested_{idx}"):
            st.session_state.query_input = suggestion

data = resources()

method = st.radio("Retrieval method", ("BM25", "Semantic"), horizontal=True)
query = st.text_input(
    "Query",
    key="query_input",
    placeholder="e.g. weight loss cookbook",
)
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