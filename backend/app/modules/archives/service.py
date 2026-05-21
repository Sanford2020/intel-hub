from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, defer

from app.config import settings
from app.models.daily_archive import DailyArchive
from app.modules.archives.metrics import archive_window_bounds, compute_daily_metrics
from app.modules.briefings.service import build_daily_briefing_sync


class ArchiveService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_archives(
        self,
        *,
        page: int,
        page_size: int,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> tuple[list[DailyArchive], int]:
        stmt = select(DailyArchive).options(defer(DailyArchive.briefing_json))
        count_stmt = select(func.count()).select_from(DailyArchive)
        if date_from is not None:
            stmt = stmt.where(DailyArchive.archive_date >= date_from)
            count_stmt = count_stmt.where(DailyArchive.archive_date >= date_from)
        if date_to is not None:
            stmt = stmt.where(DailyArchive.archive_date <= date_to)
            count_stmt = count_stmt.where(DailyArchive.archive_date <= date_to)
        total = int((await self.session.scalar(count_stmt)) or 0)
        stmt = (
            stmt.order_by(DailyArchive.archive_date.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = (await self.session.scalars(stmt)).all()
        return list(rows), total

    async def get_by_date(self, archive_date: date) -> DailyArchive | None:
        return await self.session.scalar(
            select(DailyArchive).where(DailyArchive.archive_date == archive_date)
        )

    async def category_heat_trends(self, *, days: int) -> dict[str, Any]:
        tz = settings.archive_timezone
        end_date = datetime.now(ZoneInfo(tz)).date()
        start_date = end_date - timedelta(days=max(days - 1, 0))
        stmt = (
            select(DailyArchive)
            .where(DailyArchive.archive_date >= start_date)
            .where(DailyArchive.archive_date <= end_date)
            .order_by(DailyArchive.archive_date.asc())
        )
        archives = list((await self.session.scalars(stmt)).all())

        points_by_category: dict[str, list[dict[str, Any]]] = {}
        categories: set[str] = set()
        for archive in archives:
            metrics = archive.metrics_json or {}
            for row in metrics.get("category_heat") or []:
                cat = row.get("category") or "other"
                categories.add(cat)
                points_by_category.setdefault(cat, []).append(
                    {
                        "date": archive.archive_date.isoformat(),
                        "heat_score": row.get("heat_score", 0),
                        "articles": row.get("articles", 0),
                        "high_relevance": row.get("high_relevance", 0),
                        "avg_relevance": row.get("avg_relevance", 0),
                        "category_label": row.get("category_label"),
                    }
                )

        return {
            "timezone": tz,
            "days": days,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "categories": sorted(categories),
            "points_by_category": points_by_category,
        }


def create_or_update_daily_archive_sync(
    session: Session,
    *,
    archive_date: date | None = None,
    now: datetime | None = None,
) -> DailyArchive:
    if not settings.archive_enabled:
        raise ValueError("ARCHIVE_ENABLED=false")

    hours = settings.archive_window_hours
    tz = settings.archive_timezone
    window_start, window_end, computed_date = archive_window_bounds(
        hours=hours, timezone=tz, now=now
    )
    target_date = archive_date or computed_date
    min_relevance = settings.archive_min_relevance

    existing = session.scalar(
        select(DailyArchive).where(DailyArchive.archive_date == target_date)
    )

    try:
        briefing = build_daily_briefing_sync(
            session,
            hours=hours,
            limit=settings.archive_briefing_limit,
            min_relevance=min_relevance,
            include_markdown=True,
            now=now,
        )
        metrics = compute_daily_metrics(
            session,
            window_start=window_start,
            window_end=window_end,
            min_relevance=min_relevance,
        )
        metrics["briefing_meta"] = {
            "item_count": briefing.meta.item_count,
            "min_relevance": briefing.meta.min_relevance,
            "ai_mode": briefing.meta.ai_mode,
        }

        record = existing or DailyArchive(archive_date=target_date)
        record.timezone = tz
        record.window_start = window_start
        record.window_end = window_end
        record.briefing_json = briefing.model_dump(mode="json")
        record.metrics_json = metrics
        record.status = "success"
        record.error_message = None
        if existing is None:
            session.add(record)
        session.flush()
        return record
    except Exception as exc:  # noqa: BLE001
        record = existing or DailyArchive(archive_date=target_date)
        record.timezone = tz
        record.window_start = window_start
        record.window_end = window_end
        record.status = "failed"
        record.error_message = str(exc)[:2000]
        if existing is None:
            session.add(record)
        session.flush()
        raise
