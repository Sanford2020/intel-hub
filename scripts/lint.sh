#!/bin/bash
set -e

echo "=== Running Linters ==="

echo ""
echo "--- Backend (ruff) ---"
cd backend
poetry run ruff check app/ tests/
poetry run ruff format --check app/ tests/
cd ..

echo ""
echo "--- Frontend (eslint + tsc) ---"
cd apps/web
npm run lint
npm run type-check
cd ../..

echo ""
echo "=== All Lint Checks Passed ==="
