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