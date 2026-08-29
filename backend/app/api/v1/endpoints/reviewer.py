from fastapi import APIRouter, Depends, Query, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.decision_coordination import (
    ChairDashboardResponse,
    DecisionBriefResponse,
    DecisionReadinessCheck,
    ReviewerWorkspaceQueue,
)
from app.services.decision_coordination_service import DecisionCoordinationService
from app.services.reviewer_operations import ReviewerOperationsService

router = APIRouter()


class ReviewerAssignPayload(BaseModel):
    reviewer_id: str
    assigned_by: str = "Admin"


class ReturnForRevisionPayload(BaseModel):
    returned_by: str
    reason: str


class DeclareConflictPayload(BaseModel):
    reviewer_id: str
    reason: str


class ResolveConflictPayload(BaseModel):
    resolved_by: str
    action: str  # CLEAR or REASSIGN
    note: str | None = None


class FinalizeGovernancePayload(BaseModel):
    finalized_by: str
    recommendation: str  # FAVORABLE, FAVORABLE_WITH_CONDITIONS, REQUIRES_REVISION, NOT_RECOMMENDED
    note: str


@router.get("/reviewer/workspace", summary="Get Reviewer Workspace Queue", response_model=ReviewerWorkspaceQueue)
def get_reviewer_workspace(
    reviewer_id: str = Query(..., description="Reviewer ID"),
    db: Session = Depends(get_db),
):
    """Retrieve focused reviewer workspace queue grouped by pending, completed, and COI reviews."""
    service = DecisionCoordinationService(db)
    return service.get_reviewer_workspace(reviewer_id=reviewer_id)


@router.get("/chair/dashboard", summary="Get Chair Coordination Dashboard", response_model=ChairDashboardResponse)
def get_chair_coordination_dashboard(
    role: str = Query("ADMIN", description="User role (ADMIN or CHAIR required)"),
    db: Session = Depends(get_db),
):
    """Retrieve authorized Chair/Admin reviewer coordination dashboard displaying progress, consensus, and blockers."""
    service = DecisionCoordinationService(db)
    return service.get_chair_coordination_dashboard(requesting_user_role=role)


@router.get("/proposals/{proposal_id}/decision-readiness", summary="Check Decision Readiness", response_model=DecisionReadinessCheck)
def get_decision_readiness(
    proposal_id: str,
    db: Session = Depends(get_db),
):
    """Deterministically calculate proposal workflow decision readiness and return explicit blocking reasons."""
    service = DecisionCoordinationService(db)
    return service.calculate_decision_readiness(proposal_id=proposal_id)


@router.get("/proposals/{proposal_id}/decision-brief", summary="Get Proposal Decision Brief", response_model=DecisionBriefResponse)
def get_decision_brief(
    proposal_id: str,
    reviewer_id: str | None = Query(None, description="Requesting reviewer ID"),
    role: str = Query("ADMIN", description="User role"),
    db: Session = Depends(get_db),
):
    """Retrieve comprehensive decision-ready brief summarizing proposal, evidence, rubric, consensus, and outstanding actions."""
    service = DecisionCoordinationService(db)
    return service.get_decision_brief(proposal_id=proposal_id, requesting_user_id=reviewer_id, user_role=role)


@router.get("/reviewer/queue", summary="Get reviewer assignment queue")
def get_reviewer_queue(
    reviewer_id: str = Query(..., description="Reviewer ID"),
    status: str | None = Query(None, description="Filter queue by status"),
    db: Session = Depends(get_db),
):
    """Retrieve assigned evaluations queue for a specific reviewer."""
    service = ReviewerOperationsService(db)
    return service.get_reviewer_queue(reviewer_id=reviewer_id, status_filter=status)


@router.post("/evaluations/{evaluation_id}/assign", summary="Assign evaluation to reviewer")
def assign_reviewer(
    evaluation_id: str,
    payload: ReviewerAssignPayload,
    db: Session = Depends(get_db),
):
    """Assign an evaluation to a designated reviewer and update workflow status."""
    service = ReviewerOperationsService(db)
    return service.assign_reviewer(
        evaluation_id=evaluation_id,
        reviewer_id=payload.reviewer_id,
        assigned_by=payload.assigned_by,
    )


@router.post("/evaluations/{evaluation_id}/return", summary="Return evaluation for revision")
def return_for_revision(
    evaluation_id: str,
    payload: ReturnForRevisionPayload,
    db: Session = Depends(get_db),
):
    """Return a submitted/under-review evaluation back for revision requiring a human reason."""
    service = ReviewerOperationsService(db)
    return service.return_for_revision(
        evaluation_id=evaluation_id,
        returned_by=payload.returned_by,
        reason=payload.reason,
    )


@router.post("/evaluations/{evaluation_id}/conflicts", summary="Declare conflict of interest")
def declare_conflict(
    evaluation_id: str,
    payload: DeclareConflictPayload,
    db: Session = Depends(get_db),
):
    """Declare a reviewer conflict of interest requiring human admin resolution."""
    from app.services.multi_reviewer_governance import MultiReviewerGovernanceService
    service = MultiReviewerGovernanceService(db)
    return service.declare_conflict(
        evaluation_id=evaluation_id,
        reviewer_id=payload.reviewer_id,
        reason=payload.reason,
    )


@router.post("/conflicts/{declaration_id}/resolve", summary="Resolve conflict declaration")
def resolve_conflict(
    declaration_id: str,
    payload: ResolveConflictPayload,
    db: Session = Depends(get_db),
):
    """Admin resolution of conflict declaration (CLEAR or REASSIGN)."""
    from app.services.multi_reviewer_governance import MultiReviewerGovernanceService
    service = MultiReviewerGovernanceService(db)
    return service.resolve_conflict(
        declaration_id=declaration_id,
        resolved_by=payload.resolved_by,
        action=payload.action,
        note=payload.note,
    )


@router.get("/evaluations/{evaluation_id}/reviewer-comparison", summary="Get multi-reviewer comparison")
def get_reviewer_comparison(
    evaluation_id: str,
    reviewer_id: str | None = Query(None, description="Requesting reviewer ID"),
    role: str = Query("ADMIN", description="User role"),
    db: Session = Depends(get_db),
):
    """Retrieve multi-reviewer score comparison with blinding policy enforcement."""
    from app.services.multi_reviewer_governance import MultiReviewerGovernanceService
    service = MultiReviewerGovernanceService(db)
    return service.get_reviewer_comparison(
        evaluation_id=evaluation_id,
        requesting_reviewer_id=reviewer_id,
        user_role=role,
    )


@router.post("/evaluations/{evaluation_id}/finalize-governance", summary="Finalize human governance recommendation")
def finalize_governance(
    evaluation_id: str,
    payload: FinalizeGovernancePayload,
    db: Session = Depends(get_db),
):
    """Finalize institutional governance evaluation record with human recommendation and explanation note."""
    from app.services.multi_reviewer_governance import MultiReviewerGovernanceService
    service = MultiReviewerGovernanceService(db)
    return service.finalize_evaluation_governance(
        evaluation_id=evaluation_id,
        finalized_by=payload.finalized_by,
        recommendation=payload.recommendation,
        note=payload.note,
    )


@router.get("/reports/export.csv", summary="Export operational register CSV")
def export_operational_csv(db: Session = Depends(get_db)):
    """Export proposal and evaluation operational registers as CSV file."""
    service = ReviewerOperationsService(db)
    csv_data = service.export_operational_csv()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=naccer_evaluations_register.csv"},
    )
