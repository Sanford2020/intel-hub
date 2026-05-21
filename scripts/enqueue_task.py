#!/usr/bin/env python3
"""Enqueue a Celery task from CLI."""

import sys


def main() -> None:
    task_name = sys.argv[1] if len(sys.argv) > 1 else "workers.tasks.example.example_task"
    payload = sys.argv[2] if len(sys.argv) > 2 else "hello"

    from workers.celery_app import celery_app

    result = celery_app.send_task(task_name, args=[payload])
    print(f"Enqueued {task_name} → task_id={result.id}")


if __name__ == "__main__":
    main()
