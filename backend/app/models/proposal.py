import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.audit_event import AuditEvent
    from app.models.document import Document
    from app.models.evaluation import Evaluation
    from app.models.evidence import Evidence
    from app.models.financial_check import FinancialCheck
    from app.models.institution import Institution
    from app.models.proposal_section import ProposalSection
    from app.models.review_comment import ReviewComment


class Proposal(Base):
    __tablename__ = "proposals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    institution_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False
    )
    principal_investigator: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), nullable=False)

    problem_statement: Mapped[str | None] = mapped_column(Text, nullable=True)
    objectives: Mapped[str | None] = mapped_column(Text, nullable=True)
    methodology: Mapped[str | None] = mapped_column(Text, nullable=True)
    literature_review: Mapped[str | None] = mapped_column(Text, nullable=True)
    expected_outcomes: Mapped[str | None] = mapped_column(Text, nullable=True)
    timeline: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="UNDER_REVIEW")
    priority: Mapped[str] = mapped_column(String(50), nullable=False, default="MEDIUM")
    budget_total: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    submission_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    # Relationships
    institution: Mapped["Institution"] = relationship("Institution", back_populates="proposals")
    documents: Mapped[list["Document"]] = relationship(
        "Document", back_populates="proposal", cascade="all, delete-orphan"
    )
    sections: Mapped[list["ProposalSection"]] = relationship(
        "ProposalSection",
        back_populates="proposal",
        cascade="all, delete-orphan",
        order_by="ProposalSection.start_page",
    )
    evaluations: Mapped[list["Evaluation"]] = relationship(
        "Evaluation", back_populates="proposal", cascade="all, delete-orphan"
    )
    evidences: Mapped[list["Evidence"]] = relationship(
        "Evidence", back_populates="proposal", cascade="all, delete-orphan"
    )
    financial_checks: Mapped[list["FinancialCheck"]] = relationship(
        "FinancialCheck", back_populates="proposal", cascade="all, delete-orphan"
    )
    review_comments: Mapped[list["ReviewComment"]] = relationship(
        "ReviewComment", back_populates="proposal", cascade="all, delete-orphan"
    )
    audit_events: Mapped[list["AuditEvent"]] = relationship(
        "AuditEvent", back_populates="proposal", cascade="all, delete-orphan"
    )
