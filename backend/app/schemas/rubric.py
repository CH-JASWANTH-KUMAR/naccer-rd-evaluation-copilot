from datetime import datetime

from app.schemas.common import ORMBase


class RubricCriterionRead(ORMBase):
    id: str
    key: str
    name: str
    description: str
    category: str
    max_score: float
    weight: float
    display_order: int
    required: bool
    evidence_required: bool
    source_document: str | None = None
    source_page: int | None = None
    source_section: str | None = None
    original_criterion_wording: str | None = None
    scoring_instructions: str | None = "NOT_SPECIFIED"
    scoring_scale: str | None = "NOT_SPECIFIED"
    evidence_requirements: dict | list | None = None


class EvaluationRubricRead(ORMBase):
    id: str
    name: str
    version: str
    description: str | None = None
    is_active: bool
    created_at: datetime
    criteria: list[RubricCriterionRead] = []
