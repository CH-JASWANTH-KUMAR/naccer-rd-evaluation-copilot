from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.research_papers import ResearchPaperRepository
from app.schemas.research_paper import (
    PaperPageRead,
    ResearchPaperRead,
    ResearchPaperSearchRequest,
    ResearchPaperSearchResponse,
)
from app.schemas.scientific_evidence import (
    ComparisonSummaryRead,
    ScientificDatasetRead,
    ScientificEvidenceRead,
    ScientificExperimentRead,
    ScientificMetricRead,
)
from app.services.research_paper_ingestion import ResearchPaperIngestionService
from app.services.research_paper_search_service import ResearchPaperSearchService
from app.services.scientific_evidence_service import ScientificEvidenceService

router = APIRouter()


@router.post(
    "/upload",
    response_model=ResearchPaperRead,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and ingest a research paper PDF",
)
def upload_research_paper(
    file: UploadFile = File(...),
    research_domain: str = Query("Coal Mining & Automation", description="Research domain"),
    db: Session = Depends(get_db),
):
    """Upload scientific research paper PDF, extract page-level text, and index metadata & sections."""
    ingestion_service = ResearchPaperIngestionService(db)
    return ingestion_service.ingest_paper_pdf(file, research_domain=research_domain)


@router.get(
    "",
    response_model=list[ResearchPaperRead],
    summary="List ingested scientific research papers",
)
def list_research_papers(
    domain: str | None = Query(None, description="Filter by research domain"),
    db: Session = Depends(get_db),
):
    """Retrieve list of ingested research papers with metadata."""
    repo = ResearchPaperRepository(db)
    papers = repo.get_all(research_domain=domain)
    return [ResearchPaperRead.model_validate(p) for p in papers]


@router.get(
    "/{paper_id}",
    response_model=ResearchPaperRead,
    summary="Get research paper metadata and page details by ID",
)
def get_research_paper(paper_id: str, db: Session = Depends(get_db)):
    """Retrieve details for a specific research paper."""
    repo = ResearchPaperRepository(db)
    paper = repo.get_by_id(paper_id)
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Research paper with ID '{paper_id}' not found.",
        )
    return ResearchPaperRead.model_validate(paper)


@router.get(
    "/{paper_id}/pages",
    response_model=list[PaperPageRead],
    summary="Get page-level breakdown for a research paper",
)
def get_research_paper_pages(paper_id: str, db: Session = Depends(get_db)):
    """Retrieve all pages with extracted text and section tags for a research paper."""
    repo = ResearchPaperRepository(db)
    paper = repo.get_by_id(paper_id)
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Research paper with ID '{paper_id}' not found.",
        )
    return [PaperPageRead.model_validate(p) for p in paper.pages]


@router.post(
    "/search",
    response_model=ResearchPaperSearchResponse,
    summary="Search research paper knowledge base for evidence",
)
def search_research_papers(
    payload: ResearchPaperSearchRequest,
    db: Session = Depends(get_db),
):
    """Search ingested research papers for page-traceable evidence items."""
    search_service = ResearchPaperSearchService(db)
    return search_service.search_papers(payload)


@router.get(
    "/{paper_id}/scientific-evidence",
    response_model=list[ScientificEvidenceRead],
    summary="Get structured scientific evidence for a research paper",
)
def get_scientific_evidence(
    paper_id: str,
    category: str | None = Query(None, description="Filter by category (METRIC, DATASET, METHODOLOGY, EXPERIMENT)"),
    db: Session = Depends(get_db),
):
    """Retrieve extracted scientific evidence records (metrics, datasets, methodology, baselines)."""
    ev_service = ScientificEvidenceService(db)
    return ev_service.get_paper_evidence(paper_id, category=category)


@router.get(
    "/{paper_id}/metrics",
    response_model=list[ScientificMetricRead],
    summary="Get reported scientific metrics for a research paper",
)
def get_paper_metrics(paper_id: str, db: Session = Depends(get_db)):
    """Retrieve reported metrics with raw values, normalized values, units, targets, and evidence IDs."""
    ev_service = ScientificEvidenceService(db)
    return ev_service.get_paper_metrics(paper_id)


@router.get(
    "/{paper_id}/datasets",
    response_model=list[ScientificDatasetRead],
    summary="Get dataset specifications for a research paper",
)
def get_paper_datasets(paper_id: str, db: Session = Depends(get_db)):
    """Retrieve dataset observation counts, sensor counts, and sample counts."""
    ev_service = ScientificEvidenceService(db)
    return ev_service.get_paper_datasets(paper_id)


@router.get(
    "/{paper_id}/experiments",
    response_model=list[ScientificExperimentRead],
    summary="Get experimental setup, algorithms, and baselines for a research paper",
)
def get_paper_experiments(paper_id: str, db: Session = Depends(get_db)):
    """Retrieve experimental setup, algorithms, baselines, and validation strategies."""
    ev_service = ScientificEvidenceService(db)
    return ev_service.get_paper_experiments(paper_id)


@router.post(
    "/{paper_id}/extract-evidence",
    response_model=list[ScientificEvidenceRead],
    summary="Trigger structured scientific evidence extraction for a paper",
)
def trigger_evidence_extraction(paper_id: str, db: Session = Depends(get_db)):
    """Trigger page-by-page scientific evidence extraction pipeline."""
    ev_service = ScientificEvidenceService(db)
    return ev_service.extract_and_store_paper_evidence(paper_id)


@router.post(
    "/compare-proposal",
    response_model=ComparisonSummaryRead,
    summary="Generate proposal-to-paper evidence comparison foundation record",
)
def compare_proposal_to_paper(
    proposal_id: str = Query(..., description="Target proposal ID"),
    paper_id: str = Query(..., description="Target research paper ID"),
    db: Session = Depends(get_db),
):
    """Generate structured evidence relationship comparison records (MATCHING, DIFFERENT, PARTIALLY_MATCHING, NOT_REPORTED)."""
    ev_service = ScientificEvidenceService(db)
    return ev_service.compare_proposal_to_paper(proposal_id=proposal_id, paper_id=paper_id)


@router.post(
    "/seed",
    response_model=ResearchPaperRead,
    status_code=status.HTTP_201_CREATED,
    summary="Seed synthetic predictive-maintenance research paper PDF fixture",
)
def seed_research_paper_fixture(db: Session = Depends(get_db)):
    """Seed synthetic predictive maintenance coal mining research paper fixture."""
    from pathlib import Path

    fixture_path = Path(__file__).resolve().parents[4] / "tests" / "fixtures" / "synthetic_research_paper_predictive_maintenance.pdf"
    if not fixture_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Synthetic research paper PDF fixture file not found.",
        )

    with open(fixture_path, "rb") as f:
        file_obj = UploadFile(filename="synthetic_research_paper_predictive_maintenance.pdf", file=f)
        ingestion_service = ResearchPaperIngestionService(db)
        paper = ingestion_service.ingest_paper_pdf(file_obj, research_domain="Automation & Robotics in Mining")
        
        # Trigger automatic scientific evidence extraction
        ev_service = ScientificEvidenceService(db)
        ev_service.extract_and_store_paper_evidence(paper.id)
        
        return paper
