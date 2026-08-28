from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.projects import HistoricalProjectRepository
from app.schemas.project import (
    HistoricalProjectCreate,
    HistoricalProjectRead,
    ImportBatchRead,
    ImportReportRead,
    VerificationUpdate,
)
from app.services.historical_import_service import HistoricalProjectImportService
from app.services.projects import HistoricalProjectService

router = APIRouter()


@router.post(
    "/historical-projects/import",
    response_model=ImportReportRead,
    status_code=status.HTTP_201_CREATED,
    summary="[Development/Admin] Import historical project catalogue PDF",
)
def import_historical_projects_catalog(
    file: UploadFile = File(...),
    source_name: str = Query("CIL/CMPDI R&D Catalogue", description="Source catalogue name"),
    db: Session = Depends(get_db),
):
    """Import official CIL/CMPDI historical projects PDF catalog with provenance preservation."""
    import_service = HistoricalProjectImportService(db)
    return import_service.import_pdf_catalog(file, source_name=source_name, source_type="OFFICIAL")


@router.get(
    "/historical-projects/imports",
    response_model=list[ImportBatchRead],
    summary="List all historical project import batches",
)
def list_import_batches(db: Session = Depends(get_db)):
    """Retrieve import batch summary records."""
    repo = HistoricalProjectRepository(db)
    batches = repo.get_all_import_batches()
    return [ImportBatchRead.model_validate(b) for b in batches]


@router.get(
    "/historical-projects/imports/{import_id}",
    response_model=ImportBatchRead,
    summary="Get import batch details by ID",
)
def get_import_batch_details(import_id: str, db: Session = Depends(get_db)):
    """Retrieve details for a specific import batch."""
    repo = HistoricalProjectRepository(db)
    batch = repo.get_import_batch_by_id(import_id)
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Import batch with ID '{import_id}' not found.",
        )
    return ImportBatchRead.model_validate(batch)


@router.get("/projects", response_model=list[HistoricalProjectRead], summary="List historical projects")
def list_projects(
    domain: str | None = Query(None, description="Filter by research domain"),
    status: str | None = Query(None, description="Filter by project status (ONGOING, COMPLETED, TERMINATED)"),
    institution: str | None = Query(None, description="Filter by implementing agency/institution"),
    source_type: str | None = Query(None, description="Filter by source type (OFFICIAL, SYNTHETIC)"),
    verification_status: str | None = Query(
        None, description="Filter by verification status (NEEDS_REVIEW, VERIFIED, REJECTED)"
    ),
    search: str | None = Query(None, description="Keyword search in title, code, institution, or domain"),
    db: Session = Depends(get_db),
):
    """Retrieve historical projects list with search and multi-parameter filtering."""
    service = HistoricalProjectService(db)
    return service.get_all(
        domain=domain,
        status_filter=status,
        institution=institution,
        source_type=source_type,
        verification_status=verification_status,
        search=search,
    )


@router.post(
    "/projects",
    response_model=HistoricalProjectRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create historical project",
)
def create_project(data: HistoricalProjectCreate, db: Session = Depends(get_db)):
    """Register a new historical benchmark project."""
    service = HistoricalProjectService(db)
    return service.create(data)


@router.get("/projects/{project_id}", response_model=HistoricalProjectRead, summary="Get project by ID")
def get_project(project_id: str, db: Session = Depends(get_db)):
    """Retrieve historical project by ID."""
    service = HistoricalProjectService(db)
    return service.get_by_id(project_id)


@router.get("/projects/{project_id}/source", summary="Get source provenance and raw record text")
def get_project_source_provenance(project_id: str, db: Session = Depends(get_db)):
    """Retrieve source provenance metadata and raw extracted text for auditing."""
    service = HistoricalProjectService(db)
    proj = service.get_by_id(project_id)
    return {
        "project_id": proj.id,
        "project_code": proj.project_code,
        "source": proj.source,
        "source_type": proj.source_type,
        "source_url": proj.source_url,
        "source_document_name": proj.source_document_name,
        "source_page_start": proj.source_page_start,
        "source_page_end": proj.source_page_end,
        "raw_record_text": proj.raw_record_text,
        "verification_status": proj.verification_status,
        "verification_timestamp": proj.verification_timestamp,
    }


@router.patch(
    "/projects/{project_id}/verification", response_model=HistoricalProjectRead, summary="Update verification status"
)
def update_project_verification(project_id: str, payload: VerificationUpdate, db: Session = Depends(get_db)):
    """Reviewer manual verification endpoint (sets status to VERIFIED or REJECTED)."""
    service = HistoricalProjectService(db)
    return service.update_verification_status(project_id, payload.verification_status)
