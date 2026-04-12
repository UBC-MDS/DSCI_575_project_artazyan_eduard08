# DSCI_575_project_artazyan_eduard08

##  Project Overview


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
    notebooks/milestone1_exploration.ipynb

---

## Streamlit app (query dashboard)

Interactive search over the merged corpus: choose **BM25** (keyword) or **Semantic** (dense embeddings + FAISS), set **top k**, and view ranked results.

**Prerequisites** (under `data/processed/` from the notebook / preprocessing pipeline):

- `merged.parquet`
- `bm25.pkl`
- `semantic_faiss.index` and `semantic_meta.json`

From the **repository root**, with the conda environment active:

```bash
conda activate dsci575_project
streamlit run app/app.py
```

Streamlit prints a local URL (typically `http://localhost:8501`). Open it in your browser.

### Dashboard screenshots

**BM25 retrieval**

![Streamlit dashboard — BM25 query and results](img/bm25_querry.png)

**Semantic retrieval**

![Streamlit dashboard — semantic query and results](img/semantic_querry.png)

---

## Workflow

1. Convert raw data to parquet using DuckDB
2. Merge review and metadata datasets
3. Construct document field (title + description + reviews)
4. Tokenize text using src/utils.py
5. Build BM25 index