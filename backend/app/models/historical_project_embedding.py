import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.historical_project import HistoricalProject


class HistoricalProjectEmbedding(Base):
    __tablename__ = "historical_project_embeddings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    historical_project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("historical_projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    embedding_model: Mapped[str] = mapped_column(String(100), nullable=False, default="tfidf-deterministic-v1")
    embedding_dimension: Mapped[int] = mapped_column(Integer, nullable=False, default=128)
    vector_data: Mapped[str] = mapped_column(Text, nullable=False)  # JSON serialized floats or term frequencies
    text_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    # Relationship
    historical_project: Mapped["HistoricalProject"] = relationship("HistoricalProject", back_populates="embeddings")
