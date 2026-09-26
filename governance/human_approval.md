# Human Approval Matrix

Implemented in [`backend/app/approval/approval_queue.py`](../backend/app/approval/approval_queue.py)
and enforced by the `human_review_required` hook
(`backend/app/hooks/human_review_required.py`).

## Requires approval

- Compliance Escalations — raised by the Compliance Agent (`approval_type=compliance_escalation`)
- Audit Findings — raised via eTMF audit-status findings surfaced through Compliance Agent
- Executive Reports — raised by `CopilotAgent.generate_report` (`approval_type=executive_report`)
- Site Closure Recommendations — raised by the Recommendation Agent when a recommended action
  concerns site closure (`approval_type=site_closure_recommendation`)
- Study Closure Recommendations — same path, study-level (`approval_type=study_closure_recommendation`)

## No approval required

- Dashboards
- Risk Visualization
- Forecasts
- Reporting Drafts

## Flow

1. An agent produces output that matches one of the "Requires approval" categories.
2. `BaseAgent.execute(..., approval_type=...)` calls `human_review_required.await_approval`,
   which enqueues an `ApprovalRequest` row (status `pending`) via `approval_queue.enqueue`.
3. `GET /approvals?status=pending` lists outstanding requests (surfaced in the dashboard's
   "Pending Approvals" panel).
4. A human reviewer calls `POST /approvals/{id}/decision` with `{"decision": "approved" |
   "rejected", "resolved_by": "<name>"}`.
5. Per Development Principle 5 ("Human approval overrides AI decisions"), no downstream action
   is taken by the platform itself on approval/rejection — this prototype only tracks the
   decision in the audit trail; it does not auto-execute anything as a result.
