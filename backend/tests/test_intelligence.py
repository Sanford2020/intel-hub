import json

from fastapi.testclient import TestClient


def _create_source_and_article(client: TestClient) -> tuple[int, int]:
    source_resp = client.post(
        "/api/v1/sources",
        json={
            "name": "Test Wire",
            "slug": "test-wire-intel",
            "category": "wire",
            "source_type": "rss",
            "url": "https://example.com/feed",
            "tier": 0,
            "enabled": True,
        },
    )
    assert source_resp.status_code == 201
    source_id = source_resp.json()["id"]

    article_resp = client.post(
        "/api/v1/articles",
        json={
            "source_id": source_id,
            "title": "Border tensions rise in region X",
            "url": "https://example.com/news/1",
            "content": "Officials confirmed new diplomatic talks amid rising tensions.",
            "language": "en",
        },
    )
    assert article_resp.status_code == 201
    return source_id, article_resp.json()["id"]


def test_analyze_article_creates_report(client: TestClient) -> None:
    _, article_id = _create_source_and_article(client)

    resp = client.post(f"/api/v1/articles/{article_id}/analyze")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert data["article_id"] == article_id
    assert "Mock intelligence" in data["summary"]
    assert "mock" in data["tags"]
    assert data["relevance_score"] == 7.5
    assert data["entities"][0]["name"] == "Example Org"
    assert data["model"] == "mock"


def test_get_article_report(client: TestClient) -> None:
    _, article_id = _create_source_and_article(client)

    missing = client.get(f"/api/v1/articles/{article_id}/report")
    assert missing.status_code == 404

    client.post(f"/api/v1/articles/{article_id}/analyze")
    report = client.get(f"/api/v1/articles/{article_id}/report")
    assert report.status_code == 200
    assert report.json()["data"]["article_id"] == article_id


def test_reanalyze_updates_existing_report(client: TestClient) -> None:
    _, article_id = _create_source_and_article(client)

    first = client.post(f"/api/v1/articles/{article_id}/analyze").json()["data"]
    report_id = first["id"]

    second = client.post(f"/api/v1/articles/{article_id}/analyze").json()["data"]
    assert second["id"] == report_id
    assert second["summary"] == first["summary"]


def test_analyze_article_not_found(client: TestClient) -> None:
    resp = client.post("/api/v1/articles/99999/analyze")
    assert resp.status_code == 404


def test_parse_analysis_content_normalizes_payload() -> None:
    from app.modules.intelligence.analyzer import parse_analysis_content

    raw = json.dumps(
        {
            "summary": "  Brief summary.  ",
            "tags": "geopolitics",
            "entities": [{"name": "NATO", "type": "org"}, "EU"],
            "relevance_score": 1.5,
        }
    )
    parsed = parse_analysis_content(raw)
    assert parsed["summary"] == "Brief summary."
    assert parsed["tags"] == ["geopolitics"]
    assert parsed["entities"][0]["name"] == "NATO"
    assert parsed["entities"][1]["name"] == "EU"
    assert parsed["relevance_score"] == 1.5


def test_normalize_relevance_score_legacy_and_new_scale() -> None:
    from app.modules.intelligence.analyzer import normalize_relevance_score

    assert normalize_relevance_score(0.75) == 7.5
    assert normalize_relevance_score(8.5) == 8.5
    assert normalize_relevance_score(15) == 10.0
    assert normalize_relevance_score(0.6) == 6.0


def test_analyze_article_sync_worker_path(monkeypatch) -> None:
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import sessionmaker

    from app.db.base import Base
    from app.models import Article, IntelligenceReport, Source
    from app.modules.intelligence import analyzer as intel_analyzer

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    source = Source(
        name="Worker Test",
        slug="worker-test",
        category="wire",
        source_type="rss",
        url="https://example.com/feed",
        enabled=True,
        tier=0,
    )
    session.add(source)
    session.flush()
    article = Article(
        source_id=source.id,
        title="Worker headline",
        url="https://example.com/w/1",
        content="Worker body",
        content_hash="abc123worker",
    )
    session.add(article)
    session.commit()

    async def fake_call(_article, *, client=None, prompt_template=None):
        return (
            {
                "summary": "Worker analysis",
                "tags": ["worker"],
                "entities": [],
                "relevance_score": 0.6,
                "language": "en",
            },
            "test-model",
            {"content": "{}", "usage": {}},
        )

    monkeypatch.setattr(intel_analyzer, "call_intelligence_ai", fake_call)

    result = intel_analyzer.analyze_article_sync(session, article.id)
    session.commit()

    assert result.summary == "Worker analysis"
    assert result.relevance_score == 6.0
    assert result.model == "test-model"
    reports = session.scalars(select(IntelligenceReport)).all()
    assert len(reports) == 1
    assert reports[0].tags == ["worker"]

    session.close()
