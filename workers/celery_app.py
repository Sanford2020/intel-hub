from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery_app = Celery(
    "intel_hub_worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_default_queue="default",
    task_queues={
        "default": {"exchange": "default", "routing_key": "default"},
        "ingest": {"exchange": "ingest", "routing_key": "ingest"},
    },
    beat_schedule={
        "dispatch-due-rss-sources": {
            "task": "workers.tasks.ingest.fetch_rss.dispatch_due_rss_sources",
            "schedule": crontab(minute="*/5"),
        },
        "dispatch-unanalyzed-articles": {
            "task": "workers.tasks.analyze.dispatch.dispatch_unanalyzed_articles",
            "schedule": crontab(minute="*/10"),
        },
        "generate-daily-briefing": {
            "task": "workers.tasks.briefings.generate.generate_daily_briefing",
            "schedule": crontab(hour=6, minute=0),
        },
        "archive-daily-snapshot": {
            "task": "workers.tasks.archives.snapshot.archive_daily_snapshot",
            "schedule": crontab(hour=6, minute=15),
        },
    },
)

celery_app.autodiscover_tasks(
    [
        "workers.tasks",
        "workers.tasks.ingest",
        "workers.tasks.analyze",
        "workers.tasks.alerts",
        "workers.tasks.briefings",
        "workers.tasks.archives",
    ]
)
