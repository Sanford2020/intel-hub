from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.alert_rule import AlertRule
    from app.models.article import Article

JsonColumn = JSON().with_variant(JSONB(), "postgresql")


class AlertEvent(Base):
    __tablename__ = "alert_events"

    rule_id: Mapped[int] = mapped_column(
        ForeignKey("alert_rules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    matched_keywords: Mapped[list[str]] = mapped_column(JsonColumn, nullable=False, default=list)
    notification_status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    notification_detail: Mapped[str | None] = mapped_column(Text)

    rule: Mapped["AlertRule"] = relationship("AlertRule", back_populates="events")
    article: Mapped["Article"] = relationship("Article", back_populates="alert_events")

    __table_args__ = (
        UniqueConstraint("rule_id", "article_id", name="uq_alert_events_rule_article"),
    )

    def __repr__(self) -> str:
        return f"<AlertEvent(id={self.id}, rule_id={self.rule_id}, article_id={self.article_id})>"
