from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.institutions import InstitutionRepository
from app.schemas.institution import InstitutionCreate, InstitutionRead


class InstitutionService:
    def __init__(self, db: Session):
        self.repo = InstitutionRepository(db)

    def get_all(self) -> list[InstitutionRead]:
        institutions = self.repo.get_all()
        return [InstitutionRead.model_validate(inst) for inst in institutions]

    def get_by_id(self, institution_id: str) -> InstitutionRead:
        institution = self.repo.get_by_id(institution_id)
        if not institution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Institution with id {institution_id} not found"
            )
        return InstitutionRead.model_validate(institution)

    def create(self, data: InstitutionCreate) -> InstitutionRead:
        existing = self.repo.get_by_code(data.code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Institution with code '{data.code}' already exists"
            )
        institution = self.repo.create(data)
        return InstitutionRead.model_validate(institution)
