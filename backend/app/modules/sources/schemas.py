from datetime import datetime

from pydantic import Field, field_validator

from app.schemas.base import BaseSchema, TimestampSchema


class SourceBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=120)
    category: str = Field(default="other", max_length=64)
    category_label: str | None = Field(default=None, max_length=128)
    subcategory: str | None = Field(default=None, max_length=128)
    section: str | None = Field(default=None, max_length=128)
    source_type: str = Field(default="unknown", max_length=32)
    url: str | None = Field(default=None, max_length=2048)
    language: str | None = Field(default=None, max_length=32)
    region: str | None = Field(default=None, max_length=64)
    tier: int = Field(default=1, ge=0, le=2)
    enabled: bool = False
    fetch_interval_minutes: int = Field(default=30, ge=5, le=1440)
    api_key_env: str | None = Field(default=None, max_length=64)
    license_notes: str | None = None
    source_file: str | None = Field(default=None, max_length=128)


class SourceCreate(SourceBase):
    pass


class SourceUpdate(BaseSchema):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    category: str | None = Field(default=None, max_length=64)
    category_label: str | None = None
    subcategory: str | None = None
    section: str | None = None
    source_type: str | None = Field(default=None, max_length=32)
    url: str | None = Field(default=None, max_length=2048)
    language: str | None = None
    region: str | None = None
    tier: int | None = Field(default=None, ge=0, le=2)
    enabled: bool | None = None
    fetch_interval_minutes: int | None = Field(default=None, ge=5, le=1440)
    api_key_env: str | None = None
    license_notes: str | None = None
    source_file: str | None = None


class SourceRead(SourceBase, TimestampSchema):
    id: int
    last_ingested_at: datetime | None = None


class IngestResultRead(BaseSchema):
    source_id: int
    status: str
    items_found: int = 0
    items_created: int = 0
    items_skipped: int = 0
    created_article_ids: list[int] = Field(default_factory=list)
    error_message: str | None = None
    duration_ms: int | None = None
    task_id: str | None = None


class IngestLogRead(TimestampSchema):
    id: int
    source_id: int
    status: str
    items_found: int
    items_created: int
    items_skipped: int
    error_message: str | None = None
    duration_ms: int | None = None
    finished_at: datetime | None = None


class IngestLogListResponse(BaseSchema):
    success: bool = True
    data: list[IngestLogRead]
    total: int
    page: int
    page_size: int
    total_pages: int


class SourceSeedImport(BaseSchema):
    """Row shape from seeds/all-sources.json."""

    name: str
    slug: str
    category: str = "other"
    category_label: str | None = None
    subcategory: str | None = None
    section: str | None = None
    type: str = "unknown"
    url: str | None = None
    language: str | None = None
    region: str | None = None
    tier: int = 1
    enabled: bool = False
    api_key_env: str | None = None
    license_notes: str | None = None
    source_file: str | None = None

    @field_validator("tier", mode="before")
    @classmethod
    def coerce_tier(cls, value: int | str) -> int:
        return int(value)


class SourceBulkImportRequest(BaseSchema):
    sources: list[SourceSeedImport]
    skip_existing: bool = True


class SourceBulkImportResult(BaseSchema):
    created: int
    skipped: int
    updated: int


class SourceListResponse(BaseSchema):
    success: bool = True
    data: list[SourceRead]
    total: int
    page: int
    page_size: int
    total_pages: int
