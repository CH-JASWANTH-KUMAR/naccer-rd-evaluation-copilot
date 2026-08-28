from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.evaluation import (
    EvaluationCreate,
    EvaluationEvidenceCreate,
    EvaluationRead,
    EvaluationUpdate,
)
from app.services.evaluation_service import EvaluationService

router = APIRouter()


@router.post(
    "",
    response_model=EvaluationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create Evaluation for Proposal",
)
def create_evaluation(
    data: EvaluationCreate,
    db: Session = Depends(get_db),
):
    """Create a new evaluation workspace for a proposal, binding the active rubric version."""
    service = EvaluationService(db)
    return service.create_evaluation(data)


@router.get("", response_model=list[EvaluationRead], summary="List evaluations")
def list_evaluations(
    proposal_id: str | None = Query(None, description="Filter by proposal ID"),
    status: str | None = Query(None, description="Filter by evaluation status"),
    db: Session = Depends(get_db),
):
    """Retrieve evaluations directory list."""
    service = EvaluationService(db)
    return service.get_evaluations_list(proposal_id=proposal_id, status_filter=status)


@router.get("/{evaluation_id}", response_model=EvaluationRead, summary="Get evaluation by ID")
def get_evaluation(evaluation_id: str, db: Session = Depends(get_db)):
    """Retrieve detailed evaluation record with criteria scores and evidence."""
    service = EvaluationService(db)
    return service.get_evaluation_by_id(evaluation_id)


@router.patch("/{evaluation_id}", response_model=EvaluationRead, summary="Update evaluation draft")
def update_evaluation_draft(
    evaluation_id: str,
    payload: EvaluationUpdate,
    db: Session = Depends(get_db),
):
    """Update evaluation draft criteria scores, comments, justification notes, and recommendation."""
    service = EvaluationService(db)
    return service.update_evaluation_draft(evaluation_id, payload)


@router.post("/{evaluation_id}/submit", response_model=EvaluationRead, summary="Submit evaluation")
def submit_evaluation(evaluation_id: str, db: Session = Depends(get_db)):
    """Validate mandatory criterion scores & justifications, then submit evaluation."""
    service = EvaluationService(db)
    return service.submit_evaluation(evaluation_id)


@router.get("/{evaluation_id}/evidence", summary="Get evaluation evidence matrix")
def get_evaluation_evidence(evaluation_id: str, db: Session = Depends(get_db)):
    """Retrieve criterion evidence matrix for an evaluation."""
    service = EvaluationService(db)
    eval_item = service.get_evaluation_by_id(evaluation_id)
    return {
        "evaluation_id": eval_item.id,
        "proposal_id": eval_item.proposal_id,
        "evidences": eval_item.evidences,
    }


@router.post(
    "/{evaluation_id}/evidence",
    response_model=EvaluationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add reviewer evidence item",
)
def add_reviewer_evidence(
    evaluation_id: str,
    payload: EvaluationEvidenceCreate,
    db: Session = Depends(get_db),
):
    """Add a manual reviewer evidence item or note to the evaluation."""
    service = EvaluationService(db)
    return service.add_evaluation_evidence(evaluation_id, payload)


@router.post("/{evaluation_id}/summary", summary="Generate draft summary text")
def generate_evaluation_draft_summary(evaluation_id: str, db: Session = Depends(get_db)):
    """Generate draft evaluation summary text from reviewer scores, comments, and evidence for reviewer editing."""
    service = EvaluationService(db)
    return service.generate_draft_summary(evaluation_id)


@router.post("/{evaluation_id}/ai-analysis", summary="Generate or fetch cached AI analysis snapshot")
def get_or_generate_ai_analysis(evaluation_id: str, db: Session = Depends(get_db)):
    """Retrieve cached AI evidence analysis snapshot, or generate a new snapshot if evidence changed."""
    from app.services.ai_evidence_service import AIEvidenceService
    service = AIEvidenceService(db)
    return service.get_or_generate_analysis(evaluation_id)


@router.get("/{evaluation_id}/ai-analysis", summary="Get latest AI analysis snapshot")
def get_latest_ai_analysis(evaluation_id: str, db: Session = Depends(get_db)):
    """Get the latest AI evidence analysis snapshot for an evaluation."""
    from app.services.ai_evidence_service import AIEvidenceService
    service = AIEvidenceService(db)
    return service.get_or_generate_analysis(evaluation_id)


@router.post("/{evaluation_id}/ai-analysis/refresh", summary="Refresh AI evidence analysis")
def refresh_ai_analysis(evaluation_id: str, db: Session = Depends(get_db)):
    """Force explicit regeneration of the AI evidence analysis snapshot."""
    from app.services.ai_evidence_service import AIEvidenceService
    service = AIEvidenceService(db)
    return service.refresh_analysis(evaluation_id)


# Phase P0.9 Endpoints — Reviewer Intelligence & Decision Pack Dossier

@router.get("/{evaluation_id}/review-context", summary="Get aggregated reviewer intelligence context")
def get_review_context(evaluation_id: str, db: Session = Depends(get_db)):
    """Retrieve unified reviewer context aggregating proposal, P0.5 scrutiny, P0.4 benchmarks, P0.6 rubric, P0.8 RAG AI analysis, attention items, coverage matrix, and audit timeline."""
    from app.services.reviewer_intelligence import ReviewerIntelligenceService
    service = ReviewerIntelligenceService(db)
    return service.get_review_context(evaluation_id)


@router.post("/{evaluation_id}/decision-pack", summary="Generate versioned evaluation decision pack snapshot")
def create_decision_pack(evaluation_id: str, db: Session = Depends(get_db)):
    """Generate or retrieve versioned evaluation decision pack snapshot (v1, v2...) with safety boundary validation."""
    from app.services.reviewer_intelligence import ReviewerIntelligenceService
    service = ReviewerIntelligenceService(db)
    return service.create_or_get_decision_pack(evaluation_id)


@router.get("/{evaluation_id}/decision-pack", summary="Get latest evaluation decision pack snapshot")
def get_decision_pack(evaluation_id: str, db: Session = Depends(get_db)):
    """Get the latest evaluation decision pack snapshot."""
    from app.services.reviewer_intelligence import ReviewerIntelligenceService
    service = ReviewerIntelligenceService(db)
    return service.create_or_get_decision_pack(evaluation_id)


@router.get("/{evaluation_id}/decision-pack.pdf", summary="Export printable PDF/HTML evaluation dossier")
def export_decision_pack_pdf(evaluation_id: str, db: Session = Depends(get_db)):
    """Generate printable HTML/PDF technical dossier for offline reviewer archiving and audit."""
    from fastapi.responses import HTMLResponse

    from app.services.reviewer_intelligence import ReviewerIntelligenceService
    service = ReviewerIntelligenceService(db)
    html_content = service.generate_decision_pack_pdf_html(evaluation_id)
    return HTMLResponse(
        content=html_content,
        headers={"Content-Disposition": f"inline; filename=decision_pack_{evaluation_id[:8]}.html"},
    )
