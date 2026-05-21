from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.article import Article
    from app.models.ingest_log import IngestLog


class Source(Base):
    __tablename__ = "sources"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    category: Mapped[str] = mapped_column(String(64), nullable=False, default="other")
    category_label: Mapped[str | None] = mapped_column(String(128))
    subcategory: Mapped[str | None] = mapped_column(String(128))
    section: Mapped[str | None] = mapped_column(String(128))
    source_type: Mapped[str] = mapped_column(String(32), nullable=False, default="unknown")
    url: Mapped[str | None] = mapped_column(String(2048))
    language: Mapped[str | None] = mapped_column(String(32))
    region: Mapped[str | None] = mapped_column(String(64))
    tier: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    fetch_interval_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    api_key_env: Mapped[str | None] = mapped_column(String(64))
    license_notes: Mapped[str | None] = mapped_column(Text)
    source_file: Mapped[str | None] = mapped_column(String(128))
    last_ingested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    articles: Mapped[list["Article"]] = relationship(
        "Article",
        back_populates="source",
        cascade="all, delete-orphan",
    )
    ingest_logs: Mapped[list["IngestLog"]] = relationship(
        "IngestLog",
        back_populates="source",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_sources_category_tier", "category", "tier"),
        Index("ix_sources_enabled", "enabled"),
    )

    def __repr__(self) -> str:
        return f"<Source(id={self.id}, slug={self.slug!r})>"
