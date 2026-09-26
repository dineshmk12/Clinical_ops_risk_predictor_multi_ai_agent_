"""Retrieval interface used by RCA/Recommendation/Copilot agents. Every
result carries the metadata required for grounding (doc_id, title, doc_type,
owner, effective_date) so downstream hooks can verify evidence exists."""
from app.rag import vector_store

MIN_RELEVANCE_SCORE = 0.05


def search(query: str, top_k: int = 5) -> list[dict]:
    results = vector_store.query(query, top_k=top_k)
    return [
        {
            "doc_id": r["metadata"]["doc_id"],
            "title": r["metadata"]["title"],
            "doc_type": r["metadata"]["doc_type"],
            "owner": r["metadata"]["owner"],
            "effective_date": r["metadata"]["effective_date"],
            "excerpt": r["text"][:400],
            "relevance_score": round(r["score"], 3),
        }
        for r in results
    ]


def is_grounded(evidence: list[dict]) -> bool:
    """Groundedness check: at least one piece of evidence above the minimum
    relevance threshold. Backs the rag_grounding_check hook."""
    return any(e.get("relevance_score", 0) >= MIN_RELEVANCE_SCORE for e in evidence)
