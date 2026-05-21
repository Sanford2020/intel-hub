from fastapi.testclient import TestClient


def _create_article(client: TestClient) -> int:
    source_id = client.post(
        "/api/v1/sources",
        json={
            "name": "Alert Wire",
            "slug": "alert-wire",
            "category": "wire",
            "source_type": "rss",
        },
    ).json()["id"]
    return client.post(
        "/api/v1/articles",
        json={
            "source_id": source_id,
            "title": "China Taiwan geopolitics escalation",
            "content": "Regional tensions continue to rise.",
        },
    ).json()["id"]


def test_create_alert_rule_and_match(client: TestClient) -> None:
    rule_resp = client.post(
        "/api/v1/alerts/rules",
        json={
            "name": "Geopolitics watch",
            "keywords": ["geopolitics", "Taiwan"],
            "match_in": "all",
            "channel": "log",
        },
    )
    assert rule_resp.status_code == 201
    rule_id = rule_resp.json()["id"]

    article_id = _create_article(client)
    client.post(f"/api/v1/articles/{article_id}/analyze")

    events = client.get("/api/v1/alerts/events", params={"rule_id": rule_id})
    assert events.status_code == 200
    assert events.json()["total"] >= 1
    assert "Taiwan" in events.json()["data"][0]["matched_keywords"]

    eval_resp = client.post(f"/api/v1/alerts/evaluate/{article_id}")
    assert eval_resp.status_code == 200
    assert eval_resp.json()["events_created"] == 0


def test_alert_rule_crud(client: TestClient) -> None:
    created = client.post(
        "/api/v1/alerts/rules",
        json={"name": "Tech", "keywords": ["AI", "chip"], "enabled": True},
    ).json()

    updated = client.patch(
        f"/api/v1/alerts/rules/{created['id']}",
        json={"enabled": False},
    )
    assert updated.status_code == 200
    assert updated.json()["enabled"] is False

    listed = client.get("/api/v1/alerts/rules")
    assert listed.json()["total"] >= 1

    deleted = client.delete(f"/api/v1/alerts/rules/{created['id']}")
    assert deleted.status_code == 204


def test_matcher_unit() -> None:
    from app.models.alert_rule import AlertRule
    from app.models.article import Article
    from app.models.intelligence_report import IntelligenceReport
    from app.modules.alerts.matcher import match_keywords

    article = Article(
        source_id=1,
        title="OpenAI releases new model",
        content="AI chip demand rises",
        content_hash="x",
    )
    report = IntelligenceReport(
        article_id=1,
        summary="Technology breakthrough",
        tags=["tech", "AI"],
        entities=[],
        relevance_score=0.8,
    )
    rule = AlertRule(
        name="AI",
        keywords=["AI", "miss"],
        match_in="all",
        enabled=True,
        channel="log",
    )
    matched = match_keywords(article, report, rule)
    assert matched == ["AI"]


def test_overview_stats(client: TestClient) -> None:
    client.post(
        "/api/v1/alerts/rules",
        json={"name": "Stats rule", "keywords": ["test"]},
    )
    resp = client.get("/api/v1/stats/overview")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["alert_rules_total"] >= 1
    assert "articles_total" in data
