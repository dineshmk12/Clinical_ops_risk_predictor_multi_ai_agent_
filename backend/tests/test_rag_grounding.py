import pytest

from app.hooks.rag_grounding_check import GroundingError, enforce
from app.rag import retrieve
from app.rag.ingest import load_chunks


def test_load_chunks_produces_metadata():
    chunks = load_chunks()
    assert chunks
    for c in chunks[:5]:
        for field in ("doc_id", "title", "doc_type", "study_id", "country", "site", "protocol", "version", "owner", "effective_date"):
            assert field in c["metadata"]


def test_search_finds_relevant_sop():
    evidence = retrieve.search("site activation monitoring visit cadence")
    assert evidence
    assert evidence[0]["doc_id"] == "SOP-001"
    assert evidence[0]["relevance_score"] > 0


def test_search_irrelevant_query_has_low_or_no_score():
    evidence = retrieve.search("xyzzy quantum flux capacitor nonsense")
    assert all(e["relevance_score"] < 0.3 for e in evidence)


def test_is_grounded_true_for_relevant_evidence():
    evidence = retrieve.search("training compliance findings audit")
    assert retrieve.is_grounded(evidence) is True


def test_is_grounded_false_for_empty_evidence():
    assert retrieve.is_grounded([]) is False


def test_grounding_hook_rejects_empty_evidence():
    with pytest.raises(GroundingError):
        enforce([])


def test_grounding_hook_passes_through_valid_evidence():
    evidence = retrieve.search("enrollment risk escalation thresholds")
    assert enforce(evidence) == evidence
