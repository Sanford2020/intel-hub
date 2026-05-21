"""BestBlogs RSS feed parsing smoke tests."""

from __future__ import annotations

from app.modules.ingest.rss_parser import parse_rss_feed


def test_parse_bestblogs_rss_sample() -> None:
    """BestBlogs RSS uses standard RSS/Atom fields."""
    sample = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>BestBlogs</title>
    <item>
      <title>Andrej Karpathy Joins Anthropic</title>
      <link>https://www.bestblogs.dev/article/example</link>
      <description>Summary from BestBlogs AI analysis.</description>
      <pubDate>Mon, 19 May 2026 08:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>"""
    items = parse_rss_feed(sample)
    assert len(items) == 1
    assert "Karpathy" in items[0].title
    assert items[0].url == "https://www.bestblogs.dev/article/example"
