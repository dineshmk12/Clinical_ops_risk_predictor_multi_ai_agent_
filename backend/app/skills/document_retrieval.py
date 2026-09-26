"""Skill 08: document_retrieval.

skill_name: document_retrieval
purpose: retrieve grounding evidence (SOPs, protocols, CAPA, lessons learned)
inputs: query text, optional doc_type filter
outputs: ranked list of evidence documents with relevance scores
tools: sharepoint.search_documents, etmf.retrieve_documents
evaluation_metrics: retrieval precision/recall (see evals/rag_eval.py)
"""
from app.mcp_servers.registry import call_tool


def retrieve_evidence(query: str, top_k: int = 5) -> list[dict]:
    return call_tool("sharepoint.search_documents", query=query, top_k=top_k)


def retrieve_by_type(doc_type: str, study_id: str | None = None) -> list[dict]:
    return call_tool("etmf.retrieve_documents", study_id=study_id, doc_type=doc_type)
