from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import Field

from app.schemas.base import BaseSchema, TimestampSchema


class ArchiveSummaryRead(BaseSchema):
    archive_date: date
    timezone: str
    status: str
    item_count: int = 0
    articles_created: int = 0
    high_relevance_count: int = 0
    top_category: str | None = None
    top_heat_score: float | None = None


class ArchiveDetailRead(TimestampSchema):
    id: int
    archive_date: date
    timezone: str
    window_start: datetime
    window_end: datetime
    status: str
    error_message: str | None = None
    briefing: dict[str, Any] | None = None
    metrics: dict[str, Any] | None = None


class ArchiveListResponse(BaseSchema):
    success: bool = True
    data: list[ArchiveSummaryRead]
    total: int
    page: int
    page_size: int
    total_pages: int


class ArchiveDetailResponse(BaseSchema):
    success: bool = True
    data: ArchiveDetailRead


class CategoryHeatPointRead(BaseSchema):
    date: str
    heat_score: float
    articles: int = 0
    high_relevance: int = 0
    avg_relevance: float = 0
    category_label: str | None = None


class CategoryHeatTrendsRead(BaseSchema):
    timezone: str
    days: int
    start_date: str
    end_date: str
    categories: list[str] = Field(default_factory=list)
    points_by_category: dict[str, list[CategoryHeatPointRead]] = Field(default_factory=dict)


class CategoryHeatTrendsResponse(BaseSchema):
    success: bool = True
    data: CategoryHeatTrendsRead
