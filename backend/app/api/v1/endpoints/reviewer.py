from fastapi import APIRouter, Depends, Query, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.reviewer_operations import ReviewerOperationsService

router = APIRouter()


class ReviewerAssignPayload(BaseModel):
    reviewer_id: str
    assigned_by: str = "Admin"


class ReturnForRevisionPayload(BaseModel):
    returned_by: str
    reason: str


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
