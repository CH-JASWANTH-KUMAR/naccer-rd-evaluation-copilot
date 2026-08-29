from datetime import datetime

from pydantic import Field

from app.schemas.common import ORMBase


class PaperPageRead(ORMBase):
    id: str
    research_paper_id: str
    page_number: int
    extracted_text: str
    character_count: int
    detected_sections: str | None = None
    extraction_status: str
    created_at: datetime


class ResearchPaperCreate(ORMBase):
    title: str
    authors: str | None = None
    abstract: str | None = None
    publication_year: int | None = None
    journal_or_conference: str | None = None
    doi: str | None = None
    research_domain: str = "Coal Mining & Automation"
    keywords: str | None = None
    source_filename: str
    source_document_type: str = "PDF"
    page_count: int = 0
    file_hash: str
    storage_path: str | None = None
    extraction_status: str = "COMPLETED"
    raw_text: str | None = None


class ResearchPaperRead(ORMBase):
    id: str
    title: str
    authors: str | None = None
    abstract: str | None = None
    publication_year: int | None = None
    journal_or_conference: str | None = None
    doi: str | None = None
    research_domain: str
    keywords: str | None = None
    source_filename: str
    source_document_type: str
    page_count: int
    file_hash: str
    storage_path: str | None = None
    extraction_status: str
    created_at: datetime
    updated_at: datetime
    pages: list[PaperPageRead] = Field(default_factory=list)


class ResearchPaperSearchRequest(ORMBase):
    query: str | None = Field(None, description="Search query string")
    research_domain: str | None = Field(None, description="Filter by domain")
    top_k: int = Field(10, ge=1, le=50, description="Max results to return")


class ResearchPaperSearchResultItem(ORMBase):
    paper_id: str
    evidence_id: str = Field(description="Deterministic Evidence ID (e.g. PAPER-001-P04)")
    paper_index: int = Field(description="Sequential paper index number (e.g. 1)")
    title: str
    authors: str | None = None
    publication_year: int | None = None
    research_domain: str
    page_number: int
    matched_sections: list[str] = Field(default_factory=list)
    matched_dimensions: list[str] = Field(default_factory=list)
    relevance_score: float = Field(description="Relevance score from 0.0 to 1.0")
    snippet: str
    source_filename: str


class ResearchPaperSearchResponse(ORMBase):
    query_summary: dict
    total_papers_evaluated: int
    results_count: int
    disclaimer: str = Field(
        default="Research paper search results provide scientific evidence items for human reviewer evaluation and do not constitute an automated novelty, duplication, or funding decision."
    )
    results: list[ResearchPaperSearchResultItem]
