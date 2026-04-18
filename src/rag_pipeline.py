from src.semantic import semantic_retriever_rag

def build_context(docs_df):

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




def semantic_rag_pipeline(query, llm, model, index, df, top_k=5):

    docs = semantic_retriever_rag(query, model, index, df, top_k)

    context = build_context(docs)

    prompt = build_prompt(query, context)

    response = llm.invoke(prompt)

    return {
        "answer": response.content,
        "docs": docs,
        "context": context,
        "prompt": prompt
    }