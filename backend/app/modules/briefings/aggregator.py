from __future__ import annotations

from collections import namedtuple
from datetime import UTC, datetime, timedelta

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.models.article import Article
from app.models.intelligence_report import IntelligenceReport
from app.models.source import Source

BriefingRow = namedtuple("BriefingRow", ["article", "report", "source_name"])


def _effective_timestamp():
    return func.coalesce(Article.published_at, Article.created_at)


def build_daily_briefing_statement(
    *,
    window_start: datetime,
    limit: int,
    min_relevance: float | None = None,
    lang: str | None = None,
) -> Select[tuple[Article, IntelligenceReport, str]]:
    effective_ts = _effective_timestamp()
    stmt = (
        select(Article, IntelligenceReport, Source.name)
        .join(IntelligenceReport, IntelligenceReport.article_id == Article.id)
        .join(Source, Source.id == Article.source_id)
        .where(effective_ts >= window_start)
        .order_by(
            IntelligenceReport.relevance_score.desc(),
            effective_ts.desc(),
        )
        .limit(limit)
    )
    if min_relevance is not None:
        stmt = stmt.where(IntelligenceReport.relevance_score >= min_relevance)
    if lang is not None:
        stmt = stmt.where(Article.language == lang)
    return stmt


async def fetch_daily_rows(
    session: AsyncSession,
    *,
    window_start: datetime,
    limit: int,
    min_relevance: float | None = None,
    lang: str | None = None,
) -> list[BriefingRow]:
    stmt = build_daily_briefing_statement(
        window_start=window_start,
        limit=limit,
        min_relevance=min_relevance,
        lang=lang,
    )
    result = await session.execute(stmt)
    return [
        BriefingRow(article=row[0], report=row[1], source_name=row[2])
        for row in result.all()
    ]


def fetch_daily_rows_sync(
    session: Session,
    *,
    window_start: datetime,
    limit: int,
    min_relevance: float | None = None,
    lang: str | None = None,
) -> list[BriefingRow]:
    stmt = build_daily_briefing_statement(
        window_start=window_start,
        limit=limit,
        min_relevance=min_relevance,
        lang=lang,
    )
    result = session.execute(stmt)
    return [
        BriefingRow(article=row[0], report=row[1], source_name=row[2])
        for row in result.all()
    ]


def briefing_window(
    *,
    hours: int,
    now: datetime | None = None,
) -> tuple[datetime, datetime]:
    window_end = now or datetime.now(UTC)
    window_start = window_end - timedelta(hours=hours)
    return window_start, window_end
