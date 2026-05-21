"""Telegram Bot API delivery for daily briefings."""

from __future__ import annotations

import time
from dataclasses import dataclass

import httpx

from app.core.logging import get_logger
from app.modules.briefings.schemas import DailyBriefingRead

logger = get_logger(__name__)

TIMEOUT_SECONDS = 15.0
MESSAGE_MAX = 4000


@dataclass
class TelegramSendResult:
    ok: bool
    status_code: int | None = None
    detail: str | None = None
    error_message: str | None = None
    duration_ms: int = 0


def build_telegram_text(
    briefing: DailyBriefingRead,
    *,
    top_n: int = 5,
    base_url: str = "",
) -> str:
    meta = briefing.meta
    lines = [
        f"📰 Intel Hub 每日简报 ({meta.generated_at.strftime('%Y-%m-%d')})",
        f"共 {meta.item_count} 条 · 阈值 ≥{meta.min_relevance}",
        "",
    ]
    for idx, item in enumerate(briefing.items[:top_n], start=1):
        score = item.relevance_score if item.relevance_score is not None else "?"
        lines.append(f"{idx}. [{score}] {item.title}")
        if item.url:
            lines.append(f"   {item.url}")
    if base_url:
        lines.extend(["", f"完整简报: {base_url.rstrip('/')}/briefing"])
    text = "\n".join(lines)
    if len(text) > MESSAGE_MAX:
        return text[: MESSAGE_MAX - 1] + "…"
    return text


def send_telegram_message(
    bot_token: str,
    chat_id: str,
    text: str,
) -> TelegramSendResult:
    started = time.perf_counter()
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        resp = httpx.post(
            url,
            json={"chat_id": chat_id, "text": text, "disable_web_page_preview": False},
            timeout=TIMEOUT_SECONDS,
        )
        duration_ms = int((time.perf_counter() - started) * 1000)
        data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
        ok = resp.status_code < 300 and isinstance(data, dict) and data.get("ok", False)
        if ok:
            logger.info("telegram.sent", chat_id=chat_id)
            return TelegramSendResult(
                ok=True,
                status_code=resp.status_code,
                detail="telegram sent",
                duration_ms=duration_ms,
            )
        err = data.get("description") if isinstance(data, dict) else resp.text[:500]
        logger.warning("telegram.failed", status_code=resp.status_code, error=err)
        return TelegramSendResult(
            ok=False,
            status_code=resp.status_code,
            detail=f"HTTP {resp.status_code}",
            error_message=str(err),
            duration_ms=duration_ms,
        )
    except Exception as exc:  # noqa: BLE001
        duration_ms = int((time.perf_counter() - started) * 1000)
        logger.exception("telegram.exception", error=str(exc))
        return TelegramSendResult(
            ok=False,
            error_message=str(exc),
            duration_ms=duration_ms,
        )
