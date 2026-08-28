import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.proposal import Proposal


class ReviewComment(Base):
    __tablename__ = "review_comments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    proposal_id: Mapped[str] = mapped_column(String(36), ForeignKey("proposals.id", ondelete="CASCADE"), nullable=False)
    evaluation_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("evaluations.id", ondelete="SET NULL"), nullable=True
    )

    author_id: Mapped[str] = mapped_column(String(255), nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, default="GENERAL")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    # Relationships
    proposal: Mapped["Proposal"] = relationship("Proposal", back_populates="review_comments")
