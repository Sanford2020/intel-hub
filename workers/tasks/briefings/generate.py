"""Daily briefing generation Celery tasks."""

from __future__ import annotations

from dataclasses import asdict

from app.config import settings
from app.core.logging import get_logger
from app.db.sync_session import get_sync_session
from app.modules.briefings.delivery.service import BriefingDeliveryService
from app.modules.briefings.service import build_daily_briefing_sync
from workers.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(name="workers.tasks.briefings.generate.generate_daily_briefing")
def generate_daily_briefing(
    hours: int = 24,
    limit: int = 20,
    min_relevance: float | None = None,
) -> dict:
    effective_min_relevance = (
        min_relevance if min_relevance is not None else settings.briefing_min_relevance
    )
    logger.info(
        "generate_daily_briefing.start",
        hours=hours,
        limit=limit,
        min_relevance=effective_min_relevance,
    )
    with get_sync_session() as session:
        briefing = build_daily_briefing_sync(
            session,
            hours=hours,
            limit=limit,
            min_relevance=effective_min_relevance,
            include_markdown=True,
        )

        delivery_svc = BriefingDeliveryService(session)
        delivery_result = delivery_svc.deliver(briefing)

    payload = briefing.model_dump(mode="json")
    delivery_dict = asdict(delivery_result)

    logger.info(
        "generate_daily_briefing.done",
        item_count=briefing.meta.item_count,
        ai_mode=briefing.meta.ai_mode,
        delivery_status=delivery_result.status,
    )
    return {
        "briefing": payload,
        "delivery": delivery_dict,
    }
