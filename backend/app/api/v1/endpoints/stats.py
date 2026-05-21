from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends

from app.api.deps import get_session
from app.models.alert_event import AlertEvent
from app.models.alert_rule import AlertRule
from app.models.article import Article
from app.models.intelligence_report import IntelligenceReport
from app.models.source import Source
from app.schemas.base import BaseSchema

router = APIRouter(prefix="/stats", tags=["stats"])


class OverviewStats(BaseSchema):
    sources_total: int
    sources_enabled: int
    articles_total: int
    reports_total: int
    alert_rules_total: int
    alert_rules_enabled: int
    alert_events_total: int


class OverviewResponse(BaseSchema):
    success: bool = True
    data: OverviewStats


@router.get("/overview", response_model=OverviewResponse)
async def get_overview_stats(
    session: AsyncSession = Depends(get_session),
) -> OverviewResponse:
    sources_total = int(await session.scalar(select(func.count()).select_from(Source)) or 0)
    sources_enabled = int(
        await session.scalar(
            select(func.count()).select_from(Source).where(Source.enabled.is_(True))
        )
        or 0
    )
    articles_total = int(await session.scalar(select(func.count()).select_from(Article)) or 0)
    reports_total = int(
        await session.scalar(select(func.count()).select_from(IntelligenceReport)) or 0
    )
    alert_rules_total = int(
        await session.scalar(select(func.count()).select_from(AlertRule)) or 0
    )
    alert_rules_enabled = int(
        await session.scalar(
            select(func.count()).select_from(AlertRule).where(AlertRule.enabled.is_(True))
        )
        or 0
    )
    alert_events_total = int(
        await session.scalar(select(func.count()).select_from(AlertEvent)) or 0
    )
    return OverviewResponse(
        data=OverviewStats(
            sources_total=sources_total,
            sources_enabled=sources_enabled,
            articles_total=articles_total,
            reports_total=reports_total,
            alert_rules_total=alert_rules_total,
            alert_rules_enabled=alert_rules_enabled,
            alert_events_total=alert_events_total,
        )
    )
