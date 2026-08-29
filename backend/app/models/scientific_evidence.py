import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.paper_page import PaperPage
    from app.models.research_paper import ResearchPaper


class ScientificEvidence(Base):
    __tablename__ = "scientific_evidences"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    research_paper_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("research_papers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    paper_page_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("paper_pages.id", ondelete="SET NULL"), nullable=True, index=True
    )

    evidence_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    parent_evidence_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    evidence_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="METRIC"
    )  # METHODOLOGY, ALGORITHM, DATASET, FEATURE, EXPERIMENT, BASELINE, METRIC, RESULT, VALIDATION, LIMITATION, HARDWARE, SENSOR
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="METRIC")

    field_name: Mapped[str] = mapped_column(String(255), nullable=False)
    value_text: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    unit: Mapped[str | None] = mapped_column(String(100), nullable=True)
    comparison_target: Mapped[str | None] = mapped_column(String(255), nullable=True)

    confidence: Mapped[str] = mapped_column(
        String(50), nullable=False, default="HIGH"
    )  # HIGH, MEDIUM, LOW (Labeled strictly as EXTRACTION CONFIDENCE)
    source_page_start: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    source_page_end: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    source_section: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_quote_or_snippet: Mapped[str] = mapped_column(Text, nullable=False, default="")
    extraction_method: Mapped[str] = mapped_column(
        String(50), nullable=False, default="RULE_BASED"
    )  # RULE_BASED, LLM_STRUCTURED, HYBRID

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    # Relationships
    paper: Mapped["ResearchPaper"] = relationship("ResearchPaper")
    page: Mapped["PaperPage | None"] = relationship("PaperPage")
