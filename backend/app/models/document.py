import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.document_page import DocumentPage
    from app.models.proposal import Proposal
    from app.models.proposal_section import ProposalSection


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    proposal_id: Mapped[str] = mapped_column(String(36), ForeignKey("proposals.id", ondelete="CASCADE"), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False, default="application/pdf")
    file_size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    processing_status: Mapped[str] = mapped_column(String(50), nullable=False, default="UPLOADED")
    processing_error: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    # Relationships
    proposal: Mapped["Proposal"] = relationship("Proposal", back_populates="documents")
    pages: Mapped[list["DocumentPage"]] = relationship(
        "DocumentPage", back_populates="document", cascade="all, delete-orphan", order_by="DocumentPage.page_number"
    )
    sections: Mapped[list["ProposalSection"]] = relationship(
        "ProposalSection",
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="ProposalSection.start_page",
    )
