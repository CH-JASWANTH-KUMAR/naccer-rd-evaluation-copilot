import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.ai_analysis import AIAnalysis
    from app.models.assignment import EvaluationAssignment
    from app.models.decision_pack import EvaluationDecisionPack
    from app.models.evaluation_audit import EvaluationAuditEvent
    from app.models.evaluation_evidence import EvaluationEvidence
    from app.models.proposal import Proposal
    from app.models.rubric import EvaluationRubric


class Evaluation(Base):
    __tablename__ = "evaluations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    proposal_id: Mapped[str] = mapped_column(String(36), ForeignKey("proposals.id", ondelete="CASCADE"), nullable=False)
    reviewer_id: Mapped[str] = mapped_column(String(255), nullable=False, default="Rev-01")
    rubric_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("evaluation_rubrics.id", ondelete="SET NULL"), nullable=True
    )
    rubric_version: Mapped[str] = mapped_column(String(50), nullable=False, default="v1.0")

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="DRAFT")
    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    reviewer_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewer_recommendation: Mapped[str] = mapped_column(String(50), nullable=False, default="FAVORABLE_WITH_CONDITIONS")

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    # Relationships
    proposal: Mapped["Proposal"] = relationship("Proposal", back_populates="evaluations")
    rubric: Mapped["EvaluationRubric | None"] = relationship("EvaluationRubric", back_populates="evaluations")
    criteria: Mapped[list["EvaluationCriterion"]] = relationship(
        "EvaluationCriterion", back_populates="evaluation", cascade="all, delete-orphan"
    )
    evidences: Mapped[list["EvaluationEvidence"]] = relationship(
        "EvaluationEvidence", back_populates="evaluation", cascade="all, delete-orphan"
    )
    audit_events: Mapped[list["EvaluationAuditEvent"]] = relationship(
        "EvaluationAuditEvent", back_populates="evaluation", cascade="all, delete-orphan"
    )
    ai_analyses: Mapped[list["AIAnalysis"]] = relationship(
        "AIAnalysis", back_populates="evaluation", cascade="all, delete-orphan"
    )
    decision_packs: Mapped[list["EvaluationDecisionPack"]] = relationship(
        "EvaluationDecisionPack", back_populates="evaluation", cascade="all, delete-orphan"
    )
    assignments: Mapped[list["EvaluationAssignment"]] = relationship(
        "EvaluationAssignment", back_populates="evaluation", cascade="all, delete-orphan"
    )


class EvaluationCriterion(Base):
    __tablename__ = "evaluation_criteria"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    evaluation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("evaluations.id", ondelete="CASCADE"), nullable=False
    )
    criterion_key: Mapped[str | None] = mapped_column(String(100), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    max_score: Mapped[float] = mapped_column(Float, nullable=False, default=10.0)
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    weighted_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    justification_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    # Relationships
    evaluation: Mapped["Evaluation"] = relationship("Evaluation", back_populates="criteria")
    evidences: Mapped[list["EvaluationEvidence"]] = relationship(
        "EvaluationEvidence", back_populates="criterion", cascade="all, delete-orphan"
    )
