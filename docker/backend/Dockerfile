FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

FROM base AS deps

COPY backend/requirements.txt ./
RUN pip install --prefix=/install -r requirements.txt

FROM base AS production

COPY --from=deps /install /usr/local

COPY backend/app ./app
COPY backend/alembic.ini ./
COPY services ./services
COPY packages ./packages
COPY config ./config
COPY prompts ./prompts
COPY agents ./agents
COPY workers ./workers
COPY skills ./skills

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/ping || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
