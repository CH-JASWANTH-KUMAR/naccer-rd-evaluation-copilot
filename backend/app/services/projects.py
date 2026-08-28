from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.projects import HistoricalProjectRepository
from app.schemas.project import HistoricalProjectCreate, HistoricalProjectRead


class HistoricalProjectService:
    def __init__(self, db: Session):
        self.repo = HistoricalProjectRepository(db)

    def get_all(
        self,
        domain: str | None = None,
        status_filter: str | None = None,
        institution: str | None = None,
        source_type: str | None = None,
        verification_status: str | None = None,
        search: str | None = None,
    ) -> list[HistoricalProjectRead]:
        projects = self.repo.get_all(
            domain=domain,
            status=status_filter,
            institution=institution,
            source_type=source_type,
            verification_status=verification_status,
            search=search,
        )
        return [HistoricalProjectRead.model_validate(p) for p in projects]

    def get_by_id(self, project_id: str) -> HistoricalProjectRead:
        project = self.repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Historical Project with ID '{project_id}' not found.",
            )
        return HistoricalProjectRead.model_validate(project)

    def create(self, data: HistoricalProjectCreate) -> HistoricalProjectRead:
        existing = self.repo.get_by_code(data.project_code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Historical Project with code '{data.project_code}' already exists.",
            )
        project = self.repo.create(data)
        return HistoricalProjectRead.model_validate(project)

    def update_verification_status(self, project_id: str, new_status: str) -> HistoricalProjectRead:
        if new_status not in ["VERIFIED", "REJECTED", "NEEDS_REVIEW"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification status. Must be VERIFIED, REJECTED, or NEEDS_REVIEW.",
            )
        project = self.repo.update_verification_status(project_id, new_status)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Historical Project with ID '{project_id}' not found.",
            )
        return HistoricalProjectRead.model_validate(project)
