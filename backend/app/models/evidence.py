import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.proposal import Proposal


class Evidence(Base):
    __tablename__ = "evidences"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    proposal_id: Mapped[str] = mapped_column(String(36), ForeignKey("proposals.id", ondelete="CASCADE"), nullable=False)

    evidence_type: Mapped[str] = mapped_column(String(100), nullable=False, default="NOVELTY_CLAIM")
    source_type: Mapped[str] = mapped_column(String(100), nullable=False, default="DOCUMENT_SNIPPET")
    source_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)

    document_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    section: Mapped[str | None] = mapped_column(String(255), nullable=True)

    snippet: Mapped[str] = mapped_column(Text, nullable=False)

    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    relevance_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    # Relationships
    proposal: Mapped["Proposal"] = relationship("Proposal", back_populates="evidences")
