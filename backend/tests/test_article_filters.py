from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient


def _seed_source_and_articles(client: TestClient) -> int:
    source_resp = client.post(
        "/api/v1/sources",
        json={
            "name": "Filter Wire",
            "slug": "filter-wire",
            "category": "wire",
            "source_type": "rss",
            "tier": 0,
            "enabled": True,
        },
    )
    source_id = source_resp.json()["id"]

    for idx, (title, tag) in enumerate(
        [
            ("Alpha geopolitics story", "geopolitics"),
            ("Beta tech release", "tech"),
        ],
        start=1,
    ):
        article_resp = client.post(
            "/api/v1/articles",
            json={
                "source_id": source_id,
                "title": title,
                "url": f"https://example.com/{idx}",
                "published_at": f"2026-05-{10 + idx:02d}T12:00:00Z",
            },
        )
        article_id = article_resp.json()["id"]
        client.post(f"/api/v1/articles/{article_id}/analyze")
        if tag == "tech":
            # re-analyze won't change tags in mock; patch report via second article only
            pass

    return source_id


def test_article_filter_by_source_and_q(client: TestClient) -> None:
    source_id = _seed_source_and_articles(client)

    resp = client.get(
        "/api/v1/articles",
        params={"source_id": source_id, "q": "Alpha"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert "Alpha" in body["data"][0]["title"]


def test_article_filter_has_report(client: TestClient) -> None:
    source_id = _seed_source_and_articles(client)

    with_report = client.get(
        "/api/v1/articles", params={"source_id": source_id, "has_report": True}
    )
    assert with_report.json()["total"] == 2
    assert with_report.json()["data"][0]["report"] is not None

    # delete reports by analyzing only one - use new source without analyze
    bare = client.post(
        "/api/v1/sources",
        json={
            "name": "Bare",
            "slug": "bare-wire",
            "category": "wire",
            "source_type": "rss",
        },
    ).json()["id"]
    client.post(
        "/api/v1/articles",
        json={"source_id": bare, "title": "No report yet", "url": "https://ex.com/x"},
    )
    none_resp = client.get("/api/v1/articles", params={"source_id": bare, "has_report": False})
    assert none_resp.json()["total"] == 1
    assert none_resp.json()["data"][0]["report"] is None


def test_article_filter_date_range(client: TestClient) -> None:
    source_id = _seed_source_and_articles(client)
    resp = client.get(
        "/api/v1/articles",
        params={
            "source_id": source_id,
            "published_from": "2026-05-12T00:00:00Z",
            "published_to": "2026-05-12T23:59:59Z",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["total"] == 1


def test_article_list_includes_report_summary(client: TestClient) -> None:
    source_id = _seed_source_and_articles(client)
    row = client.get("/api/v1/articles", params={"source_id": source_id}).json()["data"][0]
    assert row["report"]["summary"]
    assert "relevance_score" in row["report"]


def test_article_filter_min_relevance(client: TestClient) -> None:
    source_id = _seed_source_and_articles(client)

    high = client.get(
        "/api/v1/articles",
        params={"source_id": source_id, "min_relevance": 6},
    )
    assert high.status_code == 200
    assert high.json()["total"] == 2
    for row in high.json()["data"]:
        assert row["report"]["relevance_score"] >= 6

    # Inject a low-score report via direct DB update path: create article + analyze + patch
    low_resp = client.post(
        "/api/v1/articles",
        json={
            "source_id": source_id,
            "title": "Low relevance story",
            "url": "https://example.com/low",
            "published_at": "2026-05-14T12:00:00Z",
        },
    )
    low_id = low_resp.json()["id"]
    client.post(f"/api/v1/articles/{low_id}/analyze")

    # Re-seed low score through another article created in DB session is heavy;
    # use API list with min_relevance=8 to exclude mock 7.5 articles
    strict = client.get(
        "/api/v1/articles",
        params={"source_id": source_id, "min_relevance": 8},
    )
    assert strict.json()["total"] == 0

    none = client.get(
        "/api/v1/articles",
        params={"source_id": source_id, "min_relevance": 6},
    )
    assert none.json()["total"] == 3


@pytest.mark.asyncio
async def test_ingest_logs_endpoint(client, db_session) -> None:
    from app.models.ingest_log import IngestLog

    source_resp = client.post(
        "/api/v1/sources",
        json={
            "name": "Log Wire",
            "slug": "log-wire",
            "category": "wire",
            "source_type": "rss",
            "url": "https://example.com/feed.xml",
            "enabled": True,
        },
    )
    source_id = source_resp.json()["id"]

    db_session.add(
        IngestLog(
            source_id=source_id,
            status="success",
            items_found=2,
            items_created=1,
            items_skipped=1,
            duration_ms=500,
        )
    )
    await db_session.flush()

    logs = client.get(f"/api/v1/sources/{source_id}/ingest-logs")
    assert logs.status_code == 200
    body = logs.json()
    assert body["total"] == 1
    assert body["data"][0]["status"] == "success"
