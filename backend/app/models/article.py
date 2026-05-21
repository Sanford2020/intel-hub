from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.alert_event import AlertEvent
    from app.models.intelligence_report import IntelligenceReport
    from app.models.source import Source


class Article(Base):
    __tablename__ = "articles"

    source_id: Mapped[int] = mapped_column(
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    url: Mapped[str | None] = mapped_column(String(2048))
    content: Mapped[str | None] = mapped_column(Text)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    language: Mapped[str | None] = mapped_column(String(32))

    source: Mapped["Source"] = relationship("Source", back_populates="articles")
    intelligence_report: Mapped["IntelligenceReport | None"] = relationship(
        "IntelligenceReport",
        back_populates="article",
        uselist=False,
        cascade="all, delete-orphan",
    )
    alert_events: Mapped[list["AlertEvent"]] = relationship(
        "AlertEvent",
        back_populates="article",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("content_hash", name="uq_articles_content_hash"),
        Index("ix_articles_published_at", "published_at"),
    )

    def __repr__(self) -> str:
        return f"<Article(id={self.id}, source_id={self.source_id})>"
