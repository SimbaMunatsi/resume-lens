from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    resume_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    resume_source: Mapped[str] = mapped_column(String(50), nullable=False)
    resume_text: Mapped[str] = mapped_column(Text, nullable=False)

    job_description_source: Mapped[str | None] = mapped_column(String(50), nullable=True)
    job_description_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    job_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    target_role: Mapped[str | None] = mapped_column(String(255), nullable=True)
    rewrite_style: Mapped[str | None] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    report = relationship("Report", back_populates="analysis", uselist=False, cascade="all, delete-orphan")