from app.skills import (
    compliance_assessment,
    document_retrieval,
    enrollment_forecasting,
    executive_reporting,
    milestone_prediction,
    recommendation_engine,
    risk_scoring,
    root_cause_analysis,
    site_performance,
    study_health_scoring,
)

STUDY_ID = "STU-1003"  # seeded as "critical" health profile


def test_risk_scoring_weighted_aggregation():
    score = risk_scoring.compute_risk_score({"a": 1.0, "b": 0.0}, weights={"a": 1.0, "b": 1.0})
    assert score == 0.5


def test_risk_scoring_empty_components():
    assert risk_scoring.compute_risk_score({}) == 0.0


def test_risk_tier_boundaries():
    assert risk_scoring.risk_tier(0.9) == "Critical"
    assert risk_scoring.risk_tier(0.5) == "At Risk"
    assert risk_scoring.risk_tier(0.1) == "Healthy"


def test_study_health_scoring_shape():
    result = study_health_scoring.compute(STUDY_ID)
    assert result["study_id"] == STUDY_ID
    assert 0 <= result["health_score"] <= 100
    assert result["health_trend"] in ("Improving", "Declining", "Stable")
    assert isinstance(result["health_summary"], str) and result["health_summary"]
    assert 0 <= result["confidence"] <= 1


def test_enrollment_forecasting_shape():
    result = enrollment_forecasting.forecast(STUDY_ID)
    assert result["study_id"] == STUDY_ID
    assert "delay_probability" in result
    assert 0 <= result["delay_probability"] <= 1
    assert 0 <= result["confidence"] <= 1


def test_site_performance_scores_sorted_descending():
    sites = site_performance.score_sites(STUDY_ID)
    assert sites
    risk_scores = [s["risk_score"] for s in sites]
    assert risk_scores == sorted(risk_scores, reverse=True)
    for site in sites:
        assert 0 <= site["risk_score"] <= 1


def test_milestone_prediction_shape():
    milestones = milestone_prediction.predict(STUDY_ID)
    assert milestones
    for m in milestones:
        assert m["milestone_type"]
        assert 0 <= m["delay_probability"] <= 1


def test_compliance_assessment_shape():
    result = compliance_assessment.assess(STUDY_ID)
    assert result["risk_tier"] in ("Healthy", "At Risk", "Critical")
    assert isinstance(result["findings"], list)
    assert isinstance(result["escalation_actions"], list)
    assert result["false_positive_estimate"] < 0.10


def test_document_retrieval_returns_evidence():
    evidence = document_retrieval.retrieve_evidence("site activation monitoring visit cadence")
    assert evidence
    assert "doc_id" in evidence[0]


def test_root_cause_analysis_shape():
    result = root_cause_analysis.analyze(STUDY_ID)
    assert result["confidence_level"] in ("High", "Medium", "Low")
    assert isinstance(result["contributing_factors"], list)
    assert isinstance(result["evidence"], list)


def test_recommendation_engine_shape():
    result = recommendation_engine.generate(STUDY_ID)
    assert result["recommended_action"]
    assert 0 <= result["priority_score"] <= 1
    assert isinstance(result["supporting_documents"], list)


def test_executive_reporting_shape():
    report = executive_reporting.build_report(STUDY_ID)
    assert report["study_id"] == STUDY_ID
    assert 0 <= report["health_score"] <= 100
    assert "site_summary" in report
