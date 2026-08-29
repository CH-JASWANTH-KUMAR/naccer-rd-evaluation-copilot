import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.paper_page import PaperPage


class ResearchPaper(Base):
    __tablename__ = "research_papers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    authors: Mapped[str | None] = mapped_column(String(500), nullable=True)
    abstract: Mapped[str | None] = mapped_column(Text, nullable=True)
    publication_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    journal_or_conference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    doi: Mapped[str | None] = mapped_column(String(255), nullable=True)
    research_domain: Mapped[str] = mapped_column(String(255), nullable=False, default="Coal Mining & Automation")
    keywords: Mapped[str | None] = mapped_column(Text, nullable=True)

    source_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    source_document_type: Mapped[str] = mapped_column(String(50), nullable=False, default="PDF")
    page_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    storage_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    extraction_status: Mapped[str] = mapped_column(String(50), nullable=False, default="COMPLETED")
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    # Relationship to PaperPage
    pages: Mapped[list["PaperPage"]] = relationship(
        "PaperPage", back_populates="paper", cascade="all, delete-orphan", order_by="PaperPage.page_number"
    )
