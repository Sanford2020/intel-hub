from __future__ import annotations

import math
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.models.daily_archive import DailyArchive
from app.modules.archives.schemas import (
    ArchiveDetailRead,
    ArchiveDetailResponse,
    ArchiveListResponse,
    ArchiveSummaryRead,
    CategoryHeatTrendsResponse,
)
from app.modules.archives.service import ArchiveService

router = APIRouter(prefix="/archives", tags=["archives"])


def get_archive_service(session: AsyncSession = Depends(get_session)) -> ArchiveService:
    return ArchiveService(session)


def _to_summary(archive: DailyArchive) -> ArchiveSummaryRead:
    metrics = archive.metrics_json or {}
    category_heat = metrics.get("category_heat") or []
    top = category_heat[0] if category_heat else None
    briefing_meta = metrics.get("briefing_meta") or {}
    analysis = metrics.get("analysis") or {}
    ingest = metrics.get("ingest") or {}
    return ArchiveSummaryRead(
        archive_date=archive.archive_date,
        timezone=archive.timezone,
        status=archive.status,
        item_count=int(briefing_meta.get("item_count") or 0),
        articles_created=int(ingest.get("articles_created") or 0),
        high_relevance_count=int(analysis.get("high_relevance_count") or 0),
        top_category=top.get("category") if top else None,
        top_heat_score=top.get("heat_score") if top else None,
    )


def _to_detail(archive: DailyArchive) -> ArchiveDetailRead:
    return ArchiveDetailRead(
        id=archive.id,
        created_at=archive.created_at,
        updated_at=archive.updated_at,
        archive_date=archive.archive_date,
        timezone=archive.timezone,
        window_start=archive.window_start,
        window_end=archive.window_end,
        status=archive.status,
        error_message=archive.error_message,
        briefing=archive.briefing_json,
        metrics=archive.metrics_json,
    )


@router.get("", response_model=ArchiveListResponse)
async def list_archives(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    date_from: date | None = Query(None, alias="from"),
    date_to: date | None = Query(None, alias="to"),
    service: ArchiveService = Depends(get_archive_service),
) -> ArchiveListResponse:
    rows, total = await service.list_archives(
        page=page,
        page_size=page_size,
        date_from=date_from,
        date_to=date_to,
    )
    total_pages = max(1, math.ceil(total / page_size)) if total else 1
    return ArchiveListResponse(
        data=[_to_summary(row) for row in rows],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/trends/category-heat", response_model=CategoryHeatTrendsResponse)
async def category_heat_trends(
    days: int = Query(30, ge=1, le=365),
    service: ArchiveService = Depends(get_archive_service),
) -> CategoryHeatTrendsResponse:
    data = await service.category_heat_trends(days=days)
    return CategoryHeatTrendsResponse(data=data)


@router.get("/{archive_date}", response_model=ArchiveDetailResponse)
async def get_archive(
    archive_date: date,
    service: ArchiveService = Depends(get_archive_service),
) -> ArchiveDetailResponse:
    archive = await service.get_by_date(archive_date)
    if not archive:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archive not found")
    return ArchiveDetailResponse(data=_to_detail(archive))
