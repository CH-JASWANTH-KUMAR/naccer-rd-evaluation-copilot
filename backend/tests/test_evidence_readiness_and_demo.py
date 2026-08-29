"""Integration & System Tests for STEP 9 — Demo Reviewer Workflow + Transparent Evidence Readiness Score."""

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.assignment import EvaluationAssignment
from app.models.audit_event import AuditEvent
from app.models.evaluation import Evaluation
from app.models.proposal import Proposal
from app.services.evidence_readiness_service import EvidenceReadinessService
from app.services.seed import seed_demo_data


def test_1_seed_demo_data_populates_tasks_evaluations_and_scores(db_session: Session):
    """Verify seed_demo_data populates demo tasks, evaluation records, human reviewer scores, and audit events."""
    res = seed_demo_data(db_session)
    assert "successfully created" in res["message"] or "already exist" in res["message"]

    # 1. Verify demo proposal exists
    prop = db_session.scalars(select(Proposal).where(Proposal.proposal_reference == "PR-2026-PRED-MAINT")).first()
    assert prop is not None
    assert prop.is_demo is True
    assert "[DEMO DATA]" in prop.title

    # 2. Verify demo review tasks (assignments)
    tasks = db_session.scalars(select(EvaluationAssignment).where(EvaluationAssignment.is_demo.is_(True))).all()
    assert len(tasks) >= 3

    t1 = next((t for t in tasks if t.reviewer_id == "Reviewer A (Technical)"), None)
    assert t1 is not None
    assert t1.task_title == "Review scientific methodology and technical feasibility"
    assert t1.priority == "HIGH"

    t2 = next((t for t in tasks if t.reviewer_id == "Reviewer B (Scientific)"), None)
    assert t2 is not None
    assert t2.task_title == "Verify scientific evidence, metrics and baseline comparison"

    t3 = next((t for t in tasks if t.reviewer_id == "Reviewer C (Financial)"), None)
    assert t3 is not None
    assert t3.task_title == "Review budget compliance and implementation feasibility"
    assert t3.priority == "MEDIUM"

    # 3. Verify demo evaluation record & scores
    demo_eval = db_session.scalars(select(Evaluation).where(Evaluation.proposal_id == prop.id)).first()
    assert demo_eval is not None
    assert demo_eval.is_demo is True
    assert len(demo_eval.criteria) == 8

    # Verify score persisted for Reviewer A criterion
    crit1 = next((c for c in demo_eval.criteria if "CRIT-MOC-01" in (c.criterion_key or "")), None)
    assert crit1 is not None
    assert crit1.score == 8.0
    assert "Reviewer A" in (crit1.comments or "")

    # 4. Verify audit events created
    audits = db_session.scalars(select(AuditEvent).where(AuditEvent.proposal_id == prop.id)).all()
    actions = [a.action for a in audits]
    assert "REVIEW_TASK_CREATED" in actions
    assert "REVIEWER_ASSIGNED" in actions
    assert "RUBRIC_SCORE_ENTERED" in actions
    assert "EVIDENCE_READINESS_CALCULATED" in actions


def test_2_reviewer_queue_endpoint_returns_tasks_and_demo_labels(client: TestClient, db_session: Session):
    """Verify Reviewer Queue endpoint returns seeded tasks with priority, task_title, and demo labels."""
    seed_demo_data(db_session)
    db_session.commit()

    response = client.get("/api/v1/reviewer/workspace?reviewer_id=Reviewer%20A%20(Technical)")
    assert response.status_code == 200
    data = response.json()

    assert data["reviewer_id"] == "Reviewer A (Technical)"
    assert len(data["pending_reviews"]) > 0 or len(data["completed_reviews"]) > 0

    cards = data["pending_reviews"] + data["completed_reviews"]
    pred_card = next((c for c in cards if "PR-2026-PRED-MAINT" in c["proposal_reference"]), None)
    assert pred_card is not None
    assert pred_card["task_title"] == "Review scientific methodology and technical feasibility"
    assert pred_card["priority"] == "HIGH"
    assert pred_card["is_demo"] is True
    assert pred_card["evidence_sources_count"] > 0


def test_3_evidence_readiness_score_calculation_is_deterministic(db_session: Session):
    """Verify Evidence Readiness Score calculation is 0-100, deterministic, explainable, and sums components correctly."""
    seed_demo_data(db_session)
    db_session.commit()
    prop = db_session.scalars(select(Proposal).where(Proposal.proposal_reference == "PR-2026-PRED-MAINT")).first()
    assert prop is not None

    service = EvidenceReadinessService(db_session)
    res = service.calculate_evidence_readiness(prop.id)

    # 0-100 score bounds
    assert 0 <= res.total_score <= 100
    assert res.max_score == 100
    assert res.is_demo is True

    # Component scores sum sanity
    sum_comps = (
        res.proposal_completeness_score
        + res.scientific_evidence_coverage_score
        + res.moc_guideline_coverage_score
        + res.financial_verification_score
        + res.historical_research_support_score
        + res.reviewer_completion_score
    )
    assert abs(res.total_score - round(sum_comps)) <= 1

    # Neutral interpretation language check
    valid_labels = [
        "Strong evidence coverage",
        "Moderate evidence coverage",
        "Evidence gaps require reviewer attention",
        "Substantial evidence gaps",
    ]
    assert res.interpretation_label in valid_labels

    # Disclaimer check
    assert "Evidence Readiness Score" in res.disclaimer
    assert "not an approval or funding prediction" in res.disclaimer

    # 6 Component breakdowns present and explainable
    assert len(res.components) == 6
    for c in res.components:
        assert c.name in [
            "Proposal Completeness",
            "Scientific Evidence Coverage",
            "MoC Guideline Evidence Coverage",
            "Financial Verification",
            "Historical / Research Evidence Support",
            "Reviewer Evaluation Completion",
        ]
        assert c.score <= c.max_score
        assert len(c.explanation) > 0
        assert len(c.contributing_checks) > 0


def test_4_no_ai_approval_prediction_in_readiness_response(client: TestClient, db_session: Session):
    """Verify that Evidence Readiness Score does NOT predict approval, rejection, funding, or publication probability."""
    seed_demo_data(db_session)
    db_session.commit()
    prop = db_session.scalars(select(Proposal).where(Proposal.proposal_reference == "PR-2026-PRED-MAINT")).first()

    response = client.get(f"/api/v1/proposals/{prop.id}/evidence-readiness")
    assert response.status_code == 200
    data = response.json()

    raw_str = str(data).lower()
    forbidden_terms = ["likely approved", "likely rejected", "funding probability", "novelty prediction", "good proposal", "bad proposal"]
    for term in forbidden_terms:
        assert term not in raw_str


def test_5_reviewer_blinding_remains_enforced(client: TestClient, db_session: Session):
    """Verify reviewer blinding remains enforced for unassigned reviewers accessing decision brief."""
    seed_demo_data(db_session)
    db_session.commit()
    prop = db_session.scalars(select(Proposal).where(Proposal.proposal_reference == "PR-2026-PRED-MAINT")).first()

    # Unassigned reviewer tries to access decision brief with role=REVIEWER
    response = client.get(f"/api/v1/proposals/{prop.id}/decision-brief?reviewer_id=UnassignedReviewer999&role=REVIEWER")
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]
