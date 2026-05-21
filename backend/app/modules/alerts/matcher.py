"""Keyword matching for alert rules."""

from __future__ import annotations

from app.models.alert_rule import AlertRule
from app.models.article import Article
from app.models.intelligence_report import IntelligenceReport


def _collect_search_text(
    article: Article,
    report: IntelligenceReport | None,
    match_in: str,
) -> str:
    parts: list[str] = []
    if match_in in ("title", "all"):
        parts.append(article.title or "")
    if match_in in ("content", "all") and article.content:
        parts.append(article.content)
    if match_in in ("tags", "all") and report and report.tags:
        parts.extend(report.tags)
    if match_in in ("all",) and report and report.summary:
        parts.append(report.summary)
    return " ".join(parts).lower()


def match_keywords(
    article: Article,
    report: IntelligenceReport | None,
    rule: AlertRule,
) -> list[str]:
    if not rule.enabled or not rule.keywords:
        return []
    haystack = _collect_search_text(article, report, rule.match_in)
    matched: list[str] = []
    for keyword in rule.keywords:
        if keyword.lower() in haystack:
            matched.append(keyword)
    return matched
