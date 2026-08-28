from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.institution import Institution
from app.schemas.institution import InstitutionCreate, InstitutionUpdate


class InstitutionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Institution]:
        stmt = select(Institution).order_by(Institution.name.asc())
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, institution_id: str) -> Institution | None:
        return self.db.get(Institution, institution_id)

    def get_by_code(self, code: str) -> Institution | None:
        stmt = select(Institution).where(Institution.code == code)
        return self.db.scalars(stmt).first()

    def create(self, data: InstitutionCreate) -> Institution:
        institution = Institution(
            name=data.name,
            code=data.code,
            type=data.type,
            location=data.location,
        )
        self.db.add(institution)
        self.db.commit()
        self.db.refresh(institution)
        return institution

    def update(self, institution: Institution, data: InstitutionUpdate) -> Institution:
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(institution, key, value)
        self.db.commit()
        self.db.refresh(institution)
        return institution
