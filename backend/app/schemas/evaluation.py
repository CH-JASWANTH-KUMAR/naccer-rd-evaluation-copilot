from datetime import datetime

from pydantic import Field

from app.schemas.common import ORMBase
from app.schemas.proposal import ProposalRead


class EvaluationCriterionRead(ORMBase):
    id: str
    criterion_key: str | None = None
    name: str
    description: str | None = None
    max_score: float
    weight: float
    score: float | None = None
    weighted_score: float | None = None
    comments: str | None = None
    justification_notes: str | None = None
    evidence_status: str = "NOT_REPORTED"
    proposal_evidence_ids: list | dict | None = None
    historical_evidence_ids: list | dict | None = None
    paper_evidence_ids: list | dict | None = None
    scrutiny_evidence_ids: list | dict | None = None
    financial_evidence_ids: list | dict | None = None
    evidence_gaps: list | dict | None = None
    reviewer_questions: list | dict | None = None
    evidence_coverage_score: float | None = None


class EvaluationCriterionUpdate(ORMBase):
    id: str
    score: float | None = None
    comments: str | None = None
    justification_notes: str | None = None


class EvaluationEvidenceRead(ORMBase):
    id: str
    evaluation_id: str
    criterion_id: str | None = None
    evidence_type: str
    source_type: str
    source_reference: str | None = None
    source_page_start: int | None = None
    source_page_end: int | None = None
    evidence_text: str
    reviewer_note: str | None = None
    created_at: datetime


class EvaluationEvidenceCreate(ORMBase):
    criterion_id: str | None = None
    evidence_type: str = "PROPOSAL_SECTION"
    source_type: str = "PROPOSAL"
    source_reference: str | None = None
    source_page_start: int | None = None
    source_page_end: int | None = None
    evidence_text: str
    reviewer_note: str | None = None


class EvaluationAuditEventRead(ORMBase):
    id: str
    evaluation_id: str
    actor_id: str
    action: str
    criterion_id: str | None = None
    previous_value: str | None = None
    new_value: str | None = None
    created_at: datetime


class EvaluationCreate(ORMBase):
    proposal_id: str
    reviewer_id: str = "Rev-01"
    rubric_id: str | None = None


class EvaluationUpdate(ORMBase):
    reviewer_summary: str | None = None
    reviewer_recommendation: str | None = None
    criteria: list[EvaluationCriterionUpdate] | None = None


class EvaluationRead(ORMBase):
    id: str
    proposal_id: str
    reviewer_id: str
    rubric_id: str | None = None
    rubric_version: str
    status: str
    overall_score: float | None = None
    reviewer_summary: str | None = None
    reviewer_recommendation: str
    started_at: datetime
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    proposal: ProposalRead | None = None
    criteria: list[EvaluationCriterionRead] = Field(default_factory=list)
    evidences: list[EvaluationEvidenceRead] = Field(default_factory=list)
