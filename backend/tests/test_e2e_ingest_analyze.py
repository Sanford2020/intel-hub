"""E2E: RSS ingest returns new article IDs; analyze persists report."""

from tests.fixtures.sample_rss import SAMPLE_RSS


def test_ingest_returns_created_article_ids(monkeypatch) -> None:
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import sessionmaker

    from app.db.base import Base
    from app.models import Article, Source
    from app.modules.ingest import pipeline as ingest_pipeline

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    source = Source(
        name="E2E RSS",
        slug="e2e-rss",
        category="wire",
        source_type="rss",
        url="https://example.com/feed.xml",
        enabled=True,
        tier=0,
    )
    session.add(source)
    session.commit()

    def fake_fetch(_url: str, *, timeout: float = 20.0):
        from app.modules.ingest.rss_parser import parse_rss_feed

        return parse_rss_feed(SAMPLE_RSS)

    monkeypatch.setattr(ingest_pipeline, "fetch_rss_items", fake_fetch)

    result = ingest_pipeline.ingest_rss_source(session, source.id)
    session.commit()

    assert result.status == "success"
    assert result.items_created == 2
    assert len(result.created_article_ids) == 2

    articles = session.scalars(select(Article)).all()
    assert len(articles) == 2
    session.close()


def test_ingest_then_analyze_persists_report(monkeypatch) -> None:
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import sessionmaker

    from app.db.base import Base
    from app.models import IntelligenceReport, Source
    from app.modules.ingest import pipeline as ingest_pipeline
    from app.modules.intelligence import analyzer as intel_analyzer

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    source = Source(
        name="E2E Analyze",
        slug="e2e-analyze",
        category="wire",
        source_type="rss",
        url="https://example.com/feed.xml",
        enabled=True,
        tier=0,
    )
    session.add(source)
    session.commit()

    def fake_fetch(_url: str, *, timeout: float = 20.0):
        from app.modules.ingest.rss_parser import parse_rss_feed

        return parse_rss_feed(SAMPLE_RSS)

    async def fake_call(_article, *, client=None, prompt_template=None):
        return (
            {
                "summary": "E2E analysis",
                "tags": ["e2e"],
                "entities": [],
                "relevance_score": 0.9,
            },
            "mock",
            {},
        )

    monkeypatch.setattr(ingest_pipeline, "fetch_rss_items", fake_fetch)
    monkeypatch.setattr(intel_analyzer, "call_intelligence_ai", fake_call)

    result = ingest_pipeline.ingest_rss_source(session, source.id)
    session.commit()
    assert result.created_article_ids

    for article_id in result.created_article_ids:
        intel_analyzer.analyze_article_sync(session, article_id)
    session.commit()

    reports = session.scalars(select(IntelligenceReport)).all()
    assert len(reports) == 2
    assert reports[0].summary == "E2E analysis"
    session.close()


def test_fetch_rss_queues_analyze(monkeypatch) -> None:
    from contextlib import contextmanager

    from app.modules.ingest import pipeline as ingest_pipeline
    from workers.tasks.ingest import fetch_rss as fetch_rss_mod
    import workers.tasks.analyze.summarize as summarize_mod

    queued: list[int] = []

    def fake_ingest(_session, sid: int):  # noqa: ANN001
        return ingest_pipeline.IngestResult(
            source_id=sid,
            status="success",
            items_created=2,
            created_article_ids=[42, 43],
        )

    @contextmanager
    def fake_session():
        yield None

    class DelayProxy:
        @staticmethod
        def delay(article_id: int) -> None:
            queued.append(article_id)

    monkeypatch.setattr(fetch_rss_mod, "ingest_source", fake_ingest)
    monkeypatch.setattr(fetch_rss_mod, "get_sync_session", fake_session)
    monkeypatch.setattr(summarize_mod, "analyze_article", DelayProxy())

    fetch_rss_mod.fetch_rss_for_source.run(1)
    assert queued == [42, 43]
