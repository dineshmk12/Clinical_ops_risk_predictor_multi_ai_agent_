# Clinical Trial Health & Risk Prediction Platform (Local Prototype)

A locally runnable prototype of the multi-agent Clinical Operations Copilot platform
described in [`CLAUDE.md`](CLAUDE.md). Every Azure/enterprise dependency in that spec
(Service Bus, Azure AI Search, Azure AD, Postgres, Redis, real CTMS/CAMP/CORD/eTMF/
SharePoint, XGBoost/Prophet/LSTM) is replaced with a local, dependency-light stand-in
that preserves the same architecture, contracts, and traceability chain — see
"Stand-ins" below and the governance docs for what's simulated vs. production-ready.

All data is synthetic (`backend/app/seed_data.py`, `Faker`-generated) — no real patient
or Eli Lilly study data is used anywhere in this repository.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Optionally set ANTHROPIC_API_KEY in .env to enable live Claude narrative generation
# for the RCA, Recommendation, and Copilot agents. Without it, those agents fall back
# to deterministic templated text so the whole platform still runs offline.

cd backend
python -m app.seed_data        # seeds SQLite with 5 synthetic studies + knowledge base
uvicorn app.main:app --reload  # serves the API + dashboard at http://127.0.0.1:8000
```

Open `http://127.0.0.1:8000/` for the dashboard, or `http://127.0.0.1:8000/docs` for
the OpenAPI surface.

## Golden path to try

1. Pick a study in the dashboard's study selector (e.g. `STU-1003`, seeded "critical").
2. View its health score, enrollment trend, site risk list, and milestone risk list.
3. Ask the Copilot: *"Why is enrollment behind at this study?"* — this routes through
   the orchestrator to the RCA agent, retrieves grounded evidence from the synthetic
   SOP/CAPA knowledge base, and returns a cited explanation.
4. Ask: *"What sites are underperforming and what should we do?"* — triggers the
   Recommendation agent; if it recommends a site closure, an approval request is
   queued in the "Pending Approvals" panel (Human Approval Matrix).
5. Ask something out of scope, e.g. *"Please recommend a treatment for this patient."*
   — the guardrail layer rejects it with HTTP 403 before any agent runs.

## Architecture

```
Dashboard / REST client
        |
   Clinical Operations Copilot (Agent-08)
        |
   Agent Orchestrator  (app/agents/orchestrator.py — intent routing)
        |
   -------------------------------------------------------------
   |        |        |         |          |        |          |
Study    Enrollment  Site   Milestone  Compliance  RCA   Recommendation
Health              Intelligence
```

Each specialist agent (`backend/app/agents/`) calls one of the 10 skills
(`backend/app/skills/`), which call mock MCP-style tool modules
(`backend/app/mcp_servers/`) standing in for CTMS/CAMP/CORD/eTMF/SharePoint.
Every agent call runs through `BaseAgent.execute()` (`backend/app/agents/base.py`),
which enforces the same trace chain as CLAUDE.md: pre_risk_scoring validation →
skill execution → RAG grounding check (where evidence is used) → audit record →
high-risk alert → approval enqueueing → metrics/tracing.

## Stand-ins for unavailable infrastructure

| Spec component | Local stand-in |
|---|---|
| CTMS/CAMP/CORD/eTMF/SharePoint | Synthetic data (`seed_data.py`) + SQLite, exposed through mock modules in `backend/app/mcp_servers/` using the spec's function names |
| Azure Service Bus | In-process pub/sub (`backend/app/bus/event_bus.py`) using the spec's JSON schema and event types |
| Azure AI Search + `text-embedding-3-large` | Local TF-IDF vector index (`backend/app/rag/`) over a synthetic knowledge base, chunk size 1000 / overlap 150 |
| Redis (short-term memory) | In-memory TTL cache, 24h (`backend/app/memory/short_term.py`) |
| PostgreSQL (long-term memory / audit) | SQLite, matching the spec's Audit Record Schema, 7-year retention flag |
| XGBoost/Prophet/LSTM | Linear-trend regression + weighted risk aggregation (`backend/app/skills/`) |
| Azure AD / RBAC | **Not implemented** — see `governance/privacy.md` |
| Langfuse / OTel / Grafana | In-process counters/timers + trace recorder (`backend/app/observability/`), exposed at `/metrics` |

## Governance

See [`governance/guardrails.md`](governance/guardrails.md),
[`governance/privacy.md`](governance/privacy.md), and
[`governance/human_approval.md`](governance/human_approval.md) for how CLAUDE.md's
AI Guardrails, privacy principles, and Human Approval Matrix are enforced in code.

## Tests and evals

```bash
cd backend
pytest tests/                  # unit tests: hooks, skills, agents, RAG grounding

cd ..
python evals/agent_eval.py     # health/enrollment/milestone/compliance accuracy vs. golden_dataset.csv
python evals/rag_eval.py       # retrieval precision/recall/groundedness/citation rate
python evals/llm_eval.py       # Copilot groundedness/correctness/helpfulness + guardrail rejection
```

## Known limitations

- No authentication/authorization (Azure AD/RBAC from CLAUDE.md's Security section is
  out of scope for this local prototype).
- No encryption at rest/in transit beyond what SQLite/localhost provide by default.
- Forecasting/prediction models are simplified statistical stand-ins, not the
  XGBoost/Prophet/LSTM models named in the spec — see each skill's docstring.
- The "MCP servers" are plain Python modules dispatched by name (`app/mcp_servers/registry.py`),
  not real Model Context Protocol servers — architecturally analogous, not protocol-compliant.
