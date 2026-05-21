from fastapi.testclient import TestClient


def test_create_and_list_sources(client: TestClient) -> None:
    payload = {
        "name": "Reuters World",
        "slug": "reuters-world",
        "category": "wire",
        "source_type": "rss",
        "url": "https://www.reutersagency.com/feed/",
        "tier": 0,
        "enabled": True,
        "fetch_interval_minutes": 15,
    }
    create_resp = client.post("/api/v1/sources", json=payload)
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert created["slug"] == "reuters-world"
    assert created["enabled"] is True

    list_resp = client.get("/api/v1/sources", params={"tier": 0, "enabled": True})
    assert list_resp.status_code == 200
    body = list_resp.json()
    assert body["total"] == 1
    assert body["data"][0]["slug"] == "reuters-world"


def test_duplicate_source_slug_conflict(client: TestClient) -> None:
    payload = {
        "name": "BBC World",
        "slug": "bbc-world",
        "category": "wire",
        "source_type": "rss",
    }
    assert client.post("/api/v1/sources", json=payload).status_code == 201
    dup = client.post("/api/v1/sources", json=payload)
    assert dup.status_code == 409


def test_bulk_import_sources(client: TestClient) -> None:
    payload = {
        "skip_existing": True,
        "sources": [
            {
                "name": "AP Top News",
                "slug": "ap-top-news",
                "category": "wire",
                "type": "rss",
                "url": "https://apnews.com/hub/ap-top-news",
                "tier": 0,
                "enabled": True,
            },
            {
                "name": "AP Top News",
                "slug": "ap-top-news",
                "category": "wire",
                "type": "rss",
                "tier": 0,
                "enabled": True,
            },
        ],
    }
    resp = client.post("/api/v1/sources/import", json=payload)
    assert resp.status_code == 200
    result = resp.json()
    assert result["created"] == 1
    assert result["skipped"] == 1


def test_create_and_dedupe_articles(client: TestClient) -> None:
    source_resp = client.post(
        "/api/v1/sources",
        json={
            "name": "Test Wire",
            "slug": "test-wire",
            "category": "wire",
            "source_type": "rss",
        },
    )
    source_id = source_resp.json()["id"]

    article_payload = {
        "source_id": source_id,
        "title": "Breaking: Sample headline",
        "url": "https://example.com/a/1",
        "content": "Body text",
    }
    first = client.post("/api/v1/articles", json=article_payload)
    assert first.status_code == 201

    duplicate = client.post("/api/v1/articles", json=article_payload)
    assert duplicate.status_code == 409

    listed = client.get("/api/v1/articles", params={"source_id": source_id})
    assert listed.status_code == 200
    assert listed.json()["total"] == 1
