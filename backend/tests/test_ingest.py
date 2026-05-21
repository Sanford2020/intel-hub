from app.modules.ingest.rss_parser import parse_rss_feed
from tests.fixtures.sample_rss import SAMPLE_RSS


def test_parse_rss_feed_extracts_items() -> None:
    items = parse_rss_feed(SAMPLE_RSS)
    assert len(items) == 2
    assert items[0].title == "First headline"
    assert items[0].url == "https://example.com/a/1"
    assert items[0].content == "Body one"
    assert items[0].published_at is not None


def test_ingest_pipeline_creates_articles_and_log(monkeypatch) -> None:
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import sessionmaker

    from app.db.base import Base
    from app.models import Article, IngestLog, Source
    from app.modules.ingest import pipeline as ingest_pipeline
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    source = Source(
        name="Test RSS",
        slug="test-rss",
        category="wire",
        source_type="rss",
        url="https://example.com/feed.xml",
        enabled=True,
        tier=0,
        fetch_interval_minutes=15,
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
    assert result.items_found == 2
    assert result.items_created == 2
    assert result.items_skipped == 0

    articles = session.scalars(select(Article)).all()
    assert len(articles) == 2
    logs = session.scalars(select(IngestLog)).all()
    assert len(logs) == 1
    assert logs[0].status == "success"

    # second run dedupes
    result2 = ingest_pipeline.ingest_rss_source(session, source.id)
    session.commit()
    assert result2.items_created == 0
    assert result2.items_skipped == 2

    session.close()


def test_ingest_skipped_source_writes_log() -> None:
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import sessionmaker

    from app.db.base import Base
    from app.models import IngestLog, Source
    from app.modules.ingest import pipeline as ingest_pipeline

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    source = Source(
        name="36氪",
        slug="36-china",
        category="china",
        source_type="unknown",
        url="",
        enabled=True,
        tier=0,
        fetch_interval_minutes=15,
    )
    session.add(source)
    session.commit()

    result = ingest_pipeline.ingest_rss_source(session, source.id)
    session.commit()

    assert result.status == "skipped"
    assert "未配置 URL / 账号" in (result.error_message or "")

    logs = session.scalars(select(IngestLog)).all()
    assert len(logs) == 1
    assert logs[0].status == "skipped"
    assert logs[0].error_message is not None

    session.close()


def test_source_is_due_respects_interval() -> None:
    from datetime import UTC, datetime, timedelta

    from app.models.source import Source
    from app.modules.ingest.pipeline import source_is_due

    source = Source(
        name="Due",
        slug="due",
        category="wire",
        source_type="rss",
        url="https://example.com/feed",
        enabled=True,
        tier=0,
        fetch_interval_minutes=30,
        last_ingested_at=datetime.now(UTC) - timedelta(minutes=31),
    )
    assert source_is_due(source) is True

    source.last_ingested_at = datetime.now(UTC) - timedelta(minutes=5)
    assert source_is_due(source) is False


def test_ingest_x_source_creates_articles(monkeypatch) -> None:
    from datetime import UTC, datetime

    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import sessionmaker

    from app.db.base import Base
    from app.models import Article, IngestLog, Source
    from app.modules.ingest import pipeline as ingest_pipeline
    from app.modules.ingest.rss_parser import RssItem

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    source = Source(
        name="X — Test",
        slug="x-test",
        category="social",
        source_type="x",
        url="@testuser",
        enabled=True,
        tier=0,
        fetch_interval_minutes=15,
    )
    session.add(source)
    session.commit()

    def fake_fetch_x(_url: str):
        return [
            RssItem(
                title="Breaking on X",
                url="https://x.com/testuser/status/1",
                content="Full tweet text",
                published_at=datetime.now(UTC),
            )
        ]

    monkeypatch.setattr(ingest_pipeline, "fetch_x_items", fake_fetch_x)

    result = ingest_pipeline.ingest_source(session, source.id)
    session.commit()

    assert result.status == "success"
    assert result.items_created == 1
    articles = session.scalars(select(Article)).all()
    assert len(articles) == 1
    assert articles[0].url == "https://x.com/testuser/status/1"
    logs = session.scalars(select(IngestLog)).all()
    assert logs[0].status == "success"

    session.close()
