"""M4 integration tests: aihot, apify, n8n/telegram delivery helpers."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from app.modules.briefings.delivery.service import BriefingDeliveryService
from app.modules.briefings.delivery.webhook import build_n8n_payload
from app.modules.briefings.schemas import (
    BriefingItemRead,
    BriefingMetaRead,
    DailyBriefingRead,
)
from app.modules.ingest import pipeline as ingest_pipeline
from app.modules.ingest.aihot_parser import fetch_aihot_items
from app.modules.ingest.apify_parser import fetch_apify_items


def test_fetch_aihot_items_parses_list(monkeypatch) -> None:
    sample = [
        {
            "title": "GPT-5 rumor",
            "url": "https://example.com/1",
            "author": "x.com/user",
            "published_at": "2026-05-19T10:00:00Z",
        }
    ]

    class FakeResponse:
        def json(self):
            return sample

    monkeypatch.setattr(
        "app.modules.ingest.aihot_parser.fetch_url",
        lambda *_args, **_kwargs: FakeResponse(),
    )

    items = fetch_aihot_items("selected")
    assert len(items) == 1
    assert items[0].title == "GPT-5 rumor"
    assert items[0].url == "https://example.com/1"


def test_fetch_apify_items_requires_token(monkeypatch) -> None:
    monkeypatch.setattr("app.modules.ingest.apify_parser.settings.apify_token", "")
    with pytest.raises(ValueError, match="APIFY_TOKEN"):
        fetch_apify_items("@testuser")


def test_fetch_apify_items_maps_tweets(monkeypatch) -> None:
    monkeypatch.setattr("app.modules.ingest.apify_parser.settings.apify_token", "tok")

    run_payload = {"data": {"defaultDatasetId": "ds1"}}
    dataset_rows = [
        {
            "text": "Hello world",
            "url": "https://x.com/u/status/1",
            "createdAt": "2026-05-19T08:00:00Z",
            "likeCount": 10,
        }
    ]

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def post(self, url, **kwargs):
            resp = MagicMock()
            resp.json.return_value = run_payload
            resp.raise_for_status = MagicMock()
            return resp

        def get(self, url, **kwargs):
            resp = MagicMock()
            resp.json.return_value = dataset_rows
            resp.raise_for_status = MagicMock()
            return resp

    monkeypatch.setattr("app.modules.ingest.apify_parser.httpx.Client", FakeClient)

    items = fetch_apify_items("@testuser")
    assert len(items) == 1
    assert "Hello world" in items[0].title
    assert items[0].url == "https://x.com/u/status/1"


def test_ingest_aihot_source_creates_articles(monkeypatch) -> None:
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import sessionmaker

    from app.db.base import Base
    from app.models import Article, Source
    from app.modules.ingest.rss_parser import RssItem

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    source = Source(
        name="AI HOT API",
        slug="aihot-test",
        category="social",
        source_type="aihot",
        url="selected",
        enabled=True,
        tier=0,
        fetch_interval_minutes=15,
    )
    session.add(source)
    session.commit()

    monkeypatch.setattr(
        ingest_pipeline,
        "fetch_aihot_items",
        lambda _url: [
            RssItem(
                title="Item",
                url="https://aihot.virxact.com/item/1",
                content="body",
                published_at=datetime.now(UTC),
            )
        ],
    )

    result = ingest_pipeline.ingest_source(session, source.id)
    session.commit()
    assert result.status == "success"
    assert result.items_created == 1
    assert session.scalars(select(Article)).all()
    session.close()


def test_build_n8n_payload_contains_event() -> None:
    meta = BriefingMetaRead(
        generated_at=datetime.now(UTC),
        window_hours=24,
        window_start=datetime.now(UTC),
        window_end=datetime.now(UTC),
        item_count=1,
        limit=20,
        min_relevance=6.0,
        ai_mode="mock",
    )
    items = [
        BriefingItemRead(
            rank=1,
            article_id=1,
            source_id=1,
            source_name="Test",
            title="Headline",
            url="https://example.com",
            summary="Summary",
            relevance_score=8.5,
        )
    ]
    briefing = DailyBriefingRead(meta=meta, overview="Overview", items=items)
    payload = build_n8n_payload(briefing, top_n=1, base_url="http://localhost:3000")
    assert payload["event"] == "intel_hub.daily_briefing"
    assert payload["top_articles"][0]["title"] == "Headline"


def test_n8n_delivery_skipped_when_url_empty() -> None:
    meta = BriefingMetaRead(
        generated_at=datetime.now(UTC),
        window_hours=24,
        window_start=datetime.now(UTC),
        window_end=datetime.now(UTC),
        item_count=0,
        limit=20,
        min_relevance=6.0,
        ai_mode="mock",
    )
    briefing = DailyBriefingRead(meta=meta, overview="Empty", items=[])

    session = MagicMock()
    with patch("app.modules.briefings.delivery.service.settings") as mock_settings:
        mock_settings.briefing_push_enabled = True
        mock_settings.feishu_webhook_url = ""
        mock_settings.n8n_webhook_url = ""
        mock_settings.telegram_bot_token = ""
        mock_settings.telegram_chat_id = ""
        mock_settings.feishu_push_top_n = 5
        mock_settings.briefing_public_base_url = ""
        svc = BriefingDeliveryService(session)
        results = svc.deliver_all(briefing)

    channels = {r.channel for r in results}
    assert "n8n" in channels
    n8n = next(r for r in results if r.channel == "n8n")
    assert n8n.status == "skipped"
