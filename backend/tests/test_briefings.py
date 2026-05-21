from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article
from app.models.intelligence_report import IntelligenceReport
from app.models.source import Source
from app.modules.articles.hashing import article_content_hash
from app.modules.briefings.aggregator import briefing_window, fetch_daily_rows
from app.modules.briefings.formatter import assemble_daily_briefing, to_markdown


def _create_source(client: TestClient, slug: str) -> int:
    resp = client.post(
        "/api/v1/sources",
        json={
            "name": f"Source {slug}",
            "slug": slug,
            "category": "wire",
            "source_type": "rss",
            "tier": 0,
            "enabled": True,
        },
    )
    assert resp.status_code == 201
    return resp.json()["id"]


def _create_article(
    client: TestClient,
    *,
    source_id: int,
    title: str,
    url: str,
    published_at: str | None = None,
) -> int:
    payload: dict = {
        "source_id": source_id,
        "title": title,
        "url": url,
        "content": "Body",
        "language": "en",
    }
    if published_at:
        payload["published_at"] = published_at
    resp = client.post("/api/v1/articles", json=payload)
    assert resp.status_code == 201
    return resp.json()["id"]


def test_daily_briefing_empty(client: TestClient) -> None:
    resp = client.get("/api/v1/briefings/daily")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert data["items"] == []
    assert data["meta"]["item_count"] == 0
    assert "暂无" in data["overview"]


def test_daily_briefing_includes_analyzed_articles(client: TestClient) -> None:
    source_id = _create_source(client, "briefing-wire")
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    article_ids: list[int] = []
    for i in range(6):
        article_id = _create_article(
            client,
            source_id=source_id,
            title=f"Briefing headline {i}",
            url=f"https://example.com/briefing/{i}",
            published_at=now,
        )
        client.post(f"/api/v1/articles/{article_id}/analyze")
        article_ids.append(article_id)

    resp = client.get("/api/v1/briefings/daily", params={"limit": 20})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data["items"]) == 6
    assert data["meta"]["item_count"] == 6
    assert data["meta"]["ai_mode"] == "mock"
    ranks = [item["rank"] for item in data["items"]]
    assert ranks == list(range(1, 7))
    assert all(item["summary"] for item in data["items"])


def test_daily_briefing_markdown_format(client: TestClient) -> None:
    source_id = _create_source(client, "briefing-md")
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    article_id = _create_article(
        client,
        source_id=source_id,
        title="Markdown test headline",
        url="https://example.com/md/1",
        published_at=now,
    )
    client.post(f"/api/v1/articles/{article_id}/analyze")

    resp = client.get(
        "/api/v1/briefings/daily",
        params={"format": "markdown"},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["markdown"] is not None
    assert "# Intel Hub 每日简报" in data["markdown"]
    assert "Markdown test headline" in data["markdown"]


def test_daily_briefing_hours_validation(client: TestClient) -> None:
    assert client.get("/api/v1/briefings/daily", params={"hours": 0}).status_code == 422
    assert client.get("/api/v1/briefings/daily", params={"limit": 0}).status_code == 422


@pytest.mark.asyncio
async def test_aggregator_sorts_by_relevance(db_session: AsyncSession) -> None:
    source = Source(
        name="Agg Source",
        slug="agg-source",
        category="wire",
        source_type="rss",
        tier=0,
        enabled=True,
        fetch_interval_minutes=15,
    )
    db_session.add(source)
    await db_session.flush()

    now = datetime.now(UTC)
    scores = [9.0, 5.0, 7.5]
    for idx, score in enumerate(scores):
        article = Article(
            source_id=source.id,
            title=f"Article {idx}",
            url=f"https://example.com/a/{idx}",
            content_hash=article_content_hash(f"Article {idx}", f"https://example.com/a/{idx}"),
            published_at=now - timedelta(hours=1),
            language="en",
        )
        db_session.add(article)
        await db_session.flush()
        db_session.add(
            IntelligenceReport(
                article_id=article.id,
                summary=f"Summary {idx}",
                tags=["test"],
                relevance_score=score,
                model="test-model",
            )
        )
    await db_session.flush()

    window_start, window_end = briefing_window(hours=24, now=now)
    rows = await fetch_daily_rows(
        db_session,
        window_start=window_start,
        limit=10,
    )
    assert [row.report.relevance_score for row in rows] == [9.0, 7.5, 5.0]

    briefing = assemble_daily_briefing(
        rows,
        window_hours=24,
        window_start=window_start,
        window_end=window_end,
        limit=10,
        min_relevance=None,
    )
    assert briefing.items[0].title == "Article 0"
    md = to_markdown(briefing)
    assert "Article 0" in md


@pytest.mark.asyncio
async def test_aggregator_min_relevance_filter(db_session: AsyncSession) -> None:
    source = Source(
        name="Filter Source",
        slug="filter-source",
        category="wire",
        source_type="rss",
        tier=0,
        enabled=True,
        fetch_interval_minutes=15,
    )
    db_session.add(source)
    await db_session.flush()

    now = datetime.now(UTC)
    for idx, score in enumerate([8.0, 4.0]):
        article = Article(
            source_id=source.id,
            title=f"Filter article {idx}",
            url=f"https://example.com/f/{idx}",
            content_hash=article_content_hash(
                f"Filter article {idx}", f"https://example.com/f/{idx}"
            ),
            published_at=now - timedelta(hours=2),
        )
        db_session.add(article)
        await db_session.flush()
        db_session.add(
            IntelligenceReport(
                article_id=article.id,
                summary="s",
                tags=[],
                relevance_score=score,
            )
        )
    await db_session.flush()

    window_start, _ = briefing_window(hours=24, now=now)
    rows = await fetch_daily_rows(
        db_session,
        window_start=window_start,
        limit=10,
        min_relevance=6.0,
    )
    assert len(rows) == 1
    assert rows[0].report.relevance_score == 8.0


@pytest.mark.asyncio
async def test_daily_briefing_default_min_relevance(
    client: TestClient, db_session: AsyncSession
) -> None:
    from datetime import UTC, datetime, timedelta

    from app.models.article import Article
    from app.models.intelligence_report import IntelligenceReport
    from app.models.source import Source
    from app.modules.articles.hashing import article_content_hash

    source = Source(
        name="Brief Default",
        slug="brief-default",
        category="wire",
        source_type="rss",
        tier=0,
        enabled=True,
        fetch_interval_minutes=15,
    )
    db_session.add(source)
    await db_session.flush()
    now = datetime.now(UTC)
    for idx, score in enumerate([8.0, 4.0]):
        article = Article(
            source_id=source.id,
            title=f"Score {score}",
            url=f"https://example.com/s/{idx}",
            content_hash=article_content_hash(f"Score {score}", f"https://example.com/s/{idx}"),
            published_at=now - timedelta(hours=1),
        )
        db_session.add(article)
        await db_session.flush()
        db_session.add(
            IntelligenceReport(
                article_id=article.id,
                summary="s",
                tags=["test"],
                relevance_score=score,
                model="test",
            )
        )
    await db_session.flush()

    resp = client.get("/api/v1/briefings/daily", params={"hours": 24})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["meta"]["min_relevance"] == 6.0
    assert len(data["items"]) == 1
    assert data["items"][0]["relevance_score"] == 8.0
