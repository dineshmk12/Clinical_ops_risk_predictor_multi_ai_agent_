"""AI Guardrails, verbatim from CLAUDE.md's "AI Guardrails" section. Checked
against every Copilot request before dispatch, and documented in
governance/guardrails.md."""
import re

def _unordered(*terms: str) -> re.Pattern:
    """Match all terms anywhere in the text, in any order."""
    lookaheads = "".join(f"(?=.*{term})" for term in terms)
    return re.compile(lookaheads, re.I | re.S)


DISALLOWED_PATTERNS = [
    (_unordered(r"\bmodify\b", r"\bpatient record"), "modify patient records"),
    (_unordered(r"\brecommend\w*\b", r"\b(treatment|therapy|drug|dosage)\b"), "recommend treatments"),
    (re.compile(r"\b(diagnos|diagnose)\w*\b", re.I), "provide diagnosis"),
    (_unordered(r"\bapprove\b", r"\bprotocol amendment"), "approve protocol amendments"),
    (_unordered(r"\bsubmit\b", r"\bregulatory filing"), "submit regulatory filings"),
    (_unordered(r"\bchange\b", r"\bclinical data\b"), "change clinical data"),
    (_unordered(r"\bmodify\b", r"\benrollment target"), "modify enrollment targets"),
    (_unordered(r"\bapprove\b", r"\bcapa\b"), "approve CAPA plans"),
]


class GuardrailViolation(Exception):
    pass


def check(text: str) -> None:
    for pattern, description in DISALLOWED_PATTERNS:
        if pattern.search(text):
            raise GuardrailViolation(
                f"Request blocked by AI guardrails: this platform may not {description}."
            )
