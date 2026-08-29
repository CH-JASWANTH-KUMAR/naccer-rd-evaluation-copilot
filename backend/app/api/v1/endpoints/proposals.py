from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.institutions import InstitutionRepository
from app.repositories.proposals import ProposalRepository
from app.schemas.proposal import (
    FinancialComplianceReportRead,
    ProposalCompletenessReportRead,
    ProposalCreate,
    ProposalRead,
    ProposalUpdate,
)
from app.schemas.search import SimilaritySearchRequest, SimilaritySearchResponse
from app.services.financial_compliance import FinancialComplianceService
from app.services.historical_search_service import HistoricalProjectSearchService
from app.services.proposal_completeness import ProposalCompletenessService
from app.services.proposal_ingestion import ProposalIngestionService
from app.services.proposals import ProposalService

router = APIRouter()


@router.post(
    "/upload",
    response_model=ProposalRead,
    status_code=status.HTTP_201_CREATED,
    summary="Upload & Intake R&D Proposal PDF",
)
def upload_proposal_pdf(
    file: UploadFile = File(...),
    title: str | None = Form(None, description="Full Project Title"),
    institution_id: str | None = Form(None, description="Submitting institution ID"),
    principal_investigator: str = Form("Dr. R. K. Verma", description="Principal Investigator"),
    domain: str = Form("Mine Safety & Ventilation", description="Research Domain"),
    budget_total: float | None = Form(None, description="Proposed Budget Total"),
    db: Session = Depends(get_db),
):
    """Upload proposal PDF, validate document, extract sections, and run preliminary completeness & compliance engines."""
    ingestion_service = ProposalIngestionService(db)
    return ingestion_service.ingest_proposal_pdf(
        file=file,
        title=title,
        institution_id=institution_id,
        principal_investigator=principal_investigator,
        domain=domain,
        budget_total=budget_total,
    )


@router.post(
    "",
    response_model=ProposalRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create structured proposal record",
)
def create_proposal(
    data: ProposalCreate,
    db: Session = Depends(get_db),
):
    """Create a structured proposal record."""
    if data.budget_total is not None and data.budget_total < 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Budget total cannot be negative.",
        )

    inst_repo = InstitutionRepository(db)
    inst = inst_repo.get_by_id(data.institution_id)
    if not inst:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Institution with ID '{data.institution_id}' not found.",
        )

    service = ProposalService(db)
    return service.create_proposal(data)


@router.get("", response_model=list[ProposalRead], summary="List proposals")
def list_proposals(
    domain: str | None = Query(None, description="Filter by research domain"),
    status: str | None = Query(None, description="Filter by proposal status"),
    completeness_status: str | None = Query(None, description="Filter by completeness status"),
    compliance_status: str | None = Query(None, description="Filter by compliance status"),
    search: str | None = Query(None, description="Keyword search in title, reference, or PI"),
    db: Session = Depends(get_db),
):
    """Retrieve proposals list with query filters."""
    service = ProposalService(db)
    return service.get_all_proposals(
        domain=domain,
        status_filter=status,
        completeness_status=completeness_status,
        compliance_status=compliance_status,
        search=search,
    )


@router.get("/{proposal_id}", response_model=ProposalRead, summary="Get proposal by ID")
def get_proposal(proposal_id: str, db: Session = Depends(get_db)):
    """Retrieve structured proposal details by ID."""
    service = ProposalService(db)
    return service.get_proposal_by_id(proposal_id)


@router.patch("/{proposal_id}", response_model=ProposalRead, summary="Update proposal details")
def update_proposal(proposal_id: str, payload: ProposalUpdate, db: Session = Depends(get_db)):
    """Reviewer manual edit endpoint to update extracted proposal fields with audit logging."""
    service = ProposalService(db)
    return service.update_proposal(proposal_id, payload)


@router.delete("/{proposal_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete proposal")
def delete_proposal(proposal_id: str, db: Session = Depends(get_db)):
    """Delete proposal record."""
    repo = ProposalRepository(db)
    proposal = repo.get_by_id(proposal_id)
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proposal with ID '{proposal_id}' not found.",
        )
    repo.delete(proposal)
    return None


@router.get("/{proposal_id}/source", summary="Get proposal document page provenance")
def get_proposal_source_provenance(proposal_id: str, db: Session = Depends(get_db)):
    """Retrieve proposal document page provenance and extracted page text."""
    repo = ProposalRepository(db)
    proposal = repo.get_by_id(proposal_id)
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proposal with ID '{proposal_id}' not found.",
        )

    doc_info = []
    for doc in proposal.documents:
        pages = [
            {
                "page_number": p.page_number,
                "character_count": len(p.text),
                "extracted_text": p.text,
            }
            for p in doc.pages
        ]
        doc_info.append(
            {
                "document_id": doc.id,
                "filename": doc.filename,
                "file_size": doc.file_size,
                "document_hash": doc.document_hash,
                "page_count": doc.page_count,
                "storage_path": doc.storage_path,
                "pages": pages,
            }
        )

    return {
        "proposal_id": proposal.id,
        "proposal_reference": proposal.proposal_reference,
        "title": proposal.title,
        "documents": doc_info,
    }


@router.get(
    "/{proposal_id}/completeness",
    response_model=ProposalCompletenessReportRead,
    summary="Get proposal completeness report",
)
def get_proposal_completeness_report(proposal_id: str, db: Session = Depends(get_db)):
    """Retrieve completeness checklist findings report for proposal."""
    repo = ProposalRepository(db)
    proposal = repo.get_by_id(proposal_id)
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proposal with ID '{proposal_id}' not found.",
        )
    return ProposalCompletenessService.evaluate_completeness(proposal)


@router.get(
    "/{proposal_id}/compliance",
    response_model=FinancialComplianceReportRead,
    summary="Get financial compliance findings report",
)
def get_proposal_financial_compliance_report(proposal_id: str, db: Session = Depends(get_db)):
    """Retrieve rule-based financial arithmetic & compliance report for proposal."""
    repo = ProposalRepository(db)
    proposal = repo.get_by_id(proposal_id)
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proposal with ID '{proposal_id}' not found.",
        )
    return FinancialComplianceService.evaluate_financial_compliance(proposal)


@router.post("/{proposal_id}/reprocess", response_model=ProposalRead, summary="Reprocess proposal scrutiny")
def reprocess_proposal_scrutiny(proposal_id: str, db: Session = Depends(get_db)):
    """Re-run extraction, completeness, and financial compliance engines for a proposal."""
    ingestion_service = ProposalIngestionService(db)
    return ingestion_service.reprocess_proposal(proposal_id)


@router.post(
    "/{proposal_id}/similar-projects",
    response_model=SimilaritySearchResponse,
    summary="Connect proposal to P0.4 historical similarity engine",
)
def find_similar_historical_projects_for_proposal(
    proposal_id: str,
    top_k: int = Query(5, ge=1, le=50, description="Max historical benchmarks to return"),
    db: Session = Depends(get_db),
):
    """Integrates proposal parameters with P0.4 historical project search engine to surface evidence-backed benchmark projects."""
    repo = ProposalRepository(db)
    proposal = repo.get_by_id(proposal_id)
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proposal with ID '{proposal_id}' not found.",
        )

    # Convert proposal into P0.4 SimilaritySearchRequest representation
    search_request = SimilaritySearchRequest(
        title=proposal.title,
        objectives=proposal.objectives,
        problem_statement=proposal.problem_statement,
        methodology=proposal.methodology,
        technology=proposal.technology,
        expected_outcomes=proposal.expected_outcomes,
        domain=proposal.domain,
        institution=proposal.institution.name if proposal.institution else None,
        top_k=top_k,
    )

    search_service = HistoricalProjectSearchService(db)
    return search_service.search_similar_projects(search_request)
