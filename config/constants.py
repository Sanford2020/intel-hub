"""
Application-wide constants.

These values rarely change and are not environment-specific.
"""

API_V1_PREFIX = "/api/v1"
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

SUPPORTED_LANGUAGES = ["en", "zh"]

TASK_QUEUES = {
    "default": "default",
    "high_priority": "high_priority",
    "ai": "ai_tasks",
}
