"""
Base model module.

Import all models here so Alembic can detect them.
Example:
    from app.models.user import User  # noqa: F401
"""

from app.db.base import Base
from app.models.alert_event import AlertEvent  # noqa: F401
from app.models.alert_rule import AlertRule  # noqa: F401
from app.models.article import Article  # noqa: F401
from app.models.briefing_delivery_log import BriefingDeliveryLog  # noqa: F401
from app.models.daily_archive import DailyArchive  # noqa: F401
from app.models.ingest_log import IngestLog  # noqa: F401
from app.models.intelligence_report import IntelligenceReport  # noqa: F401
from app.models.source import Source  # noqa: F401
from app.models.user import User, UserSession  # noqa: F401

__all__ = [
    "Base",
    "Source",
    "Article",
    "IngestLog",
    "IntelligenceReport",
    "AlertRule",
    "AlertEvent",
    "BriefingDeliveryLog",
    "DailyArchive",
    "User",
    "UserSession",
]
