"""
RAG pipelines: semantic-only and hybrid (BM25 + dense + RRF).

Both paths share ``build_context`` → ``build_prompt`` → ``llm.invoke``; only the
retriever differs (``semantic_retriever_rag`` vs ``hybrid_retriever``).
"""

from src.hybrid import hybrid_retriever
from src.semantic import semantic_retriever_rag


def build_context(docs_df):
    """Build a formatted context string from retrieved documents."""

    context_parts = []

    for _, row in docs_df.iterrows():

        part = ""
        part += "Product ASIN: " + str(row.get("parent_asin", "N/A")) + "\n"
        part += "Title: " + str(row.get("product_title", "N/A")) + "\n"
        part += "Review Title: " + str(row.get("review_title", "N/A")) + "\n"
        part += "Rating: " + str(row.get("rating", "N/A")) + "\n"
        part += "Review Text: " + str(row.get("review_text", "N/A"))

        context_parts.append(part)

    context = "\n\n---\n\n".join(context_parts)
    return context

SYSTEM_PROMPT_V1 = (
    "You are a helpful Amazon shopping assistant. "
    "Answer the question using ONLY the following context (real product reviews + metadata). "
    "Always cite the product ASIN when possible."
)

SYSTEM_PROMPT_V2 = (
    "You are a helpful Amazon shopping assistant. "
    "Answer the question using ONLY the provided context (product reviews and metadata). "
    "Only include information that directly answers the question. "
    "Do NOT mention unrelated products. "
    "If the context does not contain enough relevant information, say so clearly. "
    "Cite the product ASIN when possible."
)

SYSTEM_PROMPT_V3 = (
    "You are a helpful Amazon shopping assistant. "
    "Use the provided context (product reviews and metadata) to answer the question clearly and concisely. "
    "Focus on the most relevant products and briefly explain why they are relevant. "
    "Avoid mentioning unrelated products. "
    "If the context is insufficient, say so instead of guessing. "
    "Include product ASINs when relevant."
)

SYSTEM_PROMPT = SYSTEM_PROMPT_V2

def build_prompt(query, context, system_prompt = None):
    """Construct the prompt for the LLM using query and retrieved context."""

    if system_prompt is None:
        system_prompt = SYSTEM_PROMPT
  
    prompt = ""
    prompt += system_prompt + "\n\n"
    prompt += "Context:\n"
    prompt += context
    prompt += "\n\nQuestion:\n"
    prompt += query
    prompt += "\n\nAnswer:"
    
    return prompt


def _rag_answer(query, llm, docs_df):
    """Shared context → prompt → LLM step for semantic and hybrid pipelines."""
    context = build_context(docs_df)
    prompt = build_prompt(query, context)
    response = llm.invoke(prompt)
    return {
        "answer": response.content,
        "docs": docs_df,
        "context": context,
        "prompt": prompt,
    }


def semantic_rag_pipeline(query, llm, model, index, df, top_k=5):
    """RAG with FAISS semantic retrieval only (Milestone 2 Step 2)."""
    docs = semantic_retriever_rag(query, model, index, df, top_k)
    return _rag_answer(query, llm, docs)


def hybrid_rag_pipeline(query, llm, bm25, model, index, df, top_k=5):
    """RAG with ``hybrid_retriever`` (BM25 + semantic + RRF) (Milestone 2 Step 3–3.4)."""
    docs = hybrid_retriever(query, bm25, model, index, df, top_k=top_k)
    return _rag_answer(query, llm, docs)