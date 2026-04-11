
import re
import pickle
import numpy as np
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

def tokenize(text):
    """
    Tokenize input text by lowercasing, removing punctuation,
    and splitting on whitespace.

    Args:
        text (str): Input text document

    Returns:
        list[str]: List of tokens
    """

    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return text.split()


def load_bm25():
    """
    Load the precomputed BM25 model from disk.

    Returns:
        BM25Okapi: Loaded BM25 model
    """

    with open(PROCESSED_DIR / "bm25.pkl", "rb") as f:
        bm25_model = pickle.load(f)
    return  bm25_model


def bm25_search(query, bm25, df, top_k=5):
    """
    Perform BM25 search on a corpus.

    Args:
        query (str): Query to search
        bm25: BM25 model
        df (pd.DataFrame): DataFrame with documents
        top_k (int): Number of top results to return

    Returns:
        pd.DataFrame: Top-k ranked results with BM25 scores
    """
    if not query:
        raise ValueError("Query can not be empty")

    tokenized_query = tokenize( query)

    scores = bm25.get_scores( tokenized_query)

    sorted_indices = np.argsort(scores)
    top_indices = sorted_indices[-top_k:]
    top_indices = top_indices[::-1]
    
    results = df.iloc[top_indices].copy()
    
    results["bm25_score"] = scores[top_indices]
    
    return results[[
        "product_title",
        "review_title",
        "review_text",
        "bm25_score",
        "rating"
    ]]