import math

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.models.user import User
from app.modules.auth.dependencies import require_admin, require_operator_write
from app.modules.alerts.schemas import (
    AlertEventListResponse,
    AlertEventRead,
    AlertRuleCreate,
    AlertRuleListResponse,
    AlertRuleRead,
    AlertRuleUpdate,
    EvaluateAlertsResponse,
)
from app.modules.alerts.service import AlertService, events_to_read

router = APIRouter(prefix="/alerts", tags=["alerts"])


def get_alert_service(session: AsyncSession = Depends(get_session)) -> AlertService:
    return AlertService(session)


@router.get("/rules", response_model=AlertRuleListResponse)
async def list_alert_rules(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    enabled: bool | None = None,
    service: AlertService = Depends(get_alert_service),
) -> AlertRuleListResponse:
    rows, total = await service.list_rules(page=page, page_size=page_size, enabled=enabled)
    total_pages = math.ceil(total / page_size) if total else 0
    return AlertRuleListResponse(
        data=[AlertRuleRead.model_validate(r) for r in rows],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post("/rules", response_model=AlertRuleRead, status_code=status.HTTP_201_CREATED)
async def create_alert_rule(
    payload: AlertRuleCreate,
    _user: User = Depends(require_operator_write),
    service: AlertService = Depends(get_alert_service),
) -> AlertRuleRead:
    rule = await service.create_rule(payload)
    return AlertRuleRead.model_validate(rule)


@router.get("/rules/{rule_id}", response_model=AlertRuleRead)
async def get_alert_rule(
    rule_id: int,
    service: AlertService = Depends(get_alert_service),
) -> AlertRuleRead:
    rule = await service.get_rule(rule_id)
    return AlertRuleRead.model_validate(rule)


@router.patch("/rules/{rule_id}", response_model=AlertRuleRead)
async def update_alert_rule(
    rule_id: int,
    payload: AlertRuleUpdate,
    _user: User = Depends(require_operator_write),
    service: AlertService = Depends(get_alert_service),
) -> AlertRuleRead:
    rule = await service.update_rule(rule_id, payload)
    return AlertRuleRead.model_validate(rule)


@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert_rule(
    rule_id: int,
    _user: User = Depends(require_operator_write),
    service: AlertService = Depends(get_alert_service),
) -> None:
    await service.delete_rule(rule_id)


@router.get("/events", response_model=AlertEventListResponse)
async def list_alert_events(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    rule_id: int | None = None,
    service: AlertService = Depends(get_alert_service),
) -> AlertEventListResponse:
    rows, total = await service.list_events(
        page=page, page_size=page_size, rule_id=rule_id
    )
    total_pages = math.ceil(total / page_size) if total else 0
    return AlertEventListResponse(
        data=events_to_read(rows),
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post("/evaluate/{article_id}", response_model=EvaluateAlertsResponse)
async def evaluate_alerts_for_article(
    article_id: int,
    _user: User = Depends(require_admin),
    service: AlertService = Depends(get_alert_service),
) -> EvaluateAlertsResponse:
    result = await service.evaluate_article(article_id)
    return EvaluateAlertsResponse(
        article_id=article_id,
        events_created=result.events_created,
        events=events_to_read(result.events),
    )
