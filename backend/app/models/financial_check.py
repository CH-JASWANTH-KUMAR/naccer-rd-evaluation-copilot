import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.proposal import Proposal


class FinancialCheck(Base):
    __tablename__ = "financial_checks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    proposal_id: Mapped[str] = mapped_column(String(36), ForeignKey("proposals.id", ondelete="CASCADE"), nullable=False)

    check_type: Mapped[str] = mapped_column(String(100), nullable=False, default="COST_HEAD_VERIFICATION")
    description: Mapped[str] = mapped_column(String(500), nullable=False)

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING")

    expected_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    actual_value: Mapped[float | None] = mapped_column(Float, nullable=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    # Relationships
    proposal: Mapped["Proposal"] = relationship("Proposal", back_populates="financial_checks")
