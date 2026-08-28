from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMBase
from app.schemas.institution import InstitutionRead


class ProposalCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=500)
    institution_id: str = Field(..., min_length=1)
    principal_investigator: str = Field(..., min_length=2, max_length=255)
    domain: str = Field(..., min_length=2, max_length=255)

    problem_statement: str | None = None
    objectives: str | None = None
    methodology: str | None = None
    literature_review: str | None = None
    expected_outcomes: str | None = None
    timeline: str | None = None

    status: str = Field(default="UNDER_REVIEW")
    priority: str = Field(default="MEDIUM")
    budget_total: float = Field(default=0.0, ge=0.0)


class ProposalUpdate(BaseModel):
    title: str | None = None
    principal_investigator: str | None = None
    domain: str | None = None
    problem_statement: str | None = None
    objectives: str | None = None
    methodology: str | None = None
    expected_outcomes: str | None = None
    status: str | None = None
    priority: str | None = None
    budget_total: float | None = Field(default=None, ge=0.0)


class ProposalRead(ORMBase):
    id: str
    title: str
    institution_id: str
    institution: InstitutionRead | None = None
    principal_investigator: str
    domain: str
    problem_statement: str | None = None
    objectives: str | None = None
    methodology: str | None = None
    expected_outcomes: str | None = None
    status: str
    priority: str
    budget_total: float
    submission_date: datetime
    created_at: datetime
    updated_at: datetime
