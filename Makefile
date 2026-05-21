.PHONY: help setup lint test migrate dev docker-up docker-down clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

sync: ## Sync opc-methodology skills + agency-agents
	@powershell -ExecutionPolicy Bypass -File scripts/sync-integrations.ps1

setup: ## Install all dependencies
	@bash scripts/setup.sh

lint: ## Run all linters
	@bash scripts/lint.sh

test: ## Run all tests
	@bash scripts/test.sh

migrate: ## Run database migrations (usage: make migrate or make migrate CMD=generate NAME=add_users)
	@bash scripts/migrate.sh $(CMD) $(NAME)

dev-backend: ## Start backend dev server
	cd backend && PYTHONPATH=.. poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Start frontend dev server
	cd apps/web && npm run dev

dev-worker: ## Start Celery worker
	cd backend && PYTHONPATH=.. poetry run celery -A workers.celery_app worker --loglevel=info

docker-up: ## Start all services with Docker
	docker compose up -d

docker-down: ## Stop all Docker services
	docker compose down

docker-build: ## Build all Docker images
	docker compose build

docker-logs: ## View Docker logs
	docker compose logs -f

clean: ## Clean build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .next -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name dist -exec rm -rf {} + 2>/dev/null || true

format: ## Format all code
	cd backend && poetry run ruff format app/ tests/
	cd apps/web && npm run format
