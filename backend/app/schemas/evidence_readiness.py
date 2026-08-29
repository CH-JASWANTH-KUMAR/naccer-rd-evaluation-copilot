"""Pydantic Schemas for Evidence Readiness Score & Reviewer Summary."""

from pydantic import BaseModel, Field


class EvidenceReadinessComponentDetail(BaseModel):
    name: str
    score: float
    max_score: float
    status: str
    explanation: str
    contributing_checks: list[str] = Field(default_factory=list)


class EvidenceReadinessItem(BaseModel):
    evidence_id: str
    title: str
    description: str
    source_type: str


class EvidenceReadinessScoreResponse(BaseModel):
    proposal_id: str
    total_score: int
    max_score: int = 100
    interpretation_label: str
    is_demo: bool = False
    disclaimer: str = (
        "Evidence Readiness Score — a transparent summary of available evaluation evidence. "
        "It is not an approval or funding prediction."
    )

    # 6 Deterministic Score Components (100 pts total)
    proposal_completeness_score: float  # max 20
    scientific_evidence_coverage_score: float  # max 20
    moc_guideline_coverage_score: float  # max 20
    financial_verification_score: float  # max 15
    historical_research_support_score: float  # max 15
    reviewer_completion_score: float  # max 10

    # Detailed component breakdowns
    components: list[EvidenceReadinessComponentDetail] = Field(default_factory=list)

    # Reviewer Summary
    strengths: list[EvidenceReadinessItem] = Field(default_factory=list)
    attention_required: list[EvidenceReadinessItem] = Field(default_factory=list)
