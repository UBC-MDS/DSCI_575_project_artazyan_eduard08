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

## Workflow

1. Convert raw data to parquet using DuckDB
2. Merge review and metadata datasets
3. Construct document field (title + description + reviews)
4. Tokenize text using src/utils.py
5. Build BM25 index