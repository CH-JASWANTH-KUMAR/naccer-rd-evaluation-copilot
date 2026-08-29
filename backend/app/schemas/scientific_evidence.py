from datetime import datetime

from pydantic import Field

from app.schemas.common import ORMBase


class ScientificEvidenceCreate(ORMBase):
    research_paper_id: str
    paper_page_id: str | None = None
    evidence_id: str
    parent_evidence_id: str
    evidence_type: str = "METRIC"
    category: str = "METRIC"
    field_name: str
    value_text: str
    normalized_value: float | None = None
    unit: str | None = None
    comparison_target: str | None = None
    confidence: str = "HIGH"
    source_page_start: int = 1
    source_page_end: int = 1
    source_section: str | None = None
    source_quote_or_snippet: str = ""
    extraction_method: str = "RULE_BASED"


class ScientificEvidenceRead(ORMBase):
    id: str
    research_paper_id: str
    paper_page_id: str | None = None
    evidence_id: str
    parent_evidence_id: str
    evidence_type: str
    category: str
    field_name: str
    value_text: str
    normalized_value: float | None = None
    unit: str | None = None
    comparison_target: str | None = None
    confidence: str
    source_page_start: int
    source_page_end: int
    source_section: str | None = None
    source_quote_or_snippet: str
    extraction_method: str
    created_at: datetime


class ScientificMetricRead(ORMBase):
    metric_name: str
    raw_value: str
    normalized_value: float | None = None
    unit: str | None = None
    comparison_target: str | None = Field(default=None, description="Associated algorithm/model (e.g. LSTM, Random Forest)")
    source_page: int
    source_section: str | None = None
    evidence_id: str
    source_text: str


class ScientificDatasetRead(ORMBase):
    dataset_name: str
    dataset_source: str | None = None
    sample_count_raw: str | None = None
    sample_count_numeric: int | None = None
    sensor_count: int | None = None
    feature_count: int | None = None
    source_page: int
    evidence_id: str
    source_text: str


class ScientificExperimentRead(ORMBase):
    algorithms: list[str] = Field(default_factory=list)
    baselines: list[str] = Field(default_factory=list)
    validation_strategy: str | None = None
    hardware_sensors: list[str] = Field(default_factory=list)
    source_page: int
    evidence_id: str
    source_text: str


class ComparisonRecordRead(ORMBase):
    dimension: str
    proposal_value: str
    paper_value: str
    source_evidence_id: str
    status: str = Field(description="MATCHING, DIFFERENT, PARTIALLY_MATCHING, NOT_REPORTED, NOT_COMPARABLE")


class ComparisonSummaryRead(ORMBase):
    proposal_id: str
    paper_id: str
    paper_title: str
    comparisons: list[ComparisonRecordRead]
