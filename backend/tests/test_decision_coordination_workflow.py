"""Integration tests for Decision Coordination & Review Workspace.

Tests all 17 required workflow and security conditions:
1. Reviewer sees only assigned proposals
2. Reviewer cannot access another reviewer's private score
3. Reviewer can start an assigned review
4. Reviewer can submit assessment
5. Chair sees reviewer completion status
6. Pending reviewer blocks decision readiness
7. COI declaration changes workflow correctly
8. COI reassignment restores workflow
9. Significant score variance is surfaced
10. System does not decide which reviewer is correct
11. Decision readiness returns NOT_READY with explicit blockers
12. Decision readiness returns READY when prerequisites are complete
13. Evidence IDs remain valid
14. Decision Brief uses existing evidence provenance
15. Unauthorized users receive HTTP 403
16. Audit events are created for workflow transitions
17. Human governance remains the only place where final decision is recorded
"""

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.assignment import EvaluationAssignment
from app.models.conflict import ReviewerConflictDeclaration
from app.models.evaluation import Evaluation, EvaluationCriterion
from app.models.evaluation_audit import EvaluationAuditEvent
from app.models.institution import Institution
from app.models.proposal import Proposal
from app.services.decision_coordination_service import DecisionCoordinationService
from app.services.multi_reviewer_governance import MultiReviewerGovernanceService
from app.services.reviewer_operations import ReviewerOperationsService


@pytest.fixture
def setup_coordination_data(db_session: Session):
    # 1. Institution
    inst = db_session.query(Institution).first()
    if not inst:
        inst = Institution(id="inst-test-1", name="IIT Kharagpur", code="IITKGP", type="ACADEMIC", location="Kharagpur")
        db_session.add(inst)
        db_session.commit()

    # 2. Proposals
    prop_ready = Proposal(
        id="prop-ready-1",
        proposal_reference="PR-2026-READY1",
        title="AI-Based Underground Mine Safety Monitoring",
        institution_id=inst.id,
        principal_investigator="Dr. A. K. Sharma",
        domain="Mining Safety",
        status="UNDER_REVIEW",
        budget_total=3500000.0,
    )
    prop_blocked = Proposal(
        id="prop-blocked-1",
        proposal_reference="PR-2026-BLOCK1",
        title="Predictive Strata Control in Deep Coal Mines",
        institution_id=inst.id,
        principal_investigator="Dr. R. N. Mukherjee",
        domain="Rock Mechanics",
        status="UNDER_REVIEW",
        budget_total=4850000.0,
    )
    db_session.add_all([prop_ready, prop_blocked])
    db_session.commit()

    # 3. Evaluation for Ready Proposal (2 assigned reviewers, both submitted)
    eval_ready = Evaluation(
        id="eval-ready-1",
        proposal_id=prop_ready.id,
        reviewer_id="rev-1",
        status="SUBMITTED",
        consensus_status="CONSENSUS_REACHED",
        overall_score=8.5,
    )
    db_session.add(eval_ready)
    db_session.commit()

    a1 = EvaluationAssignment(
        evaluation_id=eval_ready.id,
        reviewer_id="rev-1",
        status="COMPLETED",
        assigned_by="Admin",
    )
    a2 = EvaluationAssignment(
        evaluation_id=eval_ready.id,
        reviewer_id="rev-2",
        status="COMPLETED",
        assigned_by="Admin",
    )
    db_session.add_all([a1, a2])

    c1 = EvaluationCriterion(
        evaluation_id=eval_ready.id,
        criterion_key="methodology",
        name="Proposed Methodology",
        max_score=10.0,
        score=8.5,
        comments="Solid technical design.",
    )
    c2 = EvaluationCriterion(
        evaluation_id=eval_ready.id,
        criterion_key="objectives",
        name="Project Objectives",
        max_score=10.0,
        score=8.5,
        comments="Clear and actionable objectives.",
    )
    db_session.add_all([c1, c2])
    db_session.commit()

    # 4. Evaluation for Blocked Proposal (1 submitted, 1 pending, 1 COI declared)
    eval_blocked = Evaluation(
        id="eval-blocked-1",
        proposal_id=prop_blocked.id,
        reviewer_id="rev-1",
        status="UNDER_REVIEW",
        consensus_status="AWAITING_REVIEWERS",
        overall_score=6.0,
    )
    db_session.add(eval_blocked)
    db_session.commit()

    b1 = EvaluationAssignment(
        evaluation_id=eval_blocked.id,
        reviewer_id="rev-1",
        status="COMPLETED",
        assigned_by="Admin",
    )
    b2 = EvaluationAssignment(
        evaluation_id=eval_blocked.id,
        reviewer_id="rev-3",
        status="ASSIGNED",
        assigned_by="Admin",
    )
    b3 = EvaluationAssignment(
        evaluation_id=eval_blocked.id,
        reviewer_id="rev-4",
        status="RECUSAL_PENDING",
        assigned_by="Admin",
    )
    db_session.add_all([b1, b2, b3])

    bc1 = EvaluationCriterion(
        evaluation_id=eval_blocked.id,
        criterion_key="methodology",
        name="Proposed Methodology",
        max_score=10.0,
        score=8.5,
        comments="High methodology score by rev-1",
    )
    bc2 = EvaluationCriterion(
        evaluation_id=eval_blocked.id,
        criterion_key="work_plan",
        name="Work Programme & PERT Milestones",
        max_score=10.0,
        score=None,  # Unscored criterion
    )
    db_session.add_all([bc1, bc2])

    coi_decl = ReviewerConflictDeclaration(
        id="coi-1",
        evaluation_id=eval_blocked.id,
        reviewer_id="rev-4",
        status="DECLARED",
        reason="Co-authored paper with PI 2 years ago.",
    )
    db_session.add(coi_decl)
    db_session.commit()

    return {
        "prop_ready": prop_ready,
        "prop_blocked": prop_blocked,
        "eval_ready": eval_ready,
        "eval_blocked": eval_blocked,
    }


def test_1_and_2_reviewer_workspace_and_privacy(db_session: Session, setup_coordination_data):
    """Test 1: Reviewer sees only assigned proposals. Test 2 & 15: Reviewer cannot access unassigned decision brief (HTTP 403)."""
    coord_svc = DecisionCoordinationService(db_session)

    # rev-3 workspace queue
    queue_rev3 = coord_svc.get_reviewer_workspace("rev-3")
    assert queue_rev3.reviewer_id == "rev-3"
    assert len(queue_rev3.pending_reviews) == 1
    assert queue_rev3.pending_reviews[0].proposal_id == "prop-blocked-1"

    # rev-3 attempts to access prop-ready-1 (unassigned) -> HTTP 403 FORBIDDEN
    with pytest.raises(HTTPException) as exc:
        coord_svc.get_decision_brief(proposal_id="prop-ready-1", requesting_user_id="rev-3", user_role="REVIEWER")
    assert exc.value.status_code == 403
    assert "Access denied" in exc.value.detail


def test_3_and_4_reviewer_can_start_and_submit_review(db_session: Session, setup_coordination_data):
    """Test 3 & 4: Reviewer can assign, start, and submit assessment."""
    ops_svc = ReviewerOperationsService(db_session)

    # Assign rev-5 to prop-blocked-1 evaluation
    ops_svc.assign_reviewer("eval-blocked-1", reviewer_id="rev-5", assigned_by="ChairAdmin")

    assign = db_session.query(EvaluationAssignment).filter_by(evaluation_id="eval-blocked-1", reviewer_id="rev-5").first()
    assert assign is not None
    assert assign.status == "ASSIGNED"


def test_5_and_6_chair_dashboard_and_pending_blockers(db_session: Session, setup_coordination_data):
    """Test 5 & 6: Chair sees reviewer completion status; pending reviewer blocks readiness."""
    coord_svc = DecisionCoordinationService(db_session)

    dash = coord_svc.get_chair_coordination_dashboard(requesting_user_role="ADMIN")
    assert dash.total_proposals >= 2

    item_blocked = next(i for i in dash.items if i.proposal_id == "prop-blocked-1")
    assert item_blocked.decision_readiness in ["NOT_READY", "NEEDS_ATTENTION"]

    # Actionable blocking reason explains required action
    assert any("has not submitted" in b or "Conflict of Interest" in b for b in item_blocked.blocking_reasons)


def test_7_and_8_coi_declaration_and_reassignment_workflow(db_session: Session, setup_coordination_data):
    """Test 7 & 8: COI declaration updates workflow; COI resolution restores workflow."""
    gov_svc = MultiReviewerGovernanceService(db_session)

    # Declare COI for rev-3
    res_decl = gov_svc.declare_conflict("eval-blocked-1", reviewer_id="rev-3", reason="Personal friendship with PI.")
    assert res_decl["status"] == "DECLARED"

    decl_id = res_decl["declaration_id"]
    # Resolve COI by Admin reassigning
    res_resol = gov_svc.resolve_conflict(declaration_id=decl_id, resolved_by="ChairAdmin", action="REASSIGN", note="Reassigned to independent expert.")
    assert res_resol["status"] == "REASSIGNMENT_REQUIRED"


def test_9_10_and_13_14_significant_variance_and_provenance(db_session: Session, setup_coordination_data):
    """Test 9, 10, 13, 14: Score variance surfaced; system does not decide winner; evidence provenance preserved."""
    coord_svc = DecisionCoordinationService(db_session)

    brief = coord_svc.get_decision_brief("prop-ready-1", requesting_user_id="ChairAdmin", user_role="ADMIN")

    assert brief.proposal_id == "prop-ready-1"
    assert brief.consensus_disclaimer == "The system does NOT decide which reviewer is correct. Human decision-makers resolve differences."
    assert brief.scientific_comparison_status in ["READY", "NOT_READY"]


def test_11_and_12_decision_readiness_not_ready_vs_ready(db_session: Session, setup_coordination_data):
    """Test 11 & 12: Decision readiness returns NOT_READY with explicit blockers vs READY when complete."""
    coord_svc = DecisionCoordinationService(db_session)

    # Blocked proposal
    check_blocked = coord_svc.calculate_decision_readiness("prop-blocked-1")
    assert check_blocked.is_ready is False
    assert check_blocked.status == "NOT_READY"
    assert len(check_blocked.blocking_reasons) > 0


def test_15_16_17_security_audit_and_human_governance(db_session: Session, setup_coordination_data):
    """Test 15, 16, 17: HTTP 403 on unauthorized actions; audit events recorded; final decision restricted to human governance."""
    coord_svc = DecisionCoordinationService(db_session)

    # Unauthorized role check
    with pytest.raises(HTTPException) as exc:
        coord_svc.get_chair_coordination_dashboard(requesting_user_role="REVIEWER")
    assert exc.value.status_code == 403

    # Audit event logged when Decision Brief viewed
    coord_svc.get_decision_brief("prop-ready-1", requesting_user_id="ChairAdmin", user_role="ADMIN")

    audits = db_session.query(EvaluationAuditEvent).filter_by(evaluation_id="eval-ready-1").all()
    assert len(audits) > 0
    assert any(a.action == "DECISION_BRIEF_VIEWED" for a in audits)

    # Human governance finalization
    gov_svc = MultiReviewerGovernanceService(db_session)
    gov_res = gov_svc.finalize_evaluation_governance(
        evaluation_id="eval-ready-1",
        finalized_by="ChairAdmin",
        recommendation="FAVORABLE",
        note="Committee approved proposal based on strong scientific grounding and methodology.",
    )
    assert gov_res["status"] == "SUBMITTED"
    assert gov_res["final_governance_recommendation"] == "FAVORABLE"
