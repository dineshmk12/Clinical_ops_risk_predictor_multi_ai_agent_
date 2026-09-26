"""Synthetic CTMS/CAMP/CORD data generator — stands in for real Eli Lilly
clinical operations systems in this local prototype. Run as a script to
(re)seed the SQLite database and knowledge base used by the platform.
"""
import random
from datetime import date, timedelta
from pathlib import Path

from faker import Faker

from app.db import Base, SessionLocal, engine
from app.models import (
    Study,
    Site,
    EnrollmentRecord,
    Milestone,
    Deviation,
    Query,
    Resource,
    Document,
    TrainingCompliance,
)

fake = Faker()
random.seed(42)
Faker.seed(42)

KB_DIR = Path(__file__).parent / "knowledge_base"

THERAPEUTIC_AREAS = ["Oncology", "Diabetes", "Immunology", "Neuroscience", "Cardiology"]
COUNTRIES = ["United States", "Germany", "Japan", "Brazil", "India", "United Kingdom"]
MILESTONE_TYPES = ["Study Startup", "FPI", "LPI", "DB Lock", "CSR", "Closeout"]
ROLES = ["CRA", "Study Manager", "Clinical Trial Manager", "Data Manager", "Biostatistician"]

STUDY_PROFILES = [
    dict(study_id="STU-1001", name="Lilly-ONCO-Phase3-Trial", phase="Phase 3", therapeutic_area="Oncology", health="at_risk"),
    dict(study_id="STU-1002", name="Lilly-DIAB-Phase2-Trial", phase="Phase 2", therapeutic_area="Diabetes", health="healthy"),
    dict(study_id="STU-1003", name="Lilly-IMMU-Phase3-Trial", phase="Phase 3", therapeutic_area="Immunology", health="critical"),
    dict(study_id="STU-1004", name="Lilly-NEURO-Phase1-Trial", phase="Phase 1", therapeutic_area="Neuroscience", health="healthy"),
    dict(study_id="STU-1005", name="Lilly-CARD-Phase2-Trial", phase="Phase 2", therapeutic_area="Cardiology", health="at_risk"),
]


def _wipe():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def _seed_studies(db):
    studies = []
    for profile in STUDY_PROFILES:
        study = Study(
            study_id=profile["study_id"],
            name=profile["name"],
            phase=profile["phase"],
            therapeutic_area=profile["therapeutic_area"],
            status="Active",
            country=random.choice(COUNTRIES),
            target_enrollment=random.randint(150, 600),
            start_date=date.today() - timedelta(days=random.randint(200, 500)),
        )
        db.add(study)
        studies.append((study, profile["health"]))
    db.commit()
    return studies


def _seed_sites(db, study, health):
    sites = []
    n_sites = random.randint(4, 8)
    for i in range(n_sites):
        site_id = f"{study.study_id}-SITE-{i+1:02d}"
        planned = study.start_date + timedelta(days=random.randint(10, 60))
        delay_days = 0
        if health in ("at_risk", "critical") and random.random() < 0.5:
            delay_days = random.randint(15, 90)
        actual = planned + timedelta(days=delay_days) if delay_days or random.random() < 0.8 else None
        site = Site(
            site_id=site_id,
            study_id=study.study_id,
            country=random.choice(COUNTRIES),
            pi_name=fake.name(),
            status="Active",
            planned_activation_date=planned,
            actual_activation_date=actual,
        )
        db.add(site)
        sites.append(site)
    db.commit()
    return sites


def _seed_enrollment(db, study, sites, health):
    target_weekly = study.target_enrollment / 26  # ~6 month enrollment window baseline
    factor = {"healthy": 1.05, "at_risk": 0.65, "critical": 0.35}[health]
    for week in range(26):
        d = date.today() - timedelta(weeks=(26 - week))
        for site in sites:
            screened = max(0, int(random.gauss(target_weekly / len(sites) * 1.3, 1.5)))
            enrolled = max(0, int(screened * factor * random.uniform(0.5, 0.9)))
            db.add(
                EnrollmentRecord(
                    study_id=study.study_id,
                    site_id=site.site_id,
                    date=d,
                    subjects_screened=screened,
                    subjects_enrolled=enrolled,
                )
            )
    db.commit()


def _seed_milestones(db, study, health):
    offset = 0
    for m_type in MILESTONE_TYPES:
        offset += random.randint(30, 90)
        planned = study.start_date + timedelta(days=offset)
        delay = 0
        if health == "critical":
            delay = random.randint(20, 120)
        elif health == "at_risk":
            delay = random.randint(5, 45) if random.random() < 0.6 else 0
        is_past = planned + timedelta(days=delay) < date.today()
        actual = planned + timedelta(days=delay) if is_past else None
        status = "Completed" if actual else ("At Risk" if delay > 0 else "On Track")
        db.add(
            Milestone(
                study_id=study.study_id,
                milestone_type=m_type,
                planned_date=planned,
                actual_date=actual,
                status=status,
            )
        )
    db.commit()


def _seed_deviations_and_queries(db, study, sites, health):
    severity_weights = {"healthy": [0.7, 0.25, 0.05], "at_risk": [0.5, 0.35, 0.15], "critical": [0.3, 0.4, 0.3]}
    weights = severity_weights[health]
    for site in sites:
        for _ in range(random.randint(1, 6)):
            db.add(
                Deviation(
                    study_id=study.study_id,
                    site_id=site.site_id,
                    date=date.today() - timedelta(days=random.randint(1, 180)),
                    severity=random.choices(["Minor", "Major", "Critical"], weights=weights)[0],
                    description=fake.sentence(nb_words=10),
                )
            )
        for _ in range(random.randint(2, 10)):
            opened = date.today() - timedelta(days=random.randint(1, 120))
            resolution_days = random.randint(1, 10) if health == "healthy" else random.randint(5, 45)
            closed = opened + timedelta(days=resolution_days) if random.random() < 0.7 else None
            db.add(
                Query(
                    study_id=study.study_id,
                    site_id=site.site_id,
                    opened_date=opened,
                    closed_date=closed if closed and closed <= date.today() else None,
                    status="Closed" if closed and closed <= date.today() else "Open",
                )
            )
        db.add(
            TrainingCompliance(
                study_id=study.study_id,
                site_id=site.site_id,
                role=random.choice(ROLES),
                training_complete_pct=round(random.uniform(60, 100) if health != "healthy" else random.uniform(85, 100), 1),
            )
        )
    db.commit()


def _seed_resources(db, study, health):
    strain = {"healthy": 1.0, "at_risk": 0.8, "critical": 0.55}[health]
    for role in ROLES:
        required = round(random.uniform(1.0, 4.0), 1)
        db.add(
            Resource(
                study_id=study.study_id,
                role=role,
                required_fte=required,
                allocated_fte=round(required * strain, 1),
            )
        )
    db.commit()


KNOWLEDGE_DOCS = [
    dict(
        doc_id="SOP-001",
        doc_type="SOP",
        title="SOP: Site Activation and Monitoring Visit Cadence",
        owner="Clinical Operations QA",
        content=(
            "Standard Operating Procedure: Site Activation and Monitoring Visit Cadence.\n\n"
            "Purpose: Define the required cadence of site monitoring visits based on enrollment "
            "velocity and protocol deviation frequency.\n\n"
            "Policy: Sites with more than 2 major protocol deviations in a rolling 90-day window "
            "must be escalated to a monthly monitoring cadence, down from the standard quarterly "
            "cadence. Sites with a query resolution time exceeding 30 days must receive a Corrective "
            "and Preventive Action (CAPA) plan within 10 business days of detection. Site activation "
            "delays beyond 60 days from planned activation date require documented root cause "
            "analysis and a recovery plan submitted to the Study Manager."
        ),
    ),
    dict(
        doc_id="SOP-002",
        doc_type="SOP",
        title="SOP: Enrollment Risk Escalation Thresholds",
        owner="Clinical Operations QA",
        content=(
            "Standard Operating Procedure: Enrollment Risk Escalation Thresholds.\n\n"
            "Purpose: Standardize when enrollment shortfalls trigger management escalation.\n\n"
            "Policy: If actual enrollment velocity falls below 70% of the planned enrollment curve "
            "for two consecutive months, the study is classified 'At Risk' and an Enrollment Recovery "
            "Plan is required. If velocity falls below 40% of plan, the study is classified 'Critical' "
            "and requires immediate portfolio-level review by the Clinical Operations Manager and "
            "consideration of additional site activation or country expansion."
        ),
    ),
    dict(
        doc_id="PROT-001",
        doc_type="Protocol",
        title="Protocol Excerpt: Screening and Enrollment Procedures",
        owner="Medical Affairs",
        content=(
            "Protocol Section 5: Screening and Enrollment Procedures.\n\n"
            "Subjects must complete screening assessments within 28 days prior to randomization. "
            "Sites experiencing a screen failure rate above 40% should review inclusion/exclusion "
            "criteria interpretation with the medical monitor, as this is a leading indicator of "
            "downstream enrollment shortfall."
        ),
    ),
    dict(
        doc_id="CAPA-001",
        doc_type="CAPA",
        title="CAPA-2025-014: Recurrent Informed Consent Deviations",
        owner="Quality Assurance",
        content=(
            "CAPA Record CAPA-2025-014.\n\n"
            "Finding: Recurrent informed consent version-control deviations identified across "
            "multiple sites during routine monitoring, driven by delayed distribution of updated "
            "consent forms following protocol amendments.\n\n"
            "Corrective Action: Centralized consent-form distribution checklist introduced, "
            "requiring CRA sign-off within 5 business days of amendment approval.\n\n"
            "Preventive Action: Quarterly audit of consent form versions in use at each active site."
        ),
    ),
    dict(
        doc_id="LL-001",
        doc_type="Lessons Learned",
        title="Lessons Learned: Late Site Activation Recovery",
        owner="Clinical Operations",
        content=(
            "Lessons Learned Repository Entry: Late Site Activation Recovery.\n\n"
            "Across prior oncology studies, sites that activated more than 45 days behind plan "
            "rarely closed the enrollment gap organically. Studies that added 2-3 backup sites in "
            "high-performing countries within 60 days of detecting the delay recovered target "
            "enrollment on average 3 months faster than studies that waited for existing sites to "
            "ramp up. Early country-level reallocation of enrollment targets is the most effective "
            "recovery lever observed."
        ),
    ),
    dict(
        doc_id="AUD-001",
        doc_type="Audit Report",
        title="Audit Report Excerpt: Training Compliance Findings",
        owner="Quality Assurance",
        content=(
            "Audit Report Excerpt.\n\n"
            "Finding: Sites with training compliance below 80% for GCP refresher modules showed a "
            "statistically higher rate of protocol deviations in the subsequent quarter. Audit "
            "readiness scoring should weight training compliance percentage alongside document "
            "completeness in eTMF when calculating overall site audit readiness."
        ),
    ),
]


def _write_knowledge_base_files():
    KB_DIR.mkdir(exist_ok=True)
    for doc in KNOWLEDGE_DOCS:
        (KB_DIR / f"{doc['doc_id']}.txt").write_text(doc["content"], encoding="utf-8")


def _seed_documents(db, studies):
    for doc in KNOWLEDGE_DOCS:
        db.add(
            Document(
                doc_id=doc["doc_id"],
                study_id=None,
                doc_type=doc["doc_type"],
                title=doc["title"],
                content_path=str(KB_DIR / f"{doc['doc_id']}.txt"),
                version="1.0",
                owner=doc["owner"],
                effective_date=date.today() - timedelta(days=random.randint(30, 400)),
            )
        )
    db.commit()


def seed():
    _wipe()
    _write_knowledge_base_files()
    db = SessionLocal()
    try:
        studies = _seed_studies(db)
        for study, health in studies:
            sites = _seed_sites(db, study, health)
            _seed_enrollment(db, study, sites, health)
            _seed_milestones(db, study, health)
            _seed_deviations_and_queries(db, study, sites, health)
            _seed_resources(db, study, health)
        _seed_documents(db, studies)
    finally:
        db.close()
    print("Seed complete: 5 studies, synthetic sites/enrollment/milestones/deviations/resources, "
          f"and {len(KNOWLEDGE_DOCS)} knowledge-base documents written to {KB_DIR}")


if __name__ == "__main__":
    seed()
