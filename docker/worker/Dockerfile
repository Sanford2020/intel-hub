FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./
RUN pip install -r requirements.txt

COPY backend/app ./app
COPY workers ./workers
COPY services ./services
COPY packages ./packages
COPY config ./config
COPY prompts ./prompts

CMD ["celery", "-A", "workers.celery_app", "worker", "--loglevel=info", "--concurrency=4"]
