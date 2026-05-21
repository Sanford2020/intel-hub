from datetime import datetime

from pydantic import Field

from app.schemas.base import BaseSchema, TimestampSchema


class ReportSummary(BaseSchema):
    summary: str
    tags: list[str] = Field(default_factory=list)
    relevance_score: float


class ArticleBase(BaseSchema):
    source_id: int
    title: str = Field(..., min_length=1, max_length=512)
    url: str | None = Field(default=None, max_length=2048)
    content: str | None = None
    published_at: datetime | None = None
    language: str | None = Field(default=None, max_length=32)


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(BaseSchema):
    title: str | None = Field(default=None, min_length=1, max_length=512)
    url: str | None = Field(default=None, max_length=2048)
    content: str | None = None
    published_at: datetime | None = None
    language: str | None = None


class ArticleRead(ArticleBase, TimestampSchema):
    id: int
    content_hash: str
    report: ReportSummary | None = None


class ArticleListResponse(BaseSchema):
    success: bool = True
    data: list[ArticleRead]
    total: int
    page: int
    page_size: int
    total_pages: int
