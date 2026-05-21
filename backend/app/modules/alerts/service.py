from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload

from app.core.errors import NotFoundError
from app.models.alert_event import AlertEvent
from app.models.alert_rule import AlertRule
from app.models.article import Article
from app.models.intelligence_report import IntelligenceReport
from app.modules.alerts.matcher import match_keywords
from app.modules.alerts.notifier import send_alert_notification
from app.modules.alerts.schemas import (
    AlertEventRead,
    AlertRuleCreate,
    AlertRuleUpdate,
)


@dataclass
class EvaluateResult:
    article_id: int
    events_created: int
    events: list[AlertEvent]


def _event_to_read(event: AlertEvent) -> AlertEventRead:
    return AlertEventRead(
        id=event.id,
        rule_id=event.rule_id,
        article_id=event.article_id,
        matched_keywords=event.matched_keywords,
        notification_status=event.notification_status,
        notification_detail=event.notification_detail,
        created_at=event.created_at,
        updated_at=event.updated_at,
        article_title=event.article.title if event.article else None,
        rule_name=event.rule.name if event.rule else None,
    )


def evaluate_alerts_for_article_sync(session: Session, article_id: int) -> EvaluateResult:
    article = session.get(Article, article_id)
    if not article:
        raise NotFoundError(message=f"Article {article_id} not found")

    report = session.scalar(
        select(IntelligenceReport).where(IntelligenceReport.article_id == article_id)
    )
    rules = session.scalars(select(AlertRule).where(AlertRule.enabled.is_(True))).all()

    created_events: list[AlertEvent] = []
    for rule in rules:
        matched = match_keywords(article, report, rule)
        if not matched:
            continue

        existing = session.scalar(
            select(AlertEvent.id).where(
                AlertEvent.rule_id == rule.id,
                AlertEvent.article_id == article_id,
            )
        )
        if existing:
            continue

        event = AlertEvent(
            rule_id=rule.id,
            article_id=article_id,
            matched_keywords=matched,
            notification_status="pending",
        )
        session.add(event)
        session.flush()

        status, detail = send_alert_notification(rule, event, article)
        event.notification_status = status
        event.notification_detail = detail
        session.flush()
        created_events.append(event)

    return EvaluateResult(
        article_id=article_id,
        events_created=len(created_events),
        events=created_events,
    )


class AlertService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_rule(self, payload: AlertRuleCreate) -> AlertRule:
        rule = AlertRule(**payload.model_dump())
        self.session.add(rule)
        await self.session.flush()
        await self.session.refresh(rule)
        return rule

    async def get_rule(self, rule_id: int) -> AlertRule:
        rule = await self.session.get(AlertRule, rule_id)
        if not rule:
            raise NotFoundError(message=f"Alert rule {rule_id} not found")
        return rule

    async def list_rules(
        self, *, page: int = 1, page_size: int = 20, enabled: bool | None = None
    ) -> tuple[list[AlertRule], int]:
        query = select(AlertRule)
        if enabled is not None:
            query = query.where(AlertRule.enabled.is_(enabled))

        total = int(
            await self.session.scalar(select(func.count()).select_from(query.subquery()))
            or 0
        )
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)
        offset = (page - 1) * page_size
        rows = await self.session.scalars(
            query.order_by(AlertRule.id.desc()).offset(offset).limit(page_size)
        )
        return list(rows.all()), total

    async def update_rule(self, rule_id: int, payload: AlertRuleUpdate) -> AlertRule:
        rule = await self.get_rule(rule_id)
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(rule, key, value)
        await self.session.flush()
        await self.session.refresh(rule)
        return rule

    async def delete_rule(self, rule_id: int) -> None:
        rule = await self.get_rule(rule_id)
        await self.session.delete(rule)

    async def list_events(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        rule_id: int | None = None,
    ) -> tuple[list[AlertEvent], int]:
        query = select(AlertEvent).options(
            selectinload(AlertEvent.article),
            selectinload(AlertEvent.rule),
        )
        if rule_id is not None:
            query = query.where(AlertEvent.rule_id == rule_id)

        total = int(
            await self.session.scalar(select(func.count()).select_from(query.subquery()))
            or 0
        )
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)
        offset = (page - 1) * page_size
        rows = await self.session.scalars(
            query.order_by(AlertEvent.id.desc()).offset(offset).limit(page_size)
        )
        return list(rows.unique().all()), total

    async def evaluate_article(self, article_id: int) -> EvaluateResult:
        article = await self.session.get(Article, article_id)
        if not article:
            raise NotFoundError(message=f"Article {article_id} not found")

        report = await self.session.scalar(
            select(IntelligenceReport).where(
                IntelligenceReport.article_id == article_id
            )
        )
        rules = await self.session.scalars(
            select(AlertRule).where(AlertRule.enabled.is_(True))
        )

        created_events: list[AlertEvent] = []
        for rule in rules.all():
            matched = match_keywords(article, report, rule)
            if not matched:
                continue

            existing = await self.session.scalar(
                select(AlertEvent.id).where(
                    AlertEvent.rule_id == rule.id,
                    AlertEvent.article_id == article_id,
                )
            )
            if existing:
                continue

            event = AlertEvent(
                rule_id=rule.id,
                article_id=article_id,
                matched_keywords=matched,
                notification_status="pending",
            )
            self.session.add(event)
            await self.session.flush()

            status, detail = send_alert_notification(rule, event, article)
            event.notification_status = status
            event.notification_detail = detail
            event.article = article
            event.rule = rule
            await self.session.flush()
            created_events.append(event)

        return EvaluateResult(
            article_id=article_id,
            events_created=len(created_events),
            events=created_events,
        )


def events_to_read(events: list[AlertEvent]) -> list[AlertEventRead]:
    return [_event_to_read(e) for e in events]
