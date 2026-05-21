#!/bin/bash
set -e

echo "=== Database Migration ==="

cd backend

case "${1:-upgrade}" in
    upgrade)
        echo "Running migrations..."
        poetry run alembic upgrade head
        echo "Migrations complete"
        ;;
    downgrade)
        echo "Rolling back last migration..."
        poetry run alembic downgrade -1
        echo "Rollback complete"
        ;;
    generate)
        if [ -z "$2" ]; then
            echo "Usage: ./scripts/migrate.sh generate <migration_name>"
            exit 1
        fi
        echo "Generating migration: $2"
        poetry run alembic revision --autogenerate -m "$2"
        echo "Migration generated"
        ;;
    history)
        poetry run alembic history
        ;;
    current)
        poetry run alembic current
        ;;
    *)
        echo "Usage: ./scripts/migrate.sh [upgrade|downgrade|generate <name>|history|current]"
        exit 1
        ;;
esac
