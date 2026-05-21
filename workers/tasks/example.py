import time

from workers.celery_app import celery_app


@celery_app.task(bind=True, name="tasks.example_task")
def example_task(self, data: dict) -> dict:  # type: ignore[type-arg]
    """Example async task demonstrating Celery worker pattern."""
    task_id = self.request.id
    total_steps = data.get("steps", 5)

    for step in range(total_steps):
        self.update_state(
            state="PROGRESS",
            meta={"current": step + 1, "total": total_steps},
        )
        time.sleep(1)

    return {
        "task_id": task_id,
        "status": "completed",
        "result": f"Processed {total_steps} steps",
    }


@celery_app.task(name="tasks.send_notification")
def send_notification(channel: str, message: str) -> dict[str, str]:
    """Example notification task."""
    return {
        "channel": channel,
        "message": message,
        "status": "sent",
    }
