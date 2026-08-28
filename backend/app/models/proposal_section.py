import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.document import Document
    from app.models.proposal import Proposal


class ProposalSection(Base):
    __tablename__ = "proposal_sections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    proposal_id: Mapped[str] = mapped_column(String(36), ForeignKey("proposals.id", ondelete="CASCADE"), nullable=False)
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)

    section_type: Mapped[str] = mapped_column(String(100), nullable=False)
    section_title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")

    start_page: Mapped[int] = mapped_column(Integer, nullable=False)
    end_page: Mapped[int] = mapped_column(Integer, nullable=False)

    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    # Relationships
    proposal: Mapped["Proposal"] = relationship("Proposal", back_populates="sections")
    document: Mapped["Document"] = relationship("Document", back_populates="sections")
