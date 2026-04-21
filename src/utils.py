
import re

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

def tokenize_corpus(corpus):
    """Tokenize a list of documents into lists of tokens."""

    tokenized_corpus = []

    for document in corpus:

        tokens = tokenize(document)
        tokenized_corpus.append(tokens)

    return tokenized_corpus

def clean_output(text):
    """Remove unwanted reasoning tags (e.g., <think>) from model output."""
    if "<think>" in text:
        text = text.split("</think>")[-1]
    return text.strip()