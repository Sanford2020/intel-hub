"""Alert notification delivery stubs."""

from __future__ import annotations

import httpx

from app.core.logging import get_logger
from app.models.alert_event import AlertEvent
from app.models.alert_rule import AlertRule
from app.models.article import Article

logger = get_logger(__name__)


def send_alert_notification(
    rule: AlertRule,
    event: AlertEvent,
    article: Article,
) -> tuple[str, str | None]:
    """Returns (status, detail). status: sent | failed | skipped"""
    payload: dict[str, Any] = {
        "rule_id": rule.id,
        "rule_name": rule.name,
        "article_id": article.id,
        "article_title": article.title,
        "article_url": article.url,
        "matched_keywords": event.matched_keywords,
    }

    if rule.channel == "log":
        logger.info("alert_fired", **payload)
        return "sent", "logged"

    if rule.channel == "email_stub":
        recipient = (rule.channel_config or {}).get("email", "ops@example.com")
        logger.info("alert_email_stub", recipient=recipient, **payload)
        return "sent", f"stub email to {recipient}"

    if rule.channel == "webhook":
        url = (rule.channel_config or {}).get("url")
        if not url:
            return "failed", "webhook url missing in channel_config"
        try:
            response = httpx.post(url, json=payload, timeout=10.0)
            response.raise_for_status()
            return "sent", f"webhook {response.status_code}"
        except Exception as exc:  # noqa: BLE001
            logger.warning("alert_webhook_failed", error=str(exc), url=url)
            return "failed", str(exc)[:500]

    return "skipped", f"unknown channel {rule.channel}"
