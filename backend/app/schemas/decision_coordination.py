"""Pydantic Schemas for Decision Coordination & Review Workspace."""

from pydantic import BaseModel, Field


class ReviewerAssignedProposalCard(BaseModel):
    evaluation_id: str
    proposal_id: str
    proposal_reference: str | None = None
    proposal_title: str
    institution: str | None = None
    domain: str | None = None
    task_title: str | None = None
    priority: str | None = "MEDIUM"
    is_demo: bool = False
    evidence_sources_count: int = 6
    review_status: str
    assignment_date: str
    due_date: str | None = None
    rubric_completed_count: int
    rubric_total_count: int
    scientific_comparison_available: bool
    evidence_gaps_count: int
    consensus_status: str
    action_required: str


class ReviewerWorkspaceQueue(BaseModel):
    reviewer_id: str
    pending_reviews: list[ReviewerAssignedProposalCard] = Field(default_factory=list)
    completed_reviews: list[ReviewerAssignedProposalCard] = Field(default_factory=list)
    coi_reviews: list[ReviewerAssignedProposalCard] = Field(default_factory=list)


class ChairReviewerProgressItem(BaseModel):
    reviewer_id: str
    reviewer_name: str
    status: str
    submitted_at: str | None = None


class ChairProposalCoordinationItem(BaseModel):
    proposal_id: str
    evaluation_id: str | None = None
    proposal_reference: str
    proposal_title: str
    institution: str
    domain: str
    reviewers: list[ChairReviewerProgressItem] = Field(default_factory=list)
    rubric_progress: str
    scientific_comparison_status: str
    financial_status: str
    consensus_status: str
    max_score_variance: float = 0.0
    decision_readiness: str
    blocking_reasons: list[str] = Field(default_factory=list)
    primary_action: str


class ChairDashboardResponse(BaseModel):
    total_proposals: int
    ready_count: int
    not_ready_count: int
    needs_attention_count: int
    items: list[ChairProposalCoordinationItem] = Field(default_factory=list)


class DecisionReadinessCheck(BaseModel):
    proposal_id: str
    status: str  # READY_FOR_HUMAN_DECISION or NOT_READY
    is_ready: bool
    blocking_reasons: list[str] = Field(default_factory=list)
    prerequisites: dict[str, bool] = Field(default_factory=dict)


class DecisionBriefScientificEvidenceItem(BaseModel):
    evidence_id: str
    source_type: str
    title: str
    snippet: str
    source_provenance: str


class DecisionBriefRubricCriterionItem(BaseModel):
    criterion_key: str
    criterion_name: str
    max_score: float
    average_score: float | None = None
    reviewer_scores: dict[str, float] = Field(default_factory=dict)
    evidence_grounding_status: str
    justification_notes: list[str] = Field(default_factory=list)


class DecisionBriefDisagreementItem(BaseModel):
    criterion_name: str
    scores_by_reviewer: dict[str, float] = Field(default_factory=dict)
    difference: float
    disagreement_status: str
    permitted_comments: list[str] = Field(default_factory=list)


class DecisionBriefResponse(BaseModel):
    proposal_id: str
    title: str
    institution: str
    principal_investigator: str
    domain: str
    duration_months: int | None = None
    declared_total_budget: float | None = None

    # Review Readiness
    reviewer_completion: str
    rubric_completion: str
    scientific_comparison_status: str
    financial_verification_status: str
    completeness_status: str
    decision_readiness: str
    blocking_reasons: list[str] = Field(default_factory=list)

    # Scientific Evidence
    relevant_historical_projects: list[DecisionBriefScientificEvidenceItem] = Field(default_factory=list)
    relevant_research_papers: list[DecisionBriefScientificEvidenceItem] = Field(default_factory=list)
    evidence_gaps: list[str] = Field(default_factory=list)
    reviewer_questions: list[str] = Field(default_factory=list)

    # Rubric Review
    rubric_criteria: list[DecisionBriefRubricCriterionItem] = Field(default_factory=list)

    # Reviewer Consensus
    consensus_status: str
    disagreement_flags: list[DecisionBriefDisagreementItem] = Field(default_factory=list)
    consensus_disclaimer: str = "The system does NOT decide which reviewer is correct. Human decision-makers resolve differences."

    # Outstanding Actions
    outstanding_actions: list[str] = Field(default_factory=list)

    # Metadata
    generated_at: str
