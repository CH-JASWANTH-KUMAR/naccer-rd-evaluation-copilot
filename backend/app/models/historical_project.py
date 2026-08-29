import uuid
from datetime import UTC, date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.historical_project_embedding import HistoricalProjectEmbedding
    from app.models.import_batch import ImportBatch


class HistoricalProject(Base):
    __tablename__ = "historical_projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    institution: Mapped[str] = mapped_column(String(255), nullable=False)
    sub_implementing_agencies: Mapped[str | None] = mapped_column(String(500), nullable=True)
    domain: Mapped[str] = mapped_column(String(255), nullable=False)

    objectives: Mapped[str | None] = mapped_column(Text, nullable=True)
    methodology: Mapped[str | None] = mapped_column(Text, nullable=True)
    technology: Mapped[str | None] = mapped_column(Text, nullable=True)
    expected_outcomes: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="ONGOING")
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    completion_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    approved_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    approved_cost_raw: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Provenance fields
    source: Mapped[str] = mapped_column(String(255), nullable=False, default="CIL/CMPDI")
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, default="OFFICIAL")
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_document_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_page_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_page_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_record_identifier: Mapped[str | None] = mapped_column(String(255), nullable=True)
    raw_record_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Verification workflow fields
    verification_status: Mapped[str] = mapped_column(String(50), nullable=False, default="NEEDS_REVIEW")
    verification_timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    import_batch_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("import_batches.id", ondelete="SET NULL"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    # Relationships
    import_batch: Mapped["ImportBatch | None"] = relationship("ImportBatch", back_populates="historical_projects")
    embeddings: Mapped[list["HistoricalProjectEmbedding"]] = relationship(
        "HistoricalProjectEmbedding", back_populates="historical_project", cascade="all, delete-orphan"
    )
