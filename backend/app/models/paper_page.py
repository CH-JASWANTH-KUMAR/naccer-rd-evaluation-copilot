import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.research_paper import ResearchPaper


class PaperPage(Base):
    __tablename__ = "paper_pages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    research_paper_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("research_papers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    extracted_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    character_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    detected_sections: Mapped[str | None] = mapped_column(Text, nullable=True)
    extraction_status: Mapped[str] = mapped_column(String(50), nullable=False, default="COMPLETED")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    # Relationship to ResearchPaper
    paper: Mapped["ResearchPaper"] = relationship("ResearchPaper", back_populates="pages")
