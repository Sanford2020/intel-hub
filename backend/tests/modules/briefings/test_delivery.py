"""Tests for briefing delivery: feishu card builder, send, service, task integration."""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
import pytest

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from app.modules.briefings.delivery.feishu import (
    build_feishu_card,
    send_feishu_webhook,
)
from app.modules.briefings.delivery.service import (
    BriefingDeliveryService,
    DeliveryResult,
)
from app.modules.briefings.schemas import (
    BriefingItemRead,
    BriefingMetaRead,
    DailyBriefingRead,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_briefing(*, item_count: int = 3, ai_mode: str = "mock") -> DailyBriefingRead:
    now = datetime(2026, 5, 20, 6, 0, 0, tzinfo=UTC)
    items = [
        BriefingItemRead(
            rank=i + 1,
            article_id=100 + i,
            source_id=1,
            source_name=f"Source-{i}",
            title=f"Headline {i}",
            url=f"https://example.com/{i}",
            published_at=now,
            summary=f"Summary {i}",
            tags=["cyber", "ai"] if i == 0 else ["finance"],
            relevance_score=9.0 - i,
            sentiment="neutral",
            model="mock" if ai_mode == "mock" else "gpt-4o-mini",
        )
        for i in range(item_count)
    ]
    meta = BriefingMetaRead(
        generated_at=now,
        window_hours=24,
        window_start=datetime(2026, 5, 19, 6, 0, 0, tzinfo=UTC),
        window_end=now,
        item_count=item_count,
        limit=20,
        min_relevance=6.0,
        ai_mode=ai_mode,
    )
    return DailyBriefingRead(meta=meta, overview="过去24小时共3条高相关情报。", items=items)


def _configure_push_settings(mock_settings, **overrides) -> None:
    """MagicMock settings are truthy by default — set explicit push channel fields."""
    defaults = {
        "briefing_push_enabled": True,
        "feishu_webhook_url": "",
        "feishu_push_top_n": 5,
        "briefing_public_base_url": "http://localhost:3000",
        "n8n_webhook_url": "",
        "telegram_bot_token": "",
        "telegram_chat_id": "",
    }
    defaults.update(overrides)
    for key, value in defaults.items():
        setattr(mock_settings, key, value)


# ---------------------------------------------------------------------------
# Card builder
# ---------------------------------------------------------------------------

class TestBuildFeishuCard:
    def test_card_header_contains_date(self) -> None:
        briefing = _make_briefing()
        card = build_feishu_card(briefing, top_n=2, base_url="http://localhost:3000")
        header = card["card"]["header"]
        assert "2026-05-20" in header["title"]["content"]

    def test_card_limits_top_n(self) -> None:
        briefing = _make_briefing(item_count=5)
        card = build_feishu_card(briefing, top_n=2, base_url="")
        md_elements = [e for e in card["card"]["elements"] if e.get("tag") == "markdown"]
        # 1 overview + 2 items = 3 markdown elements
        assert len(md_elements) == 3

    def test_card_includes_button_when_base_url(self) -> None:
        briefing = _make_briefing()
        card = build_feishu_card(briefing, top_n=1, base_url="http://localhost:3000")
        action_elements = [e for e in card["card"]["elements"] if e.get("tag") == "action"]
        assert len(action_elements) == 1
        assert "/briefing" in action_elements[0]["actions"][0]["url"]

    def test_card_no_button_when_no_base_url(self) -> None:
        briefing = _make_briefing()
        card = build_feishu_card(briefing, top_n=1, base_url="")
        action_elements = [e for e in card["card"]["elements"] if e.get("tag") == "action"]
        assert len(action_elements) == 0

    def test_card_mock_footnote(self) -> None:
        briefing = _make_briefing(ai_mode="mock")
        card = build_feishu_card(briefing, top_n=1, base_url="")
        note_elements = [e for e in card["card"]["elements"] if e.get("tag") == "note"]
        assert len(note_elements) == 1
        assert "Mock" in note_elements[0]["elements"][0]["content"]

    def test_card_no_mock_footnote_for_live(self) -> None:
        briefing = _make_briefing(ai_mode="live")
        card = build_feishu_card(briefing, top_n=1, base_url="")
        note_elements = [e for e in card["card"]["elements"] if e.get("tag") == "note"]
        assert len(note_elements) == 0


# ---------------------------------------------------------------------------
# send_feishu_webhook
# ---------------------------------------------------------------------------

class TestSendFeishuWebhook:
    def test_send_success(self) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = '{"StatusCode":0}'
        mock_resp.json.return_value = {"StatusCode": 0}
        with patch("app.modules.briefings.delivery.feishu.httpx.post", return_value=mock_resp):
            result = send_feishu_webhook("https://hook.example.com/xxx", {"msg_type": "interactive"})
        assert result.ok is True
        assert result.status_code == 200
        assert result.duration_ms >= 0

    def test_send_feishu_status_code_in_body(self) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = '{"StatusCode":19001,"StatusMessage":"param invalid"}'
        mock_resp.json.return_value = {"StatusCode": 19001, "StatusMessage": "param invalid"}
        with patch("app.modules.briefings.delivery.feishu.httpx.post", return_value=mock_resp):
            result = send_feishu_webhook("https://hook.example.com/xxx", {})
        assert result.ok is False
        assert result.status_code == 200
        assert "19001" in (result.error_message or "")

    def test_send_non_2xx(self) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 400
        mock_resp.text = '{"msg":"bad request"}'
        mock_resp.json.side_effect = ValueError("not json")
        with patch("app.modules.briefings.delivery.feishu.httpx.post", return_value=mock_resp):
            result = send_feishu_webhook("https://hook.example.com/xxx", {})
        assert result.ok is False
        assert result.status_code == 400
        assert result.error_message is not None

    def test_send_exception(self) -> None:
        with patch(
            "app.modules.briefings.delivery.feishu.httpx.post",
            side_effect=httpx.ConnectError("connection refused"),
        ):
            result = send_feishu_webhook("https://hook.example.com/xxx", {})
        assert result.ok is False
        assert result.status_code is None
        assert "connection refused" in (result.error_message or "")


# ---------------------------------------------------------------------------
# BriefingDeliveryService — skipped paths
# ---------------------------------------------------------------------------

class TestDeliveryServiceSkipped:
    def test_skip_when_push_disabled(self) -> None:
        session = MagicMock()
        briefing = _make_briefing()
        with patch("app.modules.briefings.delivery.service.settings") as mock_settings:
            _configure_push_settings(
                mock_settings,
                briefing_push_enabled=False,
                feishu_webhook_url="https://hook.example.com/xxx",
            )
            svc = BriefingDeliveryService(session)
            result = svc.deliver(briefing)
        assert result.status == "skipped"
        assert result.channel == "feishu"
        assert "ENABLED" in (result.detail or "")
        session.add.assert_called_once()
        session.flush.assert_called_once()

    def test_skip_when_no_webhook_url(self) -> None:
        session = MagicMock()
        briefing = _make_briefing()
        with patch("app.modules.briefings.delivery.service.settings") as mock_settings:
            _configure_push_settings(mock_settings, briefing_push_enabled=True, feishu_webhook_url="")
            svc = BriefingDeliveryService(session)
            result = svc.deliver(briefing)
        assert result.status == "skipped"
        assert "empty" in (result.detail or "").lower()
        assert session.add.call_count == 3


# ---------------------------------------------------------------------------
# BriefingDeliveryService — sent / failed paths
# ---------------------------------------------------------------------------

class TestDeliveryServiceSentFailed:
    def test_sent(self) -> None:
        session = MagicMock()
        briefing = _make_briefing()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = '{"StatusCode":0}'
        with (
            patch("app.modules.briefings.delivery.service.settings") as mock_settings,
            patch("app.modules.briefings.delivery.feishu.httpx.post", return_value=mock_resp),
        ):
            _configure_push_settings(
                mock_settings,
                feishu_webhook_url="https://hook.example.com/xxx",
            )
            svc = BriefingDeliveryService(session)
            result = svc.deliver(briefing)
        assert result.status == "sent"
        assert result.channel == "feishu"
        assert result.webhook_status_code == 200
        assert session.add.call_count == 3

    def test_failed(self) -> None:
        session = MagicMock()
        briefing = _make_briefing()
        with (
            patch("app.modules.briefings.delivery.service.settings") as mock_settings,
            patch(
                "app.modules.briefings.delivery.feishu.httpx.post",
                side_effect=httpx.ConnectError("refused"),
            ),
        ):
            _configure_push_settings(
                mock_settings,
                feishu_webhook_url="https://hook.example.com/xxx",
                briefing_public_base_url="",
            )
            svc = BriefingDeliveryService(session)
            result = svc.deliver(briefing)
        assert result.status == "failed"
        assert result.error_message is not None
        assert session.add.call_count == 3


# ---------------------------------------------------------------------------
# Task integration — generate_daily_briefing returns delivery field
# ---------------------------------------------------------------------------

class TestGenerateTaskDeliveryIntegration:
    def test_task_returns_delivery_field(self) -> None:
        """generate_daily_briefing result dict must contain 'delivery' key."""
        fake_briefing = _make_briefing()

        mock_session = MagicMock()
        mock_session.__enter__ = MagicMock(return_value=mock_session)
        mock_session.__exit__ = MagicMock(return_value=False)

        with (
            patch(
                "workers.tasks.briefings.generate.get_sync_session",
                return_value=mock_session,
            ),
            patch(
                "workers.tasks.briefings.generate.build_daily_briefing_sync",
                return_value=fake_briefing,
            ),
            patch(
                "workers.tasks.briefings.generate.BriefingDeliveryService"
            ) as MockSvc,
        ):
            mock_svc_inst = MagicMock()
            mock_svc_inst.deliver.return_value = DeliveryResult(
                channel="feishu", status="skipped", detail="test"
            )
            MockSvc.return_value = mock_svc_inst

            from workers.tasks.briefings.generate import generate_daily_briefing

            result = generate_daily_briefing.__wrapped__(hours=24, limit=20)

        assert "briefing" in result
        assert "delivery" in result
        assert result["delivery"]["channel"] == "feishu"
        assert result["delivery"]["status"] == "skipped"
