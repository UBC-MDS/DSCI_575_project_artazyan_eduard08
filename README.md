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

---

## Workflow

1. Convert raw data to parquet using DuckDB  
2. Merge review and metadata datasets  
3. Construct document field (title + description + reviews)  
4. Tokenize text using src/utils.py  
5. Build BM25 index  
6. Build semantic search index using embeddings + FAISS  

---

## Results

Results and analysis comparing BM25 and semantic search can be found in:

```
results/milestone1_discussion.md
```