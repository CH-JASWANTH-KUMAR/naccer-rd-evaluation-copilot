from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.institution import InstitutionCreate, InstitutionRead
from app.services.institutions import InstitutionService

router = APIRouter()


@router.get("", response_model=list[InstitutionRead], summary="List all institutions")
def list_institutions(db: Session = Depends(get_db)):
    """Retrieve all registered academic and research institutions."""
    service = InstitutionService(db)
    return service.get_all()


@router.post("", response_model=InstitutionRead, status_code=status.HTTP_201_CREATED, summary="Create institution")
def create_institution(data: InstitutionCreate, db: Session = Depends(get_db)):
    """Register a new institution."""
    service = InstitutionService(db)
    return service.create(data)


@router.get("/{institution_id}", response_model=InstitutionRead, summary="Get institution by ID")
def get_institution(institution_id: str, db: Session = Depends(get_db)):
    """Retrieve institution details by ID."""
    service = InstitutionService(db)
    return service.get_by_id(institution_id)
