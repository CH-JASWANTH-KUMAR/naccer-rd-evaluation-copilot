from pydantic import Field

from app.schemas.common import ORMBase


class ScientificComparisonRecord(ORMBase):
    comparison_id: str
    dimension: str = Field(
        description="RESEARCH_OBJECTIVE, METHODOLOGY, ALGORITHM, DATASET, FEATURES, EVALUATION_METRICS, BASELINES, EXPERIMENTAL_VALIDATION, REPORTED_RESULTS, LIMITATIONS"
    )
    proposal_field: str
    proposal_value: str
    evidence_source_type: str = Field(description="HISTORICAL_PROJECT, RESEARCH_PAPER")
    evidence_source_id: str
    evidence_value: str
    comparison_status: str = Field(
        description="MATCHING, PARTIALLY_MATCHING, DIFFERENT, NOT_REPORTED, NOT_COMPARABLE, UNRESOLVED, CONFLICTING_EVIDENCE"
    )
    explanation: str
    source_page_start: int | None = None
    source_page_end: int | None = None
    evidence_id: str = Field(description="e.g. HIST-001, PAPER-001-P03, PAPER-001-P03-METRIC-01")
    confidence: str = Field(default="HIGH", description="EXTRACTION CONFIDENCE (HIGH, MEDIUM, LOW)")


class EvidenceGapRecord(ORMBase):
    dimension: str
    gap: str
    reviewer_action: str
    evidence_supporting_gap: str


class ReviewerQuestionRecord(ORMBase):
    question_id: str
    dimension: str
    question: str
    evidence_id: str
    rationale: str


class EvidenceSourceSummary(ORMBase):
    source_type: str
    evidence_id: str
    title: str
    relevance_score: float
    matched_dimensions: list[str] = Field(default_factory=list)


class ProposalScientificComparisonResponse(ORMBase):
    proposal_id: str
    comparison_summary: dict[str, int] = Field(
        default_factory=dict,
        description="Summary counts: matching, partially_matching, different, not_reported, not_comparable",
    )
    comparisons: list[ScientificComparisonRecord] = Field(default_factory=list)
    evidence_gaps: list[EvidenceGapRecord] = Field(default_factory=list)
    reviewer_questions: list[ReviewerQuestionRecord] = Field(default_factory=list)
    evidence_sources: list[EvidenceSourceSummary] = Field(default_factory=list)
