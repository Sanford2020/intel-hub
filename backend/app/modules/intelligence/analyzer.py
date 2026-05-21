"""Article intelligence analysis — prompt + AI + persistence."""

from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.config import settings
from app.core.errors import NotFoundError
from app.core.logging import get_logger
from app.models.article import Article
from app.models.intelligence_report import IntelligenceReport
from services.ai.client import AIClient, ai_client
from services.ai.prompts.base import prompt_manager

logger = get_logger(__name__)

MOCK_INTEL_JSON = (
    '{"summary":"Mock intelligence analysis.","tags":["mock","intel"],'
    '"entities":[{"name":"Example Org","type":"org"}],'
    '"relevance_score":7.5,"language":"en"}'
)


def normalize_relevance_score(score: Any) -> float:
    """Normalize to 0–10. Values in (0, 1] are treated as legacy 0–1 scale."""
    try:
        value = float(score)
    except (TypeError, ValueError):
        return 5.0
    if 0 < value <= 1.0:
        value *= 10.0
    return max(0.0, min(10.0, value))


@dataclass
class AnalyzeResult:
    article_id: int
    report_id: int
    summary: str
    tags: list[str]
    relevance_score: float
    model: str
    duration_ms: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "article_id": self.article_id,
            "report_id": self.report_id,
            "summary": self.summary,
            "tags": self.tags,
            "relevance_score": self.relevance_score,
            "model": self.model,
            "duration_ms": self.duration_ms,
        }


def build_article_user_message(article: Article) -> str:
    parts = [f"Title: {article.title}"]
    if article.url:
        parts.append(f"URL: {article.url}")
    if article.content:
        parts.append(f"Content:\n{article.content[:8000]}")
    else:
        parts.append("(No body text available; infer from title and URL.)")
    if article.language:
        parts.append(f"Detected language hint: {article.language}")
    return "\n\n".join(parts)


def normalize_analysis_payload(raw: dict[str, Any]) -> dict[str, Any]:
    tags = raw.get("tags") or []
    if not isinstance(tags, list):
        tags = [str(tags)]

    entities = raw.get("entities") or []
    if not isinstance(entities, list):
        entities = []

    normalized_entities: list[dict[str, Any]] = []
    for item in entities:
        if isinstance(item, dict) and item.get("name"):
            normalized_entities.append(
                {"name": str(item["name"]), "type": item.get("type")}
            )
        elif isinstance(item, str):
            normalized_entities.append({"name": item, "type": None})

    score = raw.get("relevance_score", 5.0)
    relevance_score = normalize_relevance_score(score)

    summary = str(raw.get("summary") or "").strip()
    if not summary:
        summary = "Analysis produced no summary."

    return {
        "summary": summary,
        "tags": [str(t) for t in tags],
        "entities": normalized_entities,
        "relevance_score": relevance_score,
        "sentiment": raw.get("sentiment"),
        "language": raw.get("language"),
    }


def parse_analysis_content(content: str) -> dict[str, Any]:
    try:
        raw = json.loads(content)
    except json.JSONDecodeError as exc:
        logger.warning("intel_analysis_json_parse_failed", error=str(exc))
        return normalize_analysis_payload({"summary": content[:2000]})
    if not isinstance(raw, dict):
        return normalize_analysis_payload({"summary": str(raw)[:2000]})
    return normalize_analysis_payload(raw)


async def call_intelligence_ai(
    article: Article,
    *,
    client: AIClient | None = None,
    prompt_template: str | None = None,
) -> tuple[dict[str, Any], str, dict[str, Any]]:
    template_name = prompt_template or settings.intel_prompt_template
    prompt_def = prompt_manager.load_yaml(template_name)
    client = client or ai_client

    messages = [
        prompt_def.to_system_message(),
        {"role": "user", "content": build_article_user_message(article)},
    ]
    response = await client.structured_output(
        messages=messages,
        temperature=prompt_def.temperature,
        max_tokens=prompt_def.max_tokens,
    )
    content = response.get("content") or MOCK_INTEL_JSON
    parsed = parse_analysis_content(content)
    model = str(response.get("model") or settings.openai_model)
    return parsed, model, {"content": content, "usage": response.get("usage")}


def upsert_intelligence_report(
    session: Session,
    article_id: int,
    parsed: dict[str, Any],
    *,
    model: str,
    prompt_template: str,
    raw_json: dict[str, Any] | None,
) -> IntelligenceReport:
    report = session.scalar(
        select(IntelligenceReport).where(IntelligenceReport.article_id == article_id)
    )
    fields = {
        "summary": parsed["summary"],
        "tags": parsed["tags"],
        "entities": parsed["entities"],
        "relevance_score": normalize_relevance_score(parsed.get("relevance_score", 5.0)),
        "sentiment": parsed.get("sentiment"),
        "language": parsed.get("language"),
        "model": model,
        "prompt_template": prompt_template,
        "raw_json": raw_json,
    }
    if report:
        for key, value in fields.items():
            setattr(report, key, value)
    else:
        report = IntelligenceReport(article_id=article_id, **fields)
        session.add(report)
    session.flush()
    return report


def analyze_article_sync(
    session: Session,
    article_id: int,
    *,
    client: AIClient | None = None,
    prompt_template: str | None = None,
) -> AnalyzeResult:
    started = time.perf_counter()
    article = session.get(Article, article_id)
    if not article:
        raise NotFoundError(message=f"Article {article_id} not found")

    template_name = prompt_template or settings.intel_prompt_template
    parsed, model, raw_json = asyncio.run(
        call_intelligence_ai(
            article, client=client, prompt_template=template_name
        )
    )
    report = upsert_intelligence_report(
        session,
        article_id,
        parsed,
        model=model,
        prompt_template=template_name,
        raw_json=raw_json,
    )
    duration_ms = int((time.perf_counter() - started) * 1000)
    logger.info(
        "analyze_article.done",
        article_id=article_id,
        report_id=report.id,
        model=model,
        duration_ms=duration_ms,
    )
    try:
        from app.modules.alerts.service import evaluate_alerts_for_article_sync

        evaluate_alerts_for_article_sync(session, article_id)
    except Exception as exc:  # noqa: BLE001
        logger.warning("alert_eval_failed", article_id=article_id, error=str(exc))
    return AnalyzeResult(
        article_id=article_id,
        report_id=report.id,
        summary=report.summary,
        tags=report.tags,
        relevance_score=report.relevance_score,
        model=model,
        duration_ms=duration_ms,
    )


async def analyze_article_async(
    session: AsyncSession,
    article_id: int,
    *,
    client: AIClient | None = None,
    prompt_template: str | None = None,
) -> IntelligenceReport:
    started = time.perf_counter()
    article = await session.get(Article, article_id)
    if not article:
        raise NotFoundError(message=f"Article {article_id} not found")

    template_name = prompt_template or settings.intel_prompt_template
    parsed, model, raw_json = await call_intelligence_ai(
        article, client=client, prompt_template=template_name
    )

    report = await session.scalar(
        select(IntelligenceReport).where(
            IntelligenceReport.article_id == article_id
        )
    )
    fields = {
        "summary": parsed["summary"],
        "tags": parsed["tags"],
        "entities": parsed["entities"],
        "relevance_score": normalize_relevance_score(parsed.get("relevance_score", 5.0)),
        "sentiment": parsed.get("sentiment"),
        "language": parsed.get("language"),
        "model": model,
        "prompt_template": template_name,
        "raw_json": raw_json,
    }
    if report:
        for key, value in fields.items():
            setattr(report, key, value)
    else:
        report = IntelligenceReport(article_id=article_id, **fields)
        session.add(report)

    await session.flush()
    await session.refresh(report)
    duration_ms = int((time.perf_counter() - started) * 1000)
    logger.info(
        "analyze_article_async.done",
        article_id=article_id,
        report_id=report.id,
        duration_ms=duration_ms,
    )
    return report


async def get_report_for_article(
    session: AsyncSession, article_id: int
) -> IntelligenceReport:
    if not await session.get(Article, article_id):
        raise NotFoundError(message=f"Article {article_id} not found")
    report = await session.scalar(
        select(IntelligenceReport).where(
            IntelligenceReport.article_id == article_id
        )
    )
    if not report:
        raise NotFoundError(
            message=f"No intelligence report for article {article_id}"
        )
    return report
