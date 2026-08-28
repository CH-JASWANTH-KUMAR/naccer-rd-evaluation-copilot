import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.evaluation import Evaluation, EvaluationCriterion


class EvaluationEvidence(Base):
    __tablename__ = "evaluation_evidences"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    evaluation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("evaluations.id", ondelete="CASCADE"), nullable=False
    )
    criterion_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("evaluation_criteria.id", ondelete="SET NULL"), nullable=True
    )

    evidence_type: Mapped[str] = mapped_column(String(100), nullable=False, default="PROPOSAL_SECTION")
    source_type: Mapped[str] = mapped_column(String(100), nullable=False, default="PROPOSAL")
    source_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)

    source_page_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_page_end: Mapped[int | None] = mapped_column(Integer, nullable=True)

    evidence_text: Mapped[str] = mapped_column(Text, nullable=False)
    reviewer_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    # Relationships
    evaluation: Mapped["Evaluation"] = relationship("Evaluation", back_populates="evidences")
    criterion: Mapped["EvaluationCriterion | None"] = relationship("EvaluationCriterion", back_populates="evidences")
