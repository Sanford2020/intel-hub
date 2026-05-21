from __future__ import annotations

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.modules.briefings.aggregator import (
    briefing_window,
    fetch_daily_rows,
    fetch_daily_rows_sync,
)
from app.modules.briefings.formatter import assemble_daily_briefing
from app.modules.briefings.schemas import DailyBriefingRead


class BriefingService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def build_daily(
        self,
        *,
        hours: int = 24,
        limit: int = 20,
        min_relevance: float | None = None,
        lang: str | None = None,
        include_markdown: bool = False,
        now: datetime | None = None,
    ) -> DailyBriefingRead:
        window_start, window_end = briefing_window(hours=hours, now=now)
        rows = await fetch_daily_rows(
            self.session,
            window_start=window_start,
            limit=limit,
            min_relevance=min_relevance,
            lang=lang,
        )
        return assemble_daily_briefing(
            rows,
            window_hours=hours,
            window_start=window_start,
            window_end=window_end,
            limit=limit,
            min_relevance=min_relevance,
            include_markdown=include_markdown,
        )


def build_daily_briefing_sync(
    session: Session,
    *,
    hours: int = 24,
    limit: int = 20,
    min_relevance: float | None = None,
    lang: str | None = None,
    include_markdown: bool = True,
    now: datetime | None = None,
) -> DailyBriefingRead:
    window_start, window_end = briefing_window(hours=hours, now=now)
    rows = fetch_daily_rows_sync(
        session,
        window_start=window_start,
        limit=limit,
        min_relevance=min_relevance,
        lang=lang,
    )
    return assemble_daily_briefing(
        rows,
        window_hours=hours,
        window_start=window_start,
        window_end=window_end,
        limit=limit,
        min_relevance=min_relevance,
        include_markdown=include_markdown,
    )
