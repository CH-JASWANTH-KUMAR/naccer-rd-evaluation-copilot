from datetime import datetime

from pydantic import Field

from app.schemas.common import ORMBase


class SimilaritySearchRequest(ORMBase):
    title: str | None = Field(None, description="Proposal title")
    objectives: str | None = Field(None, description="Proposal technical objectives")
    problem_statement: str | None = Field(None, description="Proposal problem statement")
    methodology: str | None = Field(None, description="Proposal research methodology")
    technology: str | None = Field(None, description="Proposed technologies / tools")
    expected_outcomes: str | None = Field(None, description="Expected project deliverables")
    domain: str | None = Field(None, description="Research domain")
    institution: str | None = Field(None, description="Submitting institution / PI")
    top_k: int = Field(10, ge=1, le=50, description="Max results to return")


class EvidenceItemRead(ORMBase):
    field: str = Field(description="Matched field (objectives, technology, title, domain)")
    snippet: str = Field(description="Extracted snippet from stored record text")
    reason: str = Field(description="Explanation of matched concepts")
    strength: str = Field(description="DIRECT_MATCH, RELATED, or WEAKLY_RELATED")


class ProvenanceRead(ORMBase):
    source: str
    source_type: str
    source_url: str | None = None
    source_document_name: str | None = None
    source_page_start: int | None = None
    source_page_end: int | None = None
    source_record_identifier: str | None = None
    verification_status: str
    verification_timestamp: datetime | None = None


class SimilarityResultItem(ORMBase):
    project_id: str
    project_code: str
    project_title: str
    institution: str
    domain: str
    status: str
    approved_cost: float
    approved_cost_raw: str | None = None
    similarity_score: float = Field(description="Relevance score from 0.0 to 1.0")
    similarity_percentage: int = Field(description="Relevance score percentage 0-100%")
    relationship: str = Field(description="POTENTIALLY_RELATED, CONCEPTUAL_OVERLAP, WEAK_RELATIONSHIP")
    matched_fields: list[str] = Field(default_factory=list)
    evidence: list[EvidenceItemRead] = Field(default_factory=list)
    provenance: ProvenanceRead
    summary: str | None = None
    raw_record_text: str | None = None


class SimilaritySearchResponse(ORMBase):
    query_summary: dict
    total_candidates_evaluated: int
    results_count: int
    disclaimer: str = Field(
        default="Similarity results are evidence for reviewer assessment and do not constitute an automated novelty or duplication decision."
    )
    results: list[SimilarityResultItem]
