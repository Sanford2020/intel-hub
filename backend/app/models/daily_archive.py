"""Daily archive snapshot — briefing + category heat metrics."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy import Date, DateTime, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.db.base import Base

JsonColumn = JSON().with_variant(JSONB(), "postgresql")


class DailyArchive(Base):
    __tablename__ = "daily_archives"

    archive_date: Mapped[date] = mapped_column(Date, nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="Asia/Shanghai")
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    window_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    briefing_json: Mapped[dict[str, Any] | None] = mapped_column(JsonColumn, nullable=True)
    metrics_json: Mapped[dict[str, Any] | None] = mapped_column(JsonColumn, nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="success")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("archive_date", name="uq_daily_archives_archive_date"),
    )

    def __repr__(self) -> str:
        return f"<DailyArchive(id={self.id}, archive_date={self.archive_date})>"
