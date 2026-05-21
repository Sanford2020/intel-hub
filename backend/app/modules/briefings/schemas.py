from datetime import datetime
from enum import Enum

from pydantic import Field

from app.schemas.base import BaseSchema


class BriefingFormat(str, Enum):
    json = "json"
    markdown = "markdown"


class BriefingMetaRead(BaseSchema):
    generated_at: datetime
    window_hours: int
    window_start: datetime
    window_end: datetime
    item_count: int
    limit: int
    min_relevance: float | None = None
    ai_mode: str
    sort: str = "relevance_score_desc"


class BriefingItemRead(BaseSchema):
    rank: int
    article_id: int
    source_id: int
    source_name: str
    title: str
    url: str | None = None
    published_at: datetime | None = None
    summary: str
    tags: list[str] = Field(default_factory=list)
    relevance_score: float
    sentiment: str | None = None
    model: str | None = None


class DailyBriefingRead(BaseSchema):
    meta: BriefingMetaRead
    overview: str
    items: list[BriefingItemRead] = Field(default_factory=list)
    markdown: str | None = None
    html: str | None = None


class DailyBriefingResponse(BaseSchema):
    success: bool = True
    data: DailyBriefingRead
