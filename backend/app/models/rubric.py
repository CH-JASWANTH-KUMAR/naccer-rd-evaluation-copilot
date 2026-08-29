import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.evaluation import Evaluation


class EvaluationRubric(Base):
    __tablename__ = "evaluation_rubrics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False, default="v1.0")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    # Relationships
    criteria: Mapped[list["RubricCriterion"]] = relationship(
        "RubricCriterion", back_populates="rubric", cascade="all, delete-orphan", order_by="RubricCriterion.display_order"
    )
    evaluations: Mapped[list["Evaluation"]] = relationship("Evaluation", back_populates="rubric")


class RubricCriterion(Base):
    __tablename__ = "rubric_criteria"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    rubric_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("evaluation_rubrics.id", ondelete="CASCADE"), nullable=False
    )
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, default="TECHNICAL")
    max_score: Mapped[float] = mapped_column(Float, nullable=False, default=10.0)
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    evidence_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Official Guideline Provenance (Phase P0.6 / Step 7)
    source_document: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_section: Mapped[str | None] = mapped_column(String(100), nullable=True)
    original_criterion_wording: Mapped[str | None] = mapped_column(Text, nullable=True)
    scoring_instructions: Mapped[str | None] = mapped_column(String(255), nullable=True, default="NOT_SPECIFIED")
    scoring_scale: Mapped[str | None] = mapped_column(String(100), nullable=True, default="NOT_SPECIFIED")
    evidence_requirements: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    # Relationships
    rubric: Mapped["EvaluationRubric"] = relationship("EvaluationRubric", back_populates="criteria")
