from datetime import date, datetime

from pydantic import Field

from app.schemas.common import ORMBase


class ImportBatchRead(ORMBase):
    id: str
    source_name: str
    source_type: str
    source_url: str | None = None
    document_name: str
    document_hash: str
    total_records: int
    successful_records: int
    needs_review_records: int
    failed_records: int
    status: str
    imported_at: datetime


class HistoricalSourceDocumentRead(ORMBase):
    id: str
    import_batch_id: str
    filename: str
    source_url: str | None = None
    file_hash: str
    page_count: int
    storage_path: str
    extraction_status: str
    created_at: datetime


class HistoricalProjectCreate(ORMBase):
    project_code: str
    title: str
    institution: str
    domain: str
    objectives: str | None = None
    methodology: str | None = None
    technology: str | None = None
    expected_outcomes: str | None = None
    status: str = "ONGOING"
    start_date: date | None = None
    completion_date: date | None = None
    approved_cost: float = 0.0
    approved_cost_raw: str | None = None
    source: str = "CIL/CMPDI"
    source_type: str = "OFFICIAL"
    source_url: str | None = None
    source_document_name: str | None = None
    source_page_start: int | None = None
    source_page_end: int | None = None
    source_record_identifier: str | None = None
    raw_record_text: str | None = None
    verification_status: str = "NEEDS_REVIEW"
    import_batch_id: str | None = None


class HistoricalProjectRead(ORMBase):
    id: str
    project_code: str
    title: str
    institution: str
    domain: str
    objectives: str | None = None
    methodology: str | None = None
    technology: str | None = None
    expected_outcomes: str | None = None
    status: str
    start_date: date | None = None
    completion_date: date | None = None
    approved_cost: float
    approved_cost_raw: str | None = None
    source: str
    source_type: str
    source_url: str | None = None
    source_document_name: str | None = None
    source_page_start: int | None = None
    source_page_end: int | None = None
    source_record_identifier: str | None = None
    raw_record_text: str | None = None
    verification_status: str
    verification_timestamp: datetime | None = None
    import_batch_id: str | None = None
    created_at: datetime
    updated_at: datetime


class VerificationUpdate(ORMBase):
    verification_status: str = Field(description="Must be VERIFIED or REJECTED")


class ImportReportRead(ORMBase):
    import_batch_id: str
    source_name: str
    document_name: str
    document_hash: str
    total_detected: int
    imported_count: int
    needs_review_count: int
    duplicate_count: int
    failed_count: int
    status: str
    message: str
