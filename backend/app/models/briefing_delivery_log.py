"""Briefing delivery log — tracks each push attempt."""

from __future__ import annotations

from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class BriefingDeliveryLog(Base):
    __tablename__ = "briefing_delivery_logs"

    channel: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    webhook_status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    item_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    briefing_date: Mapped[str | None] = mapped_column(String(32), nullable=True)

    def __repr__(self) -> str:
        return (
            f"<BriefingDeliveryLog(id={self.id}, channel={self.channel}, "
            f"status={self.status})>"
        )
