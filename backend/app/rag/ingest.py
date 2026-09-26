"""Chunking + metadata tagging for the RAG knowledge base, per the CLAUDE.md
RAG strategy (chunk size 1000, overlap 150). Reads Document rows + their
content files and produces (chunk_text, metadata) pairs for indexing.
"""
from pathlib import Path

from app.db import SessionLocal
from app.models import Document

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


def _chunk_text(text: str) -> list[str]:
    if len(text) <= CHUNK_SIZE:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - CHUNK_OVERLAP
    return chunks


def load_chunks() -> list[dict]:
    """Returns a list of {text, metadata} dicts for every chunk of every
    knowledge-base document currently in the eTMF/SharePoint mock store."""
    db = SessionLocal()
    try:
        docs = db.query(Document).all()
        records = []
        for doc in docs:
            path = Path(doc.content_path)
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8")
            for i, chunk in enumerate(_chunk_text(text)):
                records.append(
                    {
                        "text": chunk,
                        "metadata": {
                            "doc_id": doc.doc_id,
                            "chunk_index": i,
                            "title": doc.title,
                            "doc_type": doc.doc_type,
                            "study_id": doc.study_id,
                            "country": doc.country,
                            "site": doc.site,
                            "protocol": doc.protocol,
                            "version": doc.version,
                            "owner": doc.owner,
                            "effective_date": doc.effective_date.isoformat() if doc.effective_date else None,
                        },
                    }
                )
        return records
    finally:
        db.close()
