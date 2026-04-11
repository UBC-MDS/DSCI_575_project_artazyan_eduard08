
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

    tokenized_corpus = []

    for document in corpus:

        tokens = tokenize(document)
        tokenized_corpus.append(tokens)

    return tokenized_corpus