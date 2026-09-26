# =================================================================
# PHARMA AI PROJECT
# Clinical Trial Health & Risk Prediction Platform
# =================================================================

Version: 1.0
Domain: Clinical Operations
Organization: Eli Lilly
Implementation Pattern: Multi-Agent AI System
Architecture: Agentic AI + RAG + MCP
Framework: Claude Code

# =================================================================
# PROJECT VISION
# =================================================================

Build an AI-driven Clinical Trial Health & Risk Prediction Platform
that proactively identifies operational risks across clinical studies.

The platform leverages CTMS, CAMP, CORD and associated Clinical
Operations systems to predict:

- Enrollment delays
- Site performance issues
- Milestone slippage
- Compliance risks
- Resource bottlenecks
- Study execution risks

The goal is to transform Clinical Operations from a reactive
monitoring model to a proactive intervention model.

# =================================================================
# BUSINESS PROBLEM
# =================================================================

Clinical Operations teams monitor studies using multiple systems.

Current challenges include:

- Late identification of enrollment risks
- Site underperformance
- Delayed site activation
- Milestone slippage
- Compliance gaps
- Resource utilization inefficiencies
- Manual reporting effort

Traditional reporting is retrospective.

The platform shall provide:

- Predictive Intelligence
- Prescriptive Recommendations
- Root Cause Analysis
- Conversational Clinical Operations Copilot

# =================================================================
# BUSINESS OBJECTIVES
# =================================================================

1. Reduce enrollment delays.
2. Improve site productivity.
3. Improve milestone predictability.
4. Improve audit readiness.
5. Reduce manual reporting effort.
6. Increase study visibility.
7. Enable natural language clinical insights.
8. Improve portfolio-level decision making.

# =================================================================
# DOMAIN KNOWLEDGE
# =================================================================

Primary Systems:

- CTMS
- CAMP
- CORD

Future Systems:

- SIP
- eTMF
- Veeva
- SharePoint
- Teams
- Outlook
- Data Lake
- Snowflake

# =================================================================
# PRIMARY USERS
# =================================================================

Executive Leadership
Clinical Operations Managers
Study Managers
Clinical Trial Managers
CRAs
Site Managers
Compliance Teams
QA Teams

# =================================================================
# AGENTIC ARCHITECTURE
# =================================================================

Pattern:
Supervisor + Specialist Agents

Architecture:

Clinical Operations Copilot
            |
            |
    Agent Orchestrator
            |
------------------------------------------------
|      |       |      |      |      |          |
V      V       V      V      V      V          V

Study Health Agent
Enrollment Agent
Site Intelligence Agent
Milestone Agent
Compliance Agent
RCA Agent
Recommendation Agent

# =================================================================
# AGENT DEFINITIONS
# =================================================================

## AGENT-01

Name:
Study Health Agent

Purpose:
Assess overall study health.

Inputs:
- Enrollment
- Sites
- Milestones
- Deviations
- Queries
- Resources

Outputs:
- Health Score
- Health Trend
- Health Summary

KPIs:
- Health Accuracy > 85%

------------------------------------------------

## AGENT-02

Name:
Enrollment Prediction Agent

Purpose:
Predict future recruitment performance.

Capabilities:

- Enrollment forecasting
- Recruitment trend analysis
- Delay risk prediction

Models:

- XGBoost
- Prophet
- LSTM

Outputs:

- Forecasted Enrollment
- Delay Probability
- Confidence Score

KPIs:

Forecast Accuracy > 85%

------------------------------------------------

## AGENT-03

Name:
Site Intelligence Agent

Purpose:

Detect underperforming sites.

Capabilities:

- Site scoring
- Site ranking
- Risk assessment

Outputs:

- Site Risk Score
- Site Risk Tier
- Improvement Actions

KPIs:

Precision > 80%

------------------------------------------------

## AGENT-04

Name:
Milestone Prediction Agent

Purpose:

Predict milestone delays.

Milestones:

- Study Startup
- FPI
- LPI
- DB Lock
- CSR
- Closeout

Outputs:

- Predicted Date
- Delay Probability
- Risk Category

KPIs:

Prediction Accuracy > 85%

------------------------------------------------

## AGENT-05

Name:
Compliance Agent

Purpose:

Identify compliance risks.

Capabilities:

- Audit readiness
- Missing document detection
- Training compliance

Outputs:

- Compliance Score
- Findings
- Escalation Actions

KPIs:

False Positive Rate < 10%

------------------------------------------------

## AGENT-06

Name:
Root Cause Analysis Agent

Purpose:

Explain WHY a risk exists.

Capabilities:

- Explainability
- Causal analysis
- Driver identification

Outputs:

- Contributing Factors
- Confidence Level
- Business Narrative

------------------------------------------------

## AGENT-07

Name:
Recommendation Agent

Purpose:

Generate intervention recommendations.

Capabilities:

- Prescriptive analytics
- Action generation

Outputs:

- Recommended Action
- Business Impact
- Priority Score

------------------------------------------------

## AGENT-08

Name:
Clinical Operations Copilot

Purpose:

Natural language interface
for all platform intelligence.

Functions:

- Ask questions
- Generate reports
- Summarize risks
- Retrieve evidence
- Explain recommendations

# =================================================================
# SKILL REGISTRY
# =================================================================

Location:

.claude/skills/

Standard:

One skill = One business capability

Required Skills:

01_risk_scoring.md

02_enrollment_forecasting.md

03_site_performance.md

04_milestone_prediction.md

05_compliance_assessment.md

06_root_cause_analysis.md

07_recommendation_engine.md

08_document_retrieval.md

09_executive_reporting.md

10_study_health_scoring.md

------------------------------------------------

Skill Template

skill_name:

purpose:

inputs:

outputs:

tools:

evaluation_metrics:

# =================================================================
# AGENT COMMUNICATION PROTOCOL
# =================================================================

Format:

JSON

Transport:

Azure Service Bus

Message Schema:

{
  "event_id":"",
  "source_agent":"",
  "target_agent":"",
  "study_id":"",
  "risk_score":"",
  "timestamp":""
}

Event Types:

study_risk_detected

enrollment_risk_detected

site_risk_detected

compliance_alert

milestone_alert

report_generated

# =================================================================
# MCP SERVERS
# =================================================================

Location:

mcp/

MCP Required: YES

------------------------------------------------

CTMS MCP

Functions:

get_studies()

get_sites()

get_enrollment()

get_milestones()

get_resources()

------------------------------------------------

CAMP MCP

Functions:

startup_status()

activation_status()

approval_status()

------------------------------------------------

CORD MCP

Functions:

operational_metrics()

resource_metrics()

study_metrics()

------------------------------------------------

eTMF MCP

Functions:

retrieve_documents()

audit_status()

inspection_documents()

------------------------------------------------

SharePoint MCP

Functions:

search_documents()

retrieve_sops()

retrieve_lessons_learned()

# =================================================================
# RAG STRATEGY
# =================================================================

Required: YES

Purpose:

Provide grounded recommendations.

Knowledge Sources:

- SOPs
- Protocols
- eTMF Documents
- Monitoring Reports
- Audit Reports
- CAPA Documents
- Historical Studies
- Lessons Learned

Vector Database:

Azure AI Search

Alternative:

Pinecone

Weaviate

Embeddings:

text-embedding-3-large

Chunk Size:

1000

Overlap:

150

Metadata:

study_id

country

site

protocol

document_type

version

owner

effective_date

------------------------------------------------

Grounding Requirement

Every recommendation MUST contain:

- Risk Score
- Evidence
- Supporting Documents
- Explanation
- Recommendation

# =================================================================
# HOOKS
# =================================================================

Location:

.claude/hooks/

------------------------------------------------

Hook 01

Name:
pre_data_validation

Purpose:
Validate incoming data

Checks:

- Missing values
- Duplicate records
- Data freshness

------------------------------------------------

Hook 02

Name:
pre_risk_scoring

Purpose:
Validate study context

------------------------------------------------

Hook 03

Name:
post_risk_scoring

Purpose:
Create audit trail

Action:

write_audit_log()

------------------------------------------------

Hook 04

Name:
high_risk_alert

Condition:

risk_score > 0.85

Action:

send_notification()

------------------------------------------------

Hook 05

Name:
human_review_required

Conditions:

Compliance Risk
Audit Findings
Executive Reports

Action:

await_approval()

------------------------------------------------

Hook 06

Name:
rag_grounding_check

Purpose:

Ensure evidence exists.

Reject response if:

Evidence Missing

# =================================================================
# MEMORY STRATEGY
# =================================================================

Short-Term Memory

Redis

Retention:

24 Hours

------------------------------------------------

Long-Term Memory

PostgreSQL

Retention:

7 Years

For Audit Support

# =================================================================
# HUMAN APPROVAL MATRIX
# =================================================================

Requires Approval:

- Compliance Escalations
- Audit Findings
- Executive Reports
- Site Closure Recommendations
- Study Closure Recommendations

No Approval Required:

- Dashboards
- Risk Visualization
- Forecasts
- Reporting Drafts

# =================================================================
# GOVERNANCE
# =================================================================

Location:

governance/

Files:

guardrails.md

privacy.md

human_approval.md

# =================================================================
# AI GUARDRAILS
# =================================================================

The platform SHALL NOT:

- Modify patient records
- Recommend treatments
- Provide diagnosis
- Approve protocol amendments
- Submit regulatory filings
- Change clinical data
- Modify enrollment targets
- Approve CAPA plans

The platform MAY:

- Predict risks
- Explain risks
- Recommend actions
- Generate reports
- Retrieve evidence

# =================================================================
# COMPLIANCE REQUIREMENTS
# =================================================================

Must comply with:

ICH-GCP

21 CFR Part 11

HIPAA

GDPR

GDP

Internal AI Governance

# =================================================================
# OBSERVABILITY
# =================================================================

Location:

observability/

Frameworks:

Langfuse

OpenTelemetry

Azure Monitor

Application Insights

Grafana

------------------------------------------------

LLM Metrics

- Token Usage
- Prompt Tokens
- Completion Tokens
- Cost
- Latency

------------------------------------------------

Agent Metrics

- Execution Time
- Success Rate
- Retry Count
- Failure Rate

------------------------------------------------

RAG Metrics

- Retrieval Precision
- Retrieval Recall
- Groundedness
- Citation Rate

------------------------------------------------

MCP Metrics

- API Latency
- Availability
- Error Rate

------------------------------------------------

Prediction Metrics

- Accuracy
- MAE
- RMSE
- Precision
- Recall
- F1

# =================================================================
# TRACEABILITY
# =================================================================

Required: YES

Every action must be traceable.

Trace Chain:

User Request
      →
Agent
      →
Skill
      →
MCP Tool
      →
Retrieved Documents
      →
Model Version
      →
Prediction
      →
Recommendation
      →
Approval
      →
Audit Record

------------------------------------------------

Audit Record Schema

{
  "request_id":"",
  "session_id":"",
  "study_id":"",
  "agent":"",
  "skill":"",
  "documents_used":[],
  "model_version":"",
  "prediction":"",
  "confidence":"",
  "approved_by":"",
  "timestamp":""
}

# =================================================================
# EVALUATION FRAMEWORK
# =================================================================

Location:

evals/

Files:

golden_dataset.csv

llm_eval.py

rag_eval.py

agent_eval.py

------------------------------------------------

Enrollment Agent

Target Accuracy:

85%

------------------------------------------------

Site Agent

Target Precision:

80%

------------------------------------------------

Milestone Agent

Target Accuracy:

85%

------------------------------------------------

Compliance Agent

Target False Positive:

<10%

------------------------------------------------

Copilot

Groundedness:

>90%

Correctness:

>90%

Helpfulness:

>90%

# =================================================================
# CLINICAL OPERATIONS KPIs
# =================================================================

Enrollment

- Enrollment Velocity
- Recruitment Rate
- Screening Success Rate
- Enrollment Achievement %

------------------------------------------------

Site

- Site Activation Duration
- Site Productivity Score
- Protocol Deviations
- Query Resolution Time

------------------------------------------------

Milestone

- FPI Achievement
- LPI Achievement
- Database Lock Achievement
- Study Closeout Achievement

------------------------------------------------

Compliance

- Training Compliance %
- Audit Readiness %
- CAPA Closure %
- Inspection Findings

------------------------------------------------

AI Success Metrics

- Prediction Accuracy >85%
- Recommendation Acceptance >70%
- Manual Reporting Reduction >50%
- User Satisfaction >4.5/5
- Grounded Responses >90%

# =================================================================
# SECURITY
# =================================================================

Authentication:

Azure AD

Authorization:

RBAC

Data Classification:

Public
Internal
Confidential
Restricted

Encryption:

At Rest
In Transit

Audit Logging:

Mandatory

# =================================================================
# DEVELOPMENT PRINCIPLES
# =================================================================

Principle 1

All recommendations must be explainable.

Principle 2

Every prediction must have confidence scores.

Principle 3

Every recommendation must be grounded in evidence.

Principle 4

Every response must be auditable.

Principle 5

Human approval overrides AI decisions.

Principle 6

Prefer retrieval over hallucination.

Principle 7

Never expose PHI or PII.

Principle 8

Use specialist agents before general reasoning.

Principle 9

Measure everything.

Principle 10

Patient safety and regulatory compliance always take precedence.

# =================================================================
# DEFINITION OF SUCCESS
# =================================================================

The platform is successful when:

✓ Enrollment risks are detected proactively.

✓ Site risks are identified early.

✓ Milestone delays are predicted accurately.

✓ Compliance gaps are surfaced before audits.

✓ Study teams trust AI recommendations.

✓ Executive reporting effort is reduced.

✓ Clinical Operations users can interact using
  natural language through the Copilot.

✓ All AI decisions remain explainable,
  traceable and compliant.