# Privacy & Data Protection

## Principle 7 (CLAUDE.md): Never expose PHI or PII

This prototype does not ingest or store any real patient, subject, or PHI/PII data:

- All CTMS/CAMP/CORD/eTMF/SharePoint data is synthetically generated
  (`backend/app/seed_data.py`) using `Faker`-generated names and fabricated study/site/
  enrollment metrics. No real Eli Lilly study data is used.
- Data models operate at the study/site/aggregate level (enrollment *counts*, deviation
  *counts*, milestone dates) — there is no subject-level or patient-identifiable field in
  the schema (`backend/app/models.py`).
- The RAG knowledge base contains synthetic SOP/protocol/CAPA/lessons-learned text with no
  real patient information.

## Compliance requirements referenced (CLAUDE.md)

ICH-GCP, 21 CFR Part 11, HIPAA, GDPR, GDP, Internal AI Governance.

## Before connecting real systems

If real CTMS/CAMP/CORD/eTMF/SharePoint connections replace the mock MCP servers in
`backend/app/mcp_servers/`:

- Confirm no subject-level identifiers flow into the platform's database, RAG index, or LLM
  prompts — this platform's data model and prompts are designed around aggregate
  operational metrics only, and any real integration must preserve that boundary.
- Azure AD authentication and RBAC (referenced in CLAUDE.md's Security section) are **not**
  implemented in this local prototype and must be added before any non-synthetic deployment.
- Encryption at rest/in transit and mandatory audit logging (CLAUDE.md Security section) must
  be configured at the real database/transport layer; this prototype's SQLite file is
  unencrypted and intended for local development only.
