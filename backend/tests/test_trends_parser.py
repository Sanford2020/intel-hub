"""Tests for trend aggregator HTML parsers."""

from __future__ import annotations

from app.modules.ingest.trends_parser import (
    _parse_getdaytrends,
    _parse_trend_calendar,
    _parse_trends24,
    fetch_trends_items,
)


SAMPLE_TRENDS24 = """
<a href="https://twitter.com/search?q=%23LOLFanFest2026D1">#LOLFanFest</a>
<a href="https://twitter.com/search?q=Ashnisha%20Industries">Ashnisha</a>
<a href="https://twitter.com/search?q=%23LOLFanFest2026D1">dup</a>
"""

SAMPLE_GETDAYTRENDS = """
<a href="/trend/%23Essel100/">Essel</a>
<a href="/trend/%23CHPTeslimAl%C4%B1namaz/">CHP</a>
"""

SAMPLE_CALENDAR = """
<a href="https://twitter.com/search?q=%23HealthyLiving">X</a>
<a href="https://www.google.com/search?q=neet+2026+fee+refund">G</a>
"""


def test_parse_trends24_dedupes() -> None:
    items = _parse_trends24(SAMPLE_TRENDS24)
    assert len(items) == 2
    assert "LOLFanFest2026D1" in items[0].title
    assert items[0].url and "twitter.com/search" in items[0].url


def test_parse_getdaytrends_builds_urls() -> None:
    items = _parse_getdaytrends(SAMPLE_GETDAYTRENDS, "https://getdaytrends.com/")
    assert len(items) == 2
    assert items[0].url == "https://getdaytrends.com/trend/%23Essel100/"


def test_parse_trend_calendar_platform_filter() -> None:
    x_items = _parse_trend_calendar(SAMPLE_CALENDAR, platform="x")
    g_items = _parse_trend_calendar(SAMPLE_CALENDAR, platform="google")
    assert len(x_items) == 1
    assert len(g_items) == 1
    assert "google.com" in (g_items[0].url or "")


def test_fetch_trends_items_monkeypatch(monkeypatch) -> None:
    class FakeResponse:
        text = SAMPLE_TRENDS24

    monkeypatch.setattr(
        "app.modules.ingest.trends_parser.fetch_url",
        lambda *_args, **_kwargs: FakeResponse(),
    )
    items = fetch_trends_items("https://trends24.in/")
    assert len(items) >= 1
