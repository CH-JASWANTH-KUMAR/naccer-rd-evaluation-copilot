import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.import_batch import ImportBatch


class HistoricalSourceDocument(Base):
    __tablename__ = "historical_source_documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    import_batch_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("import_batches.id", ondelete="CASCADE"), nullable=False
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    page_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    extraction_status: Mapped[str] = mapped_column(String(50), nullable=False, default="PROCESSED")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    # Relationship
    import_batch: Mapped["ImportBatch"] = relationship("ImportBatch", back_populates="source_documents")
