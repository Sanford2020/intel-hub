from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.config import settings
from app.modules.briefings.schemas import (
    BriefingFormat,
    DailyBriefingResponse,
)
from app.modules.briefings.service import BriefingService

router = APIRouter(prefix="/briefings", tags=["briefings"])


def get_briefing_service(session: AsyncSession = Depends(get_session)) -> BriefingService:
    return BriefingService(session)


@router.get("/daily", response_model=DailyBriefingResponse)
async def get_daily_briefing(
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(20, ge=1, le=50),
    min_relevance: float | None = Query(None, ge=0.0, le=10.0),
    lang: str | None = Query(None, max_length=32),
    format: BriefingFormat = Query(BriefingFormat.json, alias="format"),
    service: BriefingService = Depends(get_briefing_service),
) -> DailyBriefingResponse:
    effective_min_relevance = (
        min_relevance if min_relevance is not None else settings.briefing_min_relevance
    )
    include_markdown = format == BriefingFormat.markdown
    data = await service.build_daily(
        hours=hours,
        limit=limit,
        min_relevance=effective_min_relevance,
        lang=lang,
        include_markdown=include_markdown,
    )
    return DailyBriefingResponse(data=data)
