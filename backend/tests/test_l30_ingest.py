import json

from app.modules.ingest.reddit_parser import fetch_reddit_items


def test_fetch_reddit_items_parses_hot(monkeypatch) -> None:
    sample = {
        "data": {
            "children": [
                {
                    "kind": "t3",
                    "data": {
                        "title": "Breaking news",
                        "permalink": "/r/worldnews/comments/abc123/title/",
                        "score": 1200,
                        "num_comments": 88,
                        "subreddit": "worldnews",
                        "author": "tester",
                        "selftext": "Details here",
                        "created_utc": 1710000000.0,
                    },
                }
            ]
        }
    }

    monkeypatch.setattr(
        "app.modules.ingest.reddit_parser._fetch_with_backoff",
        lambda *_args, **_kwargs: sample,
    )

    items = fetch_reddit_items("r/worldnews")
    assert len(items) == 1
    assert "Breaking news" in items[0].title
    assert "1200" in items[0].title or "↑1200" in items[0].title
    assert items[0].url == "https://www.reddit.com/r/worldnews/comments/abc123/title/"


def test_fetch_hn_items_parses_algolia(monkeypatch) -> None:
    from app.modules.ingest.hn_parser import fetch_hn_items

    sample = {
        "hits": [
            {
                "objectID": "123",
                "title": "Show HN: Intel Hub",
                "url": "https://example.com",
                "points": 150,
                "num_comments": 42,
                "author": "dang",
                "created_at_i": 1710000000,
            }
        ]
    }

    class FakeResponse:
        def json(self):
            return sample

    monkeypatch.setattr(
        "app.modules.ingest.hn_parser.fetch_url",
        lambda *_args, **_kwargs: FakeResponse(),
    )

    items = fetch_hn_items("search:intel hub")
    assert len(items) == 1
    assert "Intel Hub" in items[0].title
    assert items[0].url == "https://example.com"


def test_fetch_polymarket_items_parses_events(monkeypatch) -> None:
    from app.modules.ingest.polymarket_parser import fetch_polymarket_items

    sample = {
        "events": [
            {
                "title": "Will X happen?",
                "slug": "will-x-happen",
                "markets": [{"question": "Yes", "outcomePrices": "[\"0.72\",\"0.28\"]"}],
                "volume": 50000,
            }
        ]
    }

    class FakeResponse:
        def json(self):
            return sample

    monkeypatch.setattr(
        "app.modules.ingest.polymarket_parser.fetch_url",
        lambda *_args, **_kwargs: FakeResponse(),
    )

    items = fetch_polymarket_items("search:Iran")
    assert len(items) == 1
    assert "Will X happen?" in items[0].title
    assert "polymarket.com/event/will-x-happen" in items[0].url


def test_ingest_reddit_source_creates_articles(monkeypatch) -> None:
    from datetime import UTC, datetime

    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import sessionmaker

    from app.db.base import Base
    from app.models import Article, Source
    from app.modules.ingest import pipeline as ingest_pipeline
    from app.modules.ingest.rss_parser import RssItem

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    source = Source(
        name="Reddit test",
        slug="reddit-test",
        category="social",
        source_type="reddit",
        url="r/worldnews",
        enabled=True,
        tier=0,
        fetch_interval_minutes=15,
    )
    session.add(source)
    session.commit()

    monkeypatch.setattr(
        ingest_pipeline,
        "fetch_reddit_items",
        lambda _url: [
            RssItem(
                title="Post",
                url="https://reddit.com/r/worldnews/comments/1/a",
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
