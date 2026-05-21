#!/bin/bash
set -e

echo "=== Running Tests ==="

echo ""
echo "--- Backend Tests ---"
cd backend
poetry run pytest tests/ -v --tb=short
cd ..

echo ""
echo "--- Frontend Tests ---"
cd apps/web
npm run test:run
cd ../..

echo ""
echo "=== All Tests Passed ==="
