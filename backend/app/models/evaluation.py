import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.proposal import Proposal


class Evaluation(Base):
    __tablename__ = "evaluations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    proposal_id: Mapped[str] = mapped_column(String(36), ForeignKey("proposals.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="DRAFT")
    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    # Relationships
    proposal: Mapped["Proposal"] = relationship("Proposal", back_populates="evaluations")
    criteria: Mapped[list["EvaluationCriterion"]] = relationship(
        "EvaluationCriterion", back_populates="evaluation", cascade="all, delete-orphan"
    )


class EvaluationCriterion(Base):
    __tablename__ = "evaluation_criteria"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    evaluation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("evaluations.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    max_score: Mapped[float] = mapped_column(Float, nullable=False, default=25.0)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    # Relationships
    evaluation: Mapped["Evaluation"] = relationship("Evaluation", back_populates="criteria")
