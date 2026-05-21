"""Tests for daily archives and category heat metrics."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models import Article, DailyArchive, IntelligenceReport, Source
from app.modules.archives.metrics import archive_window_bounds, compute_heat_score
from app.modules.archives.service import create_or_update_daily_archive_sync


def test_compute_heat_score() -> None:
    assert compute_heat_score(articles=10, high_relevance=2, avg_relevance=5.0) == 21.0


def test_archive_window_uses_beijing_calendar_date() -> None:
    # 2026-05-20 18:00 UTC = 2026-05-21 02:00 Beijing
    now = datetime(2026, 5, 20, 18, 0, tzinfo=UTC)
    _, _, archive_date = archive_window_bounds(hours=24, timezone="Asia/Shanghai", now=now)
    assert archive_date == date(2026, 5, 21)


def test_create_daily_archive_with_category_heat() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    source = Source(
        name="OSINT",
        slug="osint-test",
        category="geopolitical",
        category_label="地缘/OSINT",
        source_type="rss",
        enabled=True,
        tier=0,
    )
    session.add(source)
    session.flush()

    now = datetime(2026, 5, 21, 10, 0, tzinfo=UTC)
    article = Article(
        source_id=source.id,
        title="Conflict update",
        url="https://example.com/1",
        content_hash="abc123",
        published_at=now,
    )
    session.add(article)
    session.flush()
    session.add(
        IntelligenceReport(
            article_id=article.id,
            summary="Summary",
            tags=["ukraine"],
            entities=[],
            relevance_score=8.0,
        )
    )
    session.commit()

    record = create_or_update_daily_archive_sync(
        session,
        archive_date=date(2026, 5, 21),
        now=now,
    )
    session.commit()

    assert record.status == "success"
    metrics = record.metrics_json or {}
    heat = metrics.get("category_heat") or []
    assert len(heat) >= 1
    assert heat[0]["category"] == "geopolitical"
    assert heat[0]["heat_score"] > 0
    assert record.briefing_json is not None
    assert record.timezone == "Asia/Shanghai"

    again = create_or_update_daily_archive_sync(
        session,
        archive_date=date(2026, 5, 21),
        now=now,
    )
    session.commit()
    count = session.scalar(select(DailyArchive))
    assert count is not None
    assert again.id == record.id
    session.close()


@pytest.mark.asyncio
async def test_category_heat_trends_api(client: TestClient, db_session) -> None:
    beijing_today = datetime.now(ZoneInfo("Asia/Shanghai")).date()
    archive_day = beijing_today - timedelta(days=1)
    db_session.add(
        DailyArchive(
            archive_date=archive_day,
            timezone="Asia/Shanghai",
            window_start=datetime(2026, 5, 19, 16, 0, tzinfo=UTC),
            window_end=datetime(2026, 5, 20, 16, 0, tzinfo=UTC),
            status="success",
            metrics_json={
                "category_heat": [
                    {
                        "category": "cyber",
                        "category_label": "网络安全",
                        "articles": 5,
                        "reports": 5,
                        "high_relevance": 2,
                        "avg_relevance": 6.5,
                        "heat_score": 17.5,
                    }
                ]
            },
        )
    )
    await db_session.flush()

    resp = client.get("/api/v1/archives/trends/category-heat?days=7")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert data["timezone"] == "Asia/Shanghai"
    assert "cyber" in data["points_by_category"]
    assert data["points_by_category"]["cyber"][0]["heat_score"] == 17.5


@pytest.mark.asyncio
async def test_list_and_get_archive_api(client: TestClient, db_session) -> None:
    db_session.add(
        DailyArchive(
            archive_date=date(2026, 5, 19),
            timezone="Asia/Shanghai",
            window_start=datetime(2026, 5, 18, 16, 0, tzinfo=UTC),
            window_end=datetime(2026, 5, 19, 16, 0, tzinfo=UTC),
            status="success",
            briefing_json={"overview": "test", "items": [], "meta": {"item_count": 0}},
            metrics_json={
                "category_heat": [{"category": "wire", "heat_score": 12.0, "articles": 10}],
                "briefing_meta": {"item_count": 3},
                "analysis": {"high_relevance_count": 2},
                "ingest": {"articles_created": 15},
            },
        )
    )
    await db_session.flush()

    listing = client.get("/api/v1/archives")
    assert listing.status_code == 200
    rows = listing.json()["data"]
    assert len(rows) == 1
    assert rows[0]["archive_date"] == "2026-05-19"
    assert rows[0]["top_category"] == "wire"

    detail = client.get("/api/v1/archives/2026-05-19")
    assert detail.status_code == 200
    assert detail.json()["data"]["briefing"]["overview"] == "test"

    missing = client.get("/api/v1/archives/2020-01-01")
    assert missing.status_code == 404
