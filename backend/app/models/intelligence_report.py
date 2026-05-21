from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.article import Article

# SQLite tests use generic JSON; PostgreSQL uses JSONB.
JsonColumn = JSON().with_variant(JSONB(), "postgresql")


class IntelligenceReport(Base):
    __tablename__ = "intelligence_reports"

    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    tags: Mapped[list[str]] = mapped_column(JsonColumn, nullable=False, default=list)
    entities: Mapped[list[dict[str, Any]]] = mapped_column(
        JsonColumn, nullable=False, default=list
    )
    relevance_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    sentiment: Mapped[str | None] = mapped_column(String(32))
    language: Mapped[str | None] = mapped_column(String(32))
    model: Mapped[str | None] = mapped_column(String(128))
    prompt_template: Mapped[str | None] = mapped_column(String(128))
    raw_json: Mapped[dict[str, Any] | None] = mapped_column(JsonColumn)

    article: Mapped["Article"] = relationship(
        "Article", back_populates="intelligence_report", uselist=False
    )

    __table_args__ = (
        UniqueConstraint("article_id", name="uq_intelligence_reports_article_id"),
    )

    def __repr__(self) -> str:
        return f"<IntelligenceReport(id={self.id}, article_id={self.article_id})>"
