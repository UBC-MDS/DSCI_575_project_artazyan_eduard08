# Final Discussion

## Step 1: Improve Your Workflow

### Dataset Scaling

We scaled our dataset by combinining approximately 275,000 records from the reviews dataset and 50,000 records from the product metadata dataset. These datasets were merged using an inner join on the product identifier (parent_asin).

The use of an inner join ensured that only records with both review and metadata information were used, avoiding entries with missing fields. After merging and preprocessing, the resulting dataset contained over 10,000 valid records, which were used in our pipeline.

This processed dataset was then used to rebuild both the semantic (FAISS) index and the BM25 index. Working with a larger and more complete dataset improved the diversity and relevance of retrieved documents, making the system more representative of a real-world application.

### LLM Experiment

#### Models Compared

We compared two models:

- Meta-Llama-3-8B-Instruct (Meta, 8B parameters)
- Qwen3-8B (Alibaba, 8B parameters)

These models were selected to compare two different LLM families using the same RAG pipeline.

---

#### Prompt Used

We used the following prompt template:

"You are a helpful Amazon shopping assistant. Answer the question using ONLY the provided context (product reviews and metadata). Only include information that directly answers the question. Do NOT mention unrelated products. If the context does not contain enough relevant information, say so clearly. Cite the product ASIN when possible."

---

#### Results

We evaluated both models using 5 queries. For each query, we retrieved the same top-k documents and passed identical context and prompts to both models.

The outputs showed clear differences in behavior between the models.

---

#### Key Observations

The Llama model consistently produced more concise and coherent responses. It followed instruction to use only the provided context and avoided introducing irrelevant information. When the context was insufficient, Llama clearly stated this, demonstrating strong reliability.

However, the Qwen model generated more verbose outputs that often included intermediate reasoning (e.g., <think> tokens). While this reasoning can be useful in sometimes, it resulted in less direct answers with irrelevant details.

Since Qwen showed less consistency, andkept drifting from the user’s intent or included unnecessary explanations, we conclude that Llama provided more stable and instruction-aligned outputs.

---

#### Model Selection

Based on these results, we selected Meta-Llama-3-8B-Instruct. It demonstrated stronger grounding, better adherence to instructions, and more reliable performance for RAG-based question answering tasks.

## Step 2: Additional Feature (state which option you chose)

The additional feature is a **fully deployed** Streamlit version of the query dashboard, available at: **<https://kindle-review-rag-engine.streamlit.app/>**

## Step 3: Improve Documentation and Code Quality

- Updated the README to include the final milestone additions, including the LLM comparison and final model selection
- Improved clarity of setup and usage instructions for running the project
- Added docstrings to all custom functions to improve readability and clarity
- Verified that no hardcoded file paths are used (all paths are relative)
- Confirmed that no API keys are stored in the source code (using `.env`)

## Step 4: Cloud Deployment Plan