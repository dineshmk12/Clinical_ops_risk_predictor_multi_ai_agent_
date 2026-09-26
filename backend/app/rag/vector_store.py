"""Local vector index — stand-in for Azure AI Search. Uses a TF-IDF
vectorizer (scikit-learn) in place of the `text-embedding-3-large` embedding
model named in CLAUDE.md, so the platform runs fully offline. Swappable for
a real embedding client + Azure AI Search index later without changing the
retrieval interface in app.rag.retrieve.
"""
import threading

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.rag.ingest import load_chunks

_lock = threading.Lock()
_state: dict = {"vectorizer": None, "matrix": None, "chunks": None}


def build_index(force: bool = False) -> None:
    with _lock:
        if _state["vectorizer"] is not None and not force:
            return
        chunks = load_chunks()
        texts = [c["text"] for c in chunks] or [""]
        vectorizer = TfidfVectorizer(stop_words="english")
        matrix = vectorizer.fit_transform(texts)
        _state["vectorizer"] = vectorizer
        _state["matrix"] = matrix
        _state["chunks"] = chunks


def query(text: str, top_k: int = 5) -> list[dict]:
    build_index()
    vectorizer = _state["vectorizer"]
    matrix = _state["matrix"]
    chunks = _state["chunks"]
    if not chunks:
        return []
    query_vec = vectorizer.transform([text])
    scores = cosine_similarity(query_vec, matrix).flatten()
    ranked = sorted(zip(scores, chunks), key=lambda x: x[0], reverse=True)
    results = []
    for score, chunk in ranked[:top_k]:
        if score <= 0:
            continue
        results.append({"score": float(score), "text": chunk["text"], "metadata": chunk["metadata"]})
    return results
