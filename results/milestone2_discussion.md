## Model choice and rationale

We use **Meta-Llama-3-8B-Instruct** via HuggingFace’s hosted endpoint (`HuggingFaceEndpoint` + `ChatHuggingFace`). It follows instructions well, produces readable answers, and tends to stay close to the retrieved review text when the system prompt asks for that. Using a hosted model avoids local GPU requirements and keeps the notebook and Streamlit app easy to reproduce: only a Hugging Face token and network access are needed.

## Prompt template experiments (V1–V3)

We defined three system prompts in `src/rag_pipeline.py` and compared them on the same queries and retrieval settings.

| Variant | Intent |
|--------|--------|
| **V1** | Minimal: answer only from context; cite ASIN when possible. |
| **V2** | Stricter: answer only from context, avoid unrelated products, admit when context is insufficient, cite ASINs. |
| **V3** | Slightly more explanatory: concise answers, briefly justify relevance, still refuse to guess when context is thin. |

**What worked best:** We adopted **V2** as `SYSTEM_PROMPT` for the main pipeline and app. **V1** sometimes produced answers that felt complete but pulled in tangential products because it did not explicitly forbid unrelated items. **V3** occasionally added extra framing that did not always match sparse retrieval, while **V2** gave the clearest trade-off between grounding and usefulness. All variants were tested with the same `build_context` format (ASIN, title, rating, review text).

## Top‑k (optional)

We mostly used **`top_k = 5`** for RAG (and `3` in some notebook cells for faster runs). **Smaller k (e.g. 3)** keeps the prompt short and reduces noise but can miss a relevant review if the retriever ranks it just outside the cut. **Larger k (e.g. 8–10)** adds coverage but increases redundancy and can dilute focus; the model may still only emphasize a subset of chunks. We did not run a formal sweep; qualitatively, **5** was a reasonable default for our Kindle subset.

## Hybrid retriever (`src/hybrid.py`)

**BM25** and **semantic FAISS** each return a ranked list of **row indices** in the merged table. We fuse them with **Reciprocal Rank Fusion (RRF)** (`rrf_k = 60`), then take the top `top_k` rows. RRF rewards documents that rank well on **both** keyword and embedding sides. We use row indices (not `bm25_search` alone) so each chunk keeps **`parent_asin`** for citations. **`hybrid_retriever`** feeds **`hybrid_rag_pipeline`**; **`semantic_rag_pipeline`** uses FAISS only, with the same prompts and context builder.

## Step 5 — Qualitative evaluation (manual)

We ran **hybrid RAG** (and spot-checked **semantic-only RAG** on the same queries) with **`top_k = 5`**. For each query we judge **Accuracy** (factually supported by retrieved reviews), **Completeness** (addresses the question’s main intent), and **Fluency** (clear, natural wording). Ratings are **Y/N** per dimension.

| # | Query | Accuracy | Completeness | Fluency |
|---|--------|----------|--------------|---------|
| 1 | books about animals for kids | Y | Y | Y |
| 2 | best books for relaxing before sleep | Y | Y | Y |
| 3 | stories about friendship and growth | Y | Y | Y |
| 4 | good books for beginners learning investing | Y | N | Y |
| 5 | novels for long flights | Y | Y | Y |

**Notes on row 4:** Retrieval often mixed general finance or tangentially related titles with true “beginner investing” books; the answer stayed grounded in context but did not always narrow to a crisp, complete buying-style recommendation. Hybrid retrieval sometimes surfaced keyword-heavy finance titles that semantic search alone ranked differently; neither pipeline guarantees perfect intent match when the corpus is sparse for that phrasing.

## Summary of observations

- **Hybrid vs semantic:** Hybrid helped on queries where **exact terms** matter (e.g. genre or topic keywords) while semantic helped on **paraphrases**; RRF merges both without hand-tuned weights per query.
- **Failure modes:** When no review in the top‑k truly matches the question, the model generally **refused or hedged** (especially under V2), which is preferable to hallucinating product facts.
- **Overall:** The pipeline behaves like a **review-grounded assistant**, not a catalog with full metadata; quality tracks retrieval quality first.

## Reflection

RAG quality in this project is largely **retrieval quality** plus a **conservative prompt**. The biggest gains came from choosing a strict system prompt (V2) and keeping context structured with ASINs and ratings. The hybrid retriever is a practical way to combine BM25 and dense search without maintaining separate manual score blends.

## Limitations (2–4)

1. **Corpus coverage:** Kindle reviews are incomplete for many products; answers cannot reflect price, availability, or non-review facts.
2. **Retrieval limits:** Fixed `top_k` and chunking (one row per “document”) can drop the best evidence or include noisy reviews.
3. **Hosted LLM:** Latency, rate limits, and occasional paraphrasing of review wording; no guarantee of verbatim quotes.
4. **Evaluation:** Manual yes/no on five queries is subjective and not a substitute for labeled QA metrics or user studies.

## Ideas for improvement

- **Re-ranking** a wider candidate pool (e.g. cross-encoder) after hybrid retrieval.
- **Query expansion** or **HyDE**-style prompts to improve recall for short queries.
- **Smaller k** when contexts are redundant; **adaptive k** when the first ranks have low scores.
- **Citation forcing** (e.g. require bracketed source indices matching our numbered context blocks) for easier verification in the app.
