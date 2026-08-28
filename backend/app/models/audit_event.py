import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.proposal import Proposal


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    proposal_id: Mapped[str] = mapped_column(String(36), ForeignKey("proposals.id", ondelete="CASCADE"), nullable=False)

    action: Mapped[str] = mapped_column(String(255), nullable=False)
    performed_by: Mapped[str] = mapped_column(String(255), nullable=False)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    # Relationships
    proposal: Mapped["Proposal"] = relationship("Proposal", back_populates="audit_events")
