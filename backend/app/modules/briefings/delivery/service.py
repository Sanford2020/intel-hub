"""BriefingDeliveryService — orchestrates delivery channels and logs results."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.config import settings
from app.core.logging import get_logger
from app.models.briefing_delivery_log import BriefingDeliveryLog
from app.modules.briefings.delivery.feishu import (
    build_feishu_card,
    send_feishu_webhook,
)
from app.modules.briefings.delivery.telegram import (
    build_telegram_text,
    send_telegram_message,
)
from app.modules.briefings.delivery.webhook import (
    build_n8n_payload,
    send_json_webhook,
)
from app.modules.briefings.schemas import DailyBriefingRead

logger = get_logger(__name__)


@dataclass
class DeliveryResult:
    channel: str
    status: str  # sent | failed | skipped
    detail: str | None = None
    error_message: str | None = None
    duration_ms: int = 0
    webhook_status_code: int | None = None
    log_id: int | None = None


class BriefingDeliveryService:
    """Deliver a DailyBriefingRead to configured channels and persist logs."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def deliver(self, briefing: DailyBriefingRead) -> DeliveryResult:
        """Deliver to all configured channels; return Feishu result when present."""
        results = self.deliver_all(briefing)
        if not results:
            return self._skip(briefing, "feishu", reason="BRIEFING_PUSH_ENABLED=false")
        for result in results:
            if result.channel == "feishu":
                return result
        for result in results:
            if result.status == "sent":
                return result
        return results[0]

    def deliver_all(self, briefing: DailyBriefingRead) -> list[DeliveryResult]:
        if not settings.briefing_push_enabled:
            return [self._skip(briefing, "feishu", reason="BRIEFING_PUSH_ENABLED=false")]

        return [
            self._deliver_feishu(briefing),
            self._deliver_n8n(briefing),
            self._deliver_telegram(briefing),
        ]

    def _deliver_feishu(self, briefing: DailyBriefingRead) -> DeliveryResult:
        channel = "feishu"
        webhook_url = settings.feishu_webhook_url
        if not webhook_url:
            return self._skip(briefing, channel, reason="FEISHU_WEBHOOK_URL is empty")

        card = build_feishu_card(
            briefing,
            top_n=settings.feishu_push_top_n,
            base_url=settings.briefing_public_base_url,
        )
        result = send_feishu_webhook(webhook_url, card)
        return self._result_from_webhook(channel, briefing, result)

    def _deliver_n8n(self, briefing: DailyBriefingRead) -> DeliveryResult:
        channel = "n8n"
        webhook_url = settings.n8n_webhook_url
        if not webhook_url:
            return self._skip(briefing, channel, reason="N8N_WEBHOOK_URL is empty")

        payload = build_n8n_payload(
            briefing,
            top_n=settings.feishu_push_top_n,
            base_url=settings.briefing_public_base_url,
        )
        result = send_json_webhook(webhook_url, payload)
        return self._result_from_webhook(channel, briefing, result)

    def _deliver_telegram(self, briefing: DailyBriefingRead) -> DeliveryResult:
        channel = "telegram"
        token = settings.telegram_bot_token.strip()
        chat_id = settings.telegram_chat_id.strip()
        if not token or not chat_id:
            return self._skip(
                briefing,
                channel,
                reason="TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is empty",
            )

        text = build_telegram_text(
            briefing,
            top_n=settings.feishu_push_top_n,
            base_url=settings.briefing_public_base_url,
        )
        result = send_telegram_message(token, chat_id, text)
        if result.ok:
            dr = DeliveryResult(
                channel=channel,
                status="sent",
                detail=result.detail,
                duration_ms=result.duration_ms,
                webhook_status_code=result.status_code,
            )
        else:
            dr = DeliveryResult(
                channel=channel,
                status="failed",
                detail=result.detail,
                error_message=result.error_message,
                duration_ms=result.duration_ms,
                webhook_status_code=result.status_code,
            )
        self._persist_log(briefing, dr)
        return dr

    def _result_from_webhook(self, channel: str, briefing: DailyBriefingRead, result) -> DeliveryResult:
        if result.ok:
            dr = DeliveryResult(
                channel=channel,
                status="sent",
                detail=result.detail,
                duration_ms=result.duration_ms,
                webhook_status_code=result.status_code,
            )
        else:
            dr = DeliveryResult(
                channel=channel,
                status="failed",
                detail=result.detail,
                error_message=result.error_message,
                duration_ms=result.duration_ms,
                webhook_status_code=result.status_code,
            )
        self._persist_log(briefing, dr)
        return dr

    def _skip(
        self,
        briefing: DailyBriefingRead,
        channel: str,
        *,
        reason: str,
    ) -> DeliveryResult:
        logger.info("briefing_delivery.skipped", channel=channel, reason=reason)
        dr = DeliveryResult(channel=channel, status="skipped", detail=reason)
        self._persist_log(briefing, dr)
        return dr

    def _persist_log(
        self,
        briefing: DailyBriefingRead,
        dr: DeliveryResult,
    ) -> None:
        log = BriefingDeliveryLog(
            channel=dr.channel,
            status=dr.status,
            detail=dr.detail,
            error_message=dr.error_message,
            duration_ms=dr.duration_ms,
            webhook_status_code=dr.webhook_status_code,
            item_count=briefing.meta.item_count,
            briefing_date=briefing.meta.generated_at.strftime("%Y-%m-%d"),
        )
        self.session.add(log)
        self.session.flush()
        dr.log_id = log.id
        logger.info(
            "briefing_delivery.logged",
            log_id=log.id,
            channel=dr.channel,
            status=dr.status,
        )
