import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st
from pandas.api.types import is_numeric_dtype

# Ensure project root is on sys.path when Streamlit runs app/app.py
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.bm25 import bm25_search, load_bm25
from src.rag_pipeline import hybrid_rag_pipeline, semantic_rag_pipeline
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

ANSWER_PREVIEW_CHARS = 2800


@st.cache_resource
def resources():
    df = pd.read_parquet(PROCESSED / "merged.parquet")
    bm25 = load_bm25()
    model, index, meta = load_semantic()
    return {"df": df, "bm25": bm25, "semantic_model": model, "semantic_index": index, "meta": meta}


@st.cache_resource
def rag_llm():
    """Hosted LLM for RAG tab; requires HUGGINGFACEHUB_API_TOKEN in environment or .env."""
    try:
        from dotenv import load_dotenv
        from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
    except ImportError as e:
        raise RuntimeError(f"Missing RAG dependencies: {e}") from e

    load_dotenv(ROOT / ".env")
    load_dotenv()
    token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    if not token:
        return None
    endpoint = HuggingFaceEndpoint(
        repo_id="meta-llama/Meta-Llama-3-8B-Instruct",
        task="text-generation",
        max_new_tokens=250,
        huggingfacehub_api_token=token,
    )
    return ChatHuggingFace(llm=endpoint)


def rating_stars(rating) -> str:
    try:
        n = int(round(float(rating)))
    except (TypeError, ValueError):
        return "—"
    n = max(0, min(5, n))
    return "★" * n + "☆" * (5 - n) + f" ({rating}/5)"


def _search_result_column_config(df: pd.DataFrame) -> dict:
    """Widen text columns and raise max_chars so long review snippets stay readable."""
    cfg = {}
    for col in df.columns:
        if is_numeric_dtype(df[col]) and "score" in col.lower():
            cl = col.lower()
            fmt = (
                "%.4f"
                if "semantic" in cl or "bm25" in cl or "rrf" in cl
                else "%.6f"
            )
            cfg[col] = st.column_config.NumberColumn(col, width="small", format=fmt)
        elif is_numeric_dtype(df[col]):
            cfg[col] = st.column_config.NumberColumn(col, width="small", format="%.2f")
        else:
            cfg[col] = st.column_config.TextColumn(
                str(col), width="large", max_chars=20_000
            )
    return cfg


def truncate_text(text, max_chars: int = 220) -> str:
    if text is None or (isinstance(text, float) and pd.isna(text)):
        return ""
    s = str(text).strip()
    if len(s) <= max_chars:
        return s
    return s[: max_chars - 1] + "…"


def render_numbered_sources(docs: pd.DataFrame):
    st.subheader("Sources (order matches context chunks)")
    for i, row in enumerate(docs.itertuples(index=False), start=1):
        title = getattr(row, "product_title", "N/A") or "N/A"
        asin = getattr(row, "parent_asin", None)
        asin_s = str(asin) if asin is not None and str(asin) != "nan" else "N/A"
        rating = getattr(row, "rating", "—")
        score_bits = []
        if hasattr(row, "hybrid_rrf_score"):
            score_bits.append(f"RRF: {getattr(row, 'hybrid_rrf_score', 0):.4f}")
        if hasattr(row, "semantic_score"):
            score_bits.append(f"semantic: {getattr(row, 'semantic_score', 0):.4f}")
        score_line = " · ".join(score_bits) if score_bits else None
        body = getattr(row, "review_text", "") or ""
        preview = truncate_text(body, 220)
        with st.container(border=True):
            st.markdown(f"**[{i}]** {title}")
            st.caption(f"ASIN: `{asin_s}` · {rating_stars(rating)}")
            if score_line:
                st.caption(score_line)
            if preview:
                st.text(preview)


APP_TITLE = "Kindle Store search & RAG"

st.set_page_config(page_title=APP_TITLE, layout="wide")
st.title(APP_TITLE)
st.caption(
    "Milestone 1: BM25 vs semantic search. Milestone 2: RAG answers (semantic or hybrid) over the same corpus."
)

st.info(
    f"This app uses **Kindle Store** customer reviews and product metadata from the "
    f"**Amazon Reviews 2023** benchmark ([McAuley Lab / UCSD]({DATASET_SOURCE_URL}))."
)

if "search_query" not in st.session_state:
    st.session_state.search_query = ""
if "rag_query" not in st.session_state:
    st.session_state.rag_query = ""

st.caption("Suggested queries — click to fill the active tab’s query box:")
_cols_per_row = 5
_n = len(SUGGESTED_QUERIES)
for row_start in range(0, _n, _cols_per_row):
    chunk = SUGGESTED_QUERIES[row_start : row_start + _cols_per_row]
    cols = st.columns(len(chunk))
    for j, (col, suggestion) in enumerate(zip(cols, chunk)):
        idx = row_start + j
        if col.button(suggestion, key=f"suggested_{idx}"):
            st.session_state.search_query = suggestion
            st.session_state.rag_query = suggestion

data = resources()

tab_search, tab_rag = st.tabs(["Search (retrieval only)", "RAG"])

with tab_search:
    st.markdown("**Milestone 1** — compare sparse vs dense retrieval; no LLM.")
    method = st.radio("Retrieval method", ("BM25", "Semantic"), horizontal=True, key="search_method")
    query = st.text_input("Query", key="search_query", placeholder="e.g. weight loss cookbook")
    top_k = st.slider("Top k", min_value=1, max_value=20, value=5, key="search_top_k")

    if st.button("Search", type="primary", key="btn_search"):
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
                h = min(800, 48 + 36 * (len(out) + 1))
                st.dataframe(
                    out,
                    use_container_width=True,
                    column_config=_search_result_column_config(out),
                    height=h,
                    hide_index=True,
                )
            except Exception as e:
                st.error(str(e))

with tab_rag:
    st.markdown("**Milestone 2** — grounded answers using retrieved reviews + hosted LLaMA.")
    rag_mode = st.radio(
        "RAG retrieval",
        ("Hybrid (BM25 + semantic + RRF)", "Semantic only"),
        horizontal=True,
        key="rag_mode",
    )
    query_r = st.text_input("Question", key="rag_query", placeholder="e.g. good books for beginners learning investing")
    rag_top_k = st.slider("Context chunks (top k)", min_value=1, max_value=15, value=5, key="rag_top_k")

    llm = rag_llm()
    if llm is None:
        st.warning(
            "Set **HUGGINGFACEHUB_API_TOKEN** in a `.env` file at the project root (or export it) "
            "and restart the app. See README → Milestone 2."
        )

    if st.button("Generate answer", type="primary", key="btn_rag", disabled=llm is None):
        q = (query_r or "").strip()
        if not q:
            st.warning("Enter a non-empty question.")
        else:
            try:
                if rag_mode.startswith("Hybrid"):
                    result = hybrid_rag_pipeline(
                        q,
                        llm,
                        data["bm25"],
                        data["semantic_model"],
                        data["semantic_index"],
                        data["df"],
                        top_k=rag_top_k,
                    )
                else:
                    result = semantic_rag_pipeline(
                        q,
                        llm,
                        data["semantic_model"],
                        data["semantic_index"],
                        data["df"],
                        top_k=rag_top_k,
                    )
                answer = result["answer"] or ""
                st.subheader("Answer")
                preview = answer[:ANSWER_PREVIEW_CHARS]
                st.markdown(preview)
                if len(answer) > ANSWER_PREVIEW_CHARS:
                    with st.expander("Full answer (model output)"):
                        st.markdown(answer)

                render_numbered_sources(result["docs"])

                with st.expander("Retrieved context (raw)"):
                    st.text(result.get("context", ""))
            except Exception as e:
                st.error(str(e))

st.divider()
st.markdown(
    "**Run locally:** `conda activate dsci575_project` then `streamlit run app/app.py` "
    "from the repository root."
)
