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

def build_prompt(query, context):
  
    prompt = ""
    prompt += "Use the information below to answer the question clearly and concisely.\n\n"
    prompt += "Also, only use relevant information from the context. Ignore unrelated content.\n\n"
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
        "docs": docs
    }