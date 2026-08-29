from datetime import datetime

from pydantic import Field

from app.schemas.common import ORMBase


class DocumentPageRead(ORMBase):
    id: str
    document_id: str
    page_number: int
    text: str
    created_at: datetime


class ProposalSectionRead(ORMBase):
    id: str
    proposal_id: str
    document_id: str
    section_type: str
    section_title: str
    content: str
    start_page: int
    end_page: int
    confidence: float
    created_at: datetime
    updated_at: datetime


class StructuredSectionRead(ORMBase):
    key: str
    display_title: str
    content: str
    summary: str
    status: str = "REPORTED"
    source_page_start: int = 1
    source_page_end: int = 1
    extraction_confidence: str = "HIGH"
    evidence_id: str = "EVID-000"


class DocumentRead(ORMBase):
    id: str
    proposal_id: str
    filename: str
    file_type: str
    file_size: int
    storage_path: str
    processing_status: str
    processing_error: str | None = None
    document_type: str = "R&D_PROPOSAL"
    document_type_confidence: str | None = None
    document_type_reasons: list[str] | None = None
    structured_sections: list[StructuredSectionRead] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class DocumentDetailRead(DocumentRead):
    pages_count: int = Field(default=0)
    sections_count: int = Field(default=0)
