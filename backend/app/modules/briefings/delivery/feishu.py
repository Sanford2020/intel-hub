"""Feishu webhook: build interactive card and POST."""

from __future__ import annotations

import time
from dataclasses import dataclass

import httpx

from app.core.logging import get_logger
from app.modules.briefings.schemas import DailyBriefingRead

logger = get_logger(__name__)

OVERVIEW_MAX_LEN = 300
TIMEOUT_SECONDS = 15.0


def _feishu_body_ok(resp: httpx.Response) -> tuple[bool, str | None]:
    """Feishu often returns HTTP 200 with StatusCode/code != 0 on failure."""
    if resp.status_code >= 300:
        snippet = resp.text[:500]
        return False, f"HTTP {resp.status_code}: {snippet}"

    try:
        data = resp.json()
    except Exception:  # noqa: BLE001
        return True, None

    if not isinstance(data, dict):
        return True, None

    if "StatusCode" in data and data["StatusCode"] != 0:
        msg = data.get("StatusMessage") or data.get("msg") or resp.text[:500]
        return False, f"Feishu StatusCode={data['StatusCode']}: {msg}"

    if "code" in data and data["code"] != 0:
        msg = data.get("msg") or resp.text[:500]
        return False, f"Feishu code={data['code']}: {msg}"

    return True, None


@dataclass
class FeishuSendResult:
    ok: bool
    status_code: int | None = None
    detail: str | None = None
    error_message: str | None = None
    duration_ms: int = 0


def build_feishu_card(
    briefing: DailyBriefingRead,
    *,
    top_n: int = 5,
    base_url: str = "",
) -> dict:
    """Return a Feishu interactive card payload (msg_type=interactive)."""
    meta = briefing.meta
    date_str = meta.generated_at.strftime("%Y-%m-%d")
    overview = briefing.overview
    if len(overview) > OVERVIEW_MAX_LEN:
        overview = overview[: OVERVIEW_MAX_LEN - 1] + "…"

    elements: list[dict] = [
        {
            "tag": "markdown",
            "content": overview,
        },
        {"tag": "hr"},
    ]

    top_items = briefing.items[:top_n]
    for item in top_items:
        line = (
            f"**#{item.rank}** {item.title}\n"
            f"来源：{item.source_name} · 相关度 {item.relevance_score:.1f}"
        )
        elements.append({"tag": "markdown", "content": line})

    if base_url:
        elements.append({"tag": "hr"})
        elements.append(
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {"tag": "plain_text", "content": "查看完整简报"},
                        "type": "primary",
                        "url": f"{base_url.rstrip('/')}/briefing",
                    }
                ],
            }
        )

    if meta.ai_mode == "mock":
        elements.append(
            {
                "tag": "note",
                "elements": [
                    {
                        "tag": "plain_text",
                        "content": "⚠ 当前为 Mock AI 分析模式，数据仅供参考",
                    }
                ],
            }
        )

    card = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"📋 Intel Hub 每日简报 — {date_str}",
                },
                "template": "blue",
            },
            "elements": elements,
        },
    }
    return card


def send_feishu_webhook(
    webhook_url: str,
    card_payload: dict,
) -> FeishuSendResult:
    """POST card_payload to Feishu webhook. Returns FeishuSendResult."""
    start = time.monotonic()
    try:
        resp = httpx.post(webhook_url, json=card_payload, timeout=TIMEOUT_SECONDS)
        duration_ms = int((time.monotonic() - start) * 1000)
        ok, error_message = _feishu_body_ok(resp)
        if ok:
            logger.info(
                "feishu_webhook.sent",
                status_code=resp.status_code,
                duration_ms=duration_ms,
            )
            return FeishuSendResult(
                ok=True,
                status_code=resp.status_code,
                detail=f"feishu {resp.status_code}",
                duration_ms=duration_ms,
            )

        body_snippet = error_message or resp.text[:500]
        logger.warning(
            "feishu_webhook.failed",
            status_code=resp.status_code,
            error=body_snippet,
            duration_ms=duration_ms,
        )
        return FeishuSendResult(
            ok=False,
            status_code=resp.status_code,
            error_message=body_snippet[:500],
            duration_ms=duration_ms,
        )
    except Exception as exc:  # noqa: BLE001
        duration_ms = int((time.monotonic() - start) * 1000)
        logger.error(
            "feishu_webhook.exception",
            error=str(exc),
            duration_ms=duration_ms,
        )
        return FeishuSendResult(
            ok=False,
            error_message=str(exc)[:500],
            duration_ms=duration_ms,
        )
