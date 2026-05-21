from typing import Any, Literal

from pydantic import Field, field_validator

from app.schemas.base import BaseSchema, TimestampSchema

MatchIn = Literal["title", "content", "tags", "all"]
AlertChannel = Literal["log", "webhook", "email_stub"]


class AlertRuleBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=255)
    keywords: list[str] = Field(..., min_length=1)
    enabled: bool = True
    match_in: MatchIn = "all"
    channel: AlertChannel = "log"
    channel_config: dict[str, Any] | None = None

    @field_validator("keywords")
    @classmethod
    def normalize_keywords(cls, value: list[str]) -> list[str]:
        cleaned = [k.strip() for k in value if k and k.strip()]
        if not cleaned:
            raise ValueError("At least one non-empty keyword required")
        return cleaned


class AlertRuleCreate(AlertRuleBase):
    pass


class AlertRuleUpdate(BaseSchema):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    keywords: list[str] | None = None
    enabled: bool | None = None
    match_in: MatchIn | None = None
    channel: AlertChannel | None = None
    channel_config: dict[str, Any] | None = None


class AlertRuleRead(AlertRuleBase, TimestampSchema):
    id: int


class AlertRuleListResponse(BaseSchema):
    success: bool = True
    data: list[AlertRuleRead]
    total: int
    page: int
    page_size: int
    total_pages: int


class AlertEventRead(TimestampSchema):
    id: int
    rule_id: int
    article_id: int
    matched_keywords: list[str]
    notification_status: str
    notification_detail: str | None = None
    article_title: str | None = None
    rule_name: str | None = None


class AlertEventListResponse(BaseSchema):
    success: bool = True
    data: list[AlertEventRead]
    total: int
    page: int
    page_size: int
    total_pages: int


class EvaluateAlertsResponse(BaseSchema):
    success: bool = True
    article_id: int
    events_created: int
    events: list[AlertEventRead]
