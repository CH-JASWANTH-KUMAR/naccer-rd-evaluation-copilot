from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.scientific_evidence import ScientificEvidence
from app.schemas.scientific_evidence import ScientificEvidenceCreate


class ScientificEvidenceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_paper_id(self, paper_id: str, category: str | None = None) -> list[ScientificEvidence]:
        stmt = (
            select(ScientificEvidence)
            .where(ScientificEvidence.research_paper_id == paper_id)
            .order_by(ScientificEvidence.source_page_start.asc(), ScientificEvidence.evidence_id.asc())
        )
        if category:
            stmt = stmt.where(ScientificEvidence.category == category)
        return list(self.db.scalars(stmt).all())

    def get_by_evidence_id(self, evidence_id: str) -> ScientificEvidence | None:
        stmt = select(ScientificEvidence).where(ScientificEvidence.evidence_id == evidence_id)
        return self.db.scalar(stmt)

    def delete_by_paper_id(self, paper_id: str) -> int:
        stmt = select(ScientificEvidence).where(ScientificEvidence.research_paper_id == paper_id)
        records = list(self.db.scalars(stmt).all())
        for r in records:
            self.db.delete(r)
        self.db.commit()
        return len(records)

    def create(self, data: ScientificEvidenceCreate) -> ScientificEvidence:
        ev = ScientificEvidence(
            research_paper_id=data.research_paper_id,
            paper_page_id=data.paper_page_id,
            evidence_id=data.evidence_id,
            parent_evidence_id=data.parent_evidence_id,
            evidence_type=data.evidence_type,
            category=data.category,
            field_name=data.field_name,
            value_text=data.value_text,
            normalized_value=data.normalized_value,
            unit=data.unit,
            comparison_target=data.comparison_target,
            confidence=data.confidence,
            source_page_start=data.source_page_start,
            source_page_end=data.source_page_end,
            source_section=data.source_section,
            source_quote_or_snippet=data.source_quote_or_snippet,
            extraction_method=data.extraction_method,
        )
        self.db.add(ev)
        self.db.commit()
        self.db.refresh(ev)
        return ev
