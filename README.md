# DSCI_575_project_artazyan_eduard08

## Project Overview

This project builds a search system over Amazon Kindle Store data using two approaches:

- BM25 (keyword-based retrieval)
- Semantic search (dense embeddings + FAISS)

The goal is to compare both methods in terms of relevance and performance across different query types.

---

## Environment

From the repo root:

```bash
conda env create -f environment.yml
conda activate dsci575_project
jupyter lab
```

---

## How to Run

1. Launch Jupyter Lab:
```bash
jupyter lab
```

2. Open and run:
```bash
notebooks/milestone1_exploration.ipynb
```

---

## Streamlit App (Query Dashboard)

Interactive search over the dataset using:

- BM25 → keyword matching  
- Semantic search → embeddings + FAISS  

### Prerequisites (in data/processed/)

- merged.parquet  
- bm25.pkl  
- semantic_faiss.index  
- semantic_meta.json  

### Run the app

```bash
conda activate dsci575_project
streamlit run app/app.py
```

Then open:
http://localhost:8501

### Screenshots

**BM25 retrieval**

![Streamlit app — BM25 query and results](img/bm25_querry.png)

**Semantic retrieval**

![Streamlit app — semantic query and results](img/semantic_querry.png)

**App main query UI**

![Streamlit app — main query UI](img/app_mq.png)

---

## Workflow

1. Convert raw data to parquet using DuckDB  
2. Merge review and metadata datasets  
3. Construct document field (title + description + reviews)  
4. Tokenize text using src/utils.py  
5. Build BM25 index  
6. Build semantic search index using embeddings + FAISS  

---

## RAG Pipeline Workflow

We implemented a semantic RAG pipeline that follows four steps: retrieval, context construction, prompt generation, and response generation.

Given a user query, we first retrieve the top-k most relevant documents using an updated Milestone 1 semantic retriever function. Then, these documents are combined into a structured context. The context and query are passed into a prompt template, which is sent to the language model to generate a final answer.

This design allows us to easily test different prompts and ensures that the model’s responses are accurate.

```mermaid
flowchart LR
    A[User Query] --> B[Semantic Retriever (FAISS)]
    B --> C[Top-K Relevant Documents]
    C --> D[Build Context]
    D --> E[Prompt Template (V2)]
    E --> F[LLM (Meta LLaMA)]
    F --> G[Final Answer + Sources]
```

---

## Results

### Milestone 1: Retrieval Evaluation
Results and analysis comparing BM25 and semantic search can be found in:

results/milestone1_discussion.md

### Milestone 2: RAG Evaluation
Results and qualitative evaluation of the RAG and hybrid RAG systems can be found in:

results/milestone2_discussion.md