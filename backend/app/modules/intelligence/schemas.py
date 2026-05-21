from typing import Any

from pydantic import Field

from app.schemas.base import BaseSchema, TimestampSchema


class EntityRead(BaseSchema):
    name: str
    type: str | None = None


class IntelligenceReportRead(TimestampSchema):
    id: int
    article_id: int
    summary: str
    tags: list[str] = Field(default_factory=list)
    entities: list[EntityRead] = Field(default_factory=list)
    relevance_score: float
    sentiment: str | None = None
    language: str | None = None
    model: str | None = None
    prompt_template: str | None = None
    raw_json: dict[str, Any] | None = None


class AnalyzeArticleResponse(BaseSchema):
    success: bool = True
    data: IntelligenceReportRead
