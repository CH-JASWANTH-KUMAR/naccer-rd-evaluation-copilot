import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.historical_project import HistoricalProject
    from app.models.historical_source_document import HistoricalSourceDocument


class ImportBatch(Base):
    __tablename__ = "import_batches"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, default="OFFICIAL")
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    document_name: Mapped[str] = mapped_column(String(255), nullable=False)
    document_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    total_records: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    successful_records: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    needs_review_records: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_records: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="STARTED")
    imported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    # Relationships
    source_documents: Mapped[list["HistoricalSourceDocument"]] = relationship(
        "HistoricalSourceDocument", back_populates="import_batch", cascade="all, delete-orphan"
    )
    historical_projects: Mapped[list["HistoricalProject"]] = relationship(
        "HistoricalProject", back_populates="import_batch"
    )
