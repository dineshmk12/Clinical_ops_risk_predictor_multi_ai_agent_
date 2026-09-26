"""SharePoint MCP (mock) — document/SOP/lessons-learned search stand-in.
Delegates ranking to the local RAG vector store (app.rag.vector_store).
"""
from app.mcp_servers.etmf_mcp import retrieve_documents
from app.rag.retrieve import search as rag_search


def search_documents(query: str, top_k: int = 5) -> list[dict]:
    return rag_search(query, top_k=top_k)


def retrieve_sops() -> list[dict]:
    return retrieve_documents(doc_type="SOP")


def retrieve_lessons_learned() -> list[dict]:
    return retrieve_documents(doc_type="Lessons Learned")
