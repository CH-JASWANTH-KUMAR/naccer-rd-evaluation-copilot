from datetime import datetime

from pydantic import Field, field_validator

from app.schemas.common import ORMBase


class EvidenceReference(ORMBase):
    source_type: str = Field(description="PROPOSAL, HISTORICAL_PROJECT, FINANCIAL_CHECK, COMPLETENESS_CHECK, REVIEWER")
    source_reference: str = Field(description="Name or ID of evidence source")
    page_start: int | None = Field(default=None, description="Starting source page number")
    page_end: int | None = Field(default=None, description="Ending source page number")
    evidence_text: str = Field(description="Exact snippet or summary of supporting evidence")


class CriterionAnalysisItem(ORMBase):
    criterion_key: str
    criterion_name: str
    observation: str
    supporting_evidence: list[EvidenceReference] = Field(default_factory=list)
    evidence_gaps: list[str] = Field(default_factory=list)
    reviewer_questions: list[str] = Field(default_factory=list)


class StrengthItem(ORMBase):
    title: str
    description: str
    supporting_evidence: list[EvidenceReference] = Field(default_factory=list)


class ConcernItem(ORMBase):
    title: str
    description: str
    supporting_evidence: list[EvidenceReference] = Field(default_factory=list)


class EvidenceGapItem(ORMBase):
    criterion_key: str
    gap_description: str
    impact: str
    reviewer_action: str


class ReviewerQuestionItem(ORMBase):
    criterion_key: str
    question: str
    rationale: str


class ContradictionItem(ORMBase):
    field_a: str
    field_b: str
    observation: str
    severity: str = "WARNING"


class AIAnalysisResult(ORMBase):
    overall_observation: str
    criterion_analysis: list[CriterionAnalysisItem] = Field(default_factory=list)
    strengths: list[StrengthItem] = Field(default_factory=list)
    concerns: list[ConcernItem] = Field(default_factory=list)
    evidence_gaps: list[EvidenceGapItem] = Field(default_factory=list)
    reviewer_questions: list[ReviewerQuestionItem] = Field(default_factory=list)
    contradictions: list[ContradictionItem] = Field(default_factory=list)
    disclaimer: str = Field(
        default="AI analysis is evidence-grounded decision support. It does not assign reviewer scores or make autonomous novelty, duplication, approval, rejection, or funding decisions."
    )

    @field_validator("overall_observation", mode="after")
    @classmethod
    def validate_safety_boundaries(cls, v: str) -> str:
        disallowed = ["AUTONOMOUS_APPROVAL", "AUTONOMOUS_REJECTION", "NOT_NOVEL_VERDICT"]
        for d in disallowed:
            if d in v.upper():
                raise ValueError(f"AI output contains prohibited autonomous decision field '{d}'.")
        return v


class AIAnalysisRead(ORMBase):
    id: str
    evaluation_id: str
    provider: str
    model: str
    prompt_version: str
    input_hash: str
    status: str
    created_at: datetime
    analysis_result: AIAnalysisResult
