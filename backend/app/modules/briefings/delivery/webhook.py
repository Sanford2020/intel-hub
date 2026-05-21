"""Generic JSON webhook delivery (n8n, Zapier, etc.)."""

from __future__ import annotations

import time
from dataclasses import dataclass

import httpx

from app.core.logging import get_logger
from app.modules.briefings.schemas import DailyBriefingRead

logger = get_logger(__name__)

TIMEOUT_SECONDS = 15.0


@dataclass
class WebhookSendResult:
    ok: bool
    status_code: int | None = None
    detail: str | None = None
    error_message: str | None = None
    duration_ms: int = 0


def build_n8n_payload(
    briefing: DailyBriefingRead,
    *,
    top_n: int = 10,
    base_url: str = "",
) -> dict:
    """Compact JSON payload for n8n / generic automation webhooks."""
    items = briefing.items[:top_n]
    return {
        "event": "intel_hub.daily_briefing",
        "meta": briefing.meta.model_dump(mode="json"),
        "top_articles": [
            {
                "title": item.title,
                "url": item.url,
                "relevance_score": item.relevance_score,
                "summary": item.summary,
                "source_name": item.source_name,
            }
            for item in items
        ],
        "briefing_url": f"{base_url.rstrip('/')}/briefing" if base_url else None,
        "markdown_preview": (briefing.markdown or "")[:4000] if briefing.markdown else None,
    }


def send_json_webhook(webhook_url: str, payload: dict) -> WebhookSendResult:
    started = time.perf_counter()
    try:
        resp = httpx.post(webhook_url, json=payload, timeout=TIMEOUT_SECONDS)
        duration_ms = int((time.perf_counter() - started) * 1000)
        ok = resp.status_code < 300
        if ok:
            logger.info("n8n_webhook.sent", status_code=resp.status_code)
            return WebhookSendResult(
                ok=True,
                status_code=resp.status_code,
                detail=f"webhook {resp.status_code}",
                duration_ms=duration_ms,
            )
        snippet = resp.text[:500]
        logger.warning("n8n_webhook.failed", status_code=resp.status_code, body=snippet)
        return WebhookSendResult(
            ok=False,
            status_code=resp.status_code,
            detail=f"HTTP {resp.status_code}",
            error_message=snippet,
            duration_ms=duration_ms,
        )
    except Exception as exc:  # noqa: BLE001
        duration_ms = int((time.perf_counter() - started) * 1000)
        logger.exception("n8n_webhook.exception", error=str(exc))
        return WebhookSendResult(
            ok=False,
            error_message=str(exc),
            duration_ms=duration_ms,
        )
