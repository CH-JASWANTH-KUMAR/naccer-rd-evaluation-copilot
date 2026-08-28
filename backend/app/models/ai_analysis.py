import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.evaluation import Evaluation


class AIAnalysis(Base):
    __tablename__ = "ai_analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    evaluation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("evaluations.id", ondelete="CASCADE"), nullable=False
    )
    provider: Mapped[str] = mapped_column(String(100), nullable=False, default="deterministic-grounded-v1")
    model: Mapped[str] = mapped_column(String(100), nullable=False, default="naccer-evidence-reasoner-v1")
    prompt_version: Mapped[str] = mapped_column(String(50), nullable=False, default="evidence-analysis-v1")
    input_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    output_json: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="GENERATED")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    # Relationships
    evaluation: Mapped["Evaluation"] = relationship("Evaluation", back_populates="ai_analyses")
