"""RAG retrieval evaluation against the synthetic knowledge base.

Proxy for CLAUDE.md's RAG metrics (Retrieval Precision, Retrieval Recall,
Groundedness, Citation Rate) using a small hand-labeled query -> expected
doc_id set. Run: `python evals/rag_eval.py` from the repo root (after
`python backend/app/seed_data.py`).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.rag import retrieve

# Each query maps to the doc_id(s) a relevant retrieval should surface.
LABELED_QUERIES = [
    {"query": "site activation monitoring visit cadence", "expected_doc_ids": {"SOP-001"}},
    {"query": "enrollment risk escalation thresholds", "expected_doc_ids": {"SOP-002"}},
    {"query": "screening and enrollment procedures protocol", "expected_doc_ids": {"PROT-001"}},
    {"query": "recurrent informed consent deviations CAPA", "expected_doc_ids": {"CAPA-001"}},
    {"query": "late site activation recovery lessons learned", "expected_doc_ids": {"LL-001"}},
    {"query": "training compliance findings audit", "expected_doc_ids": {"AUD-001"}},
]


def run():
    total_precision = total_recall = 0.0
    grounded_count = 0
    cited_count = 0

    for case in LABELED_QUERIES:
        evidence = retrieve.search(case["query"], top_k=5)
        retrieved_ids = {e["doc_id"] for e in evidence}
        expected_ids = case["expected_doc_ids"]

        true_positives = retrieved_ids & expected_ids
        precision = len(true_positives) / len(retrieved_ids) if retrieved_ids else 0.0
        recall = len(true_positives) / len(expected_ids) if expected_ids else 0.0
        total_precision += precision
        total_recall += recall

        grounded = retrieve.is_grounded(evidence)
        grounded_count += grounded
        cited_count += bool(retrieved_ids)

        print(
            f"query={case['query']!r}: retrieved={sorted(retrieved_ids)} "
            f"expected={sorted(expected_ids)} precision={precision:.2f} recall={recall:.2f} "
            f"grounded={grounded}"
        )

    n = len(LABELED_QUERIES)
    print("\n--- RAG Eval Summary ---")
    print(f"Mean retrieval precision: {total_precision / n:.2f}")
    print(f"Mean retrieval recall:    {total_recall / n:.2f}")
    print(f"Groundedness rate:        {grounded_count}/{n} ({100 * grounded_count / n:.0f}%)")
    print(f"Citation rate:            {cited_count}/{n} ({100 * cited_count / n:.0f}%)")


if __name__ == "__main__":
    run()
