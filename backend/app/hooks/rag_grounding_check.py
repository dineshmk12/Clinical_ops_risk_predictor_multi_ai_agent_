"""Hook 06: rag_grounding_check — rejects a response if no supporting
evidence was retrieved (Grounding Requirement + Development Principle 6,
per CLAUDE.md)."""
from app.rag.retrieve import is_grounded


class GroundingError(Exception):
    """Raised when a response would be returned without supporting evidence."""


def enforce(evidence: list[dict]) -> list[dict]:
    if not is_grounded(evidence):
        raise GroundingError("no supporting evidence found — response rejected to prevent hallucination")
    return evidence
