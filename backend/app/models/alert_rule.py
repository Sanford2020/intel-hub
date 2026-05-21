from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.alert_event import AlertEvent

JsonColumn = JSON().with_variant(JSONB(), "postgresql")


class AlertRule(Base):
    __tablename__ = "alert_rules"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    keywords: Mapped[list[str]] = mapped_column(JsonColumn, nullable=False, default=list)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    match_in: Mapped[str] = mapped_column(String(32), nullable=False, default="all")
    channel: Mapped[str] = mapped_column(String(32), nullable=False, default="log")
    channel_config: Mapped[dict[str, Any] | None] = mapped_column(JsonColumn)

    events: Mapped[list["AlertEvent"]] = relationship(
        "AlertEvent",
        back_populates="rule",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<AlertRule(id={self.id}, name={self.name!r})>"
