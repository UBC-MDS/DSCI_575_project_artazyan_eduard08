## Model Choice and Rationale

The model we chose was Meta-Llama-3-8B-Instruct from HuggingFaceEndpoint. We chose this model because it seems to provide strong instruction-following capabilities and generates coherent, context-aware responses. HuggingFaceEndpoint allows us to leverage an open-source model without requiring local deployment, which reduces setup complexity while maintaining reproducibility.

Additionally, the model performs well at grounding responses in retrieved context, which is essential for our RAG systems.

## Hybrid retriever (`src/hybrid.py`)

**BM25** and **semantic FAISS** retrieval (same stack as Milestone 1) each produce a ranked list of **row indices** in the merged reviews table. We fuse those lists with **Reciprocal Rank Fusion (RRF)** using `rrf_k = 60`, then take the top `top_k` rows. RRF sums `1 / (rrf_k + rank)` from each list so documents that rank well in both paths rise to the top.

We rank by index instead of calling `bm25_search` alone because that helper drops `parent_asin`, which RAG needs for citations. After fusion we slice the full dataframe so each chunk has metadata and review text.

**Main API:** `hybrid_retriever(...)` (used by `hybrid_rag_pipeline` in `src/rag_pipeline.py`). Optional: `HybridRetriever` class with `invoke` for notebooks or the app.

**Knobs:** `top_k` = final context size; `per_source_k` defaults to `max(top_k * 2, 10)` candidates per retriever before fusion; results include `hybrid_rrf_score` for debugging.
