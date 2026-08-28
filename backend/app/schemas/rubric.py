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


class EvaluationRubricRead(ORMBase):
    id: str
    name: str
    version: str
    description: str | None = None
    is_active: bool
    created_at: datetime
    criteria: list[RubricCriterionRead] = []
