# AI Guardrails

Enforced in code by [`backend/app/guardrails.py`](../backend/app/guardrails.py), checked on
every Clinical Operations Copilot request before dispatch to any specialist agent.

## The platform SHALL NOT

- Modify patient records
- Recommend treatments
- Provide diagnosis
- Approve protocol amendments
- Submit regulatory filings
- Change clinical data
- Modify enrollment targets
- Approve CAPA plans

## The platform MAY

- Predict risks
- Explain risks
- Recommend actions
- Generate reports
- Retrieve evidence

## Enforcement

- The Copilot's `guardrails.check()` scans every incoming natural-language question for
  the disallowed intents above and rejects the request (HTTP 403) before any agent runs.
- No API endpoint exposes a write path into patient, clinical, or enrollment-target data —
  the platform is read/predict/recommend-only by construction; there is nothing to guardrail
  at the data layer because no such mutation endpoint exists.
- The RCA and Recommendation agents' system prompts additionally instruct the model never to
  recommend treatments, diagnoses, protocol amendments, regulatory filings, or clinical/
  enrollment data changes, as a second layer of defense on top of the guardrail check.
- Recommended actions are drawn from a fixed, human-curated action library
  (`backend/app/skills/recommendation_engine.py`) rather than open-ended generation, so
  recommendations are inherently bounded to operational/administrative interventions.
