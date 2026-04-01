from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    analysis_id: Mapped[int] = mapped_column(
        ForeignKey("analyses.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    match_score: Mapped[int] = mapped_column(Integer, nullable=False)
    candidate_profile_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    gap_analysis_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    final_report_json: Mapped[dict] = mapped_column(JSON, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    analysis = relationship("Analysis", back_populates="report")