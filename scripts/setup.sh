#!/bin/bash
set -e

echo "=== OPC Scaffold Setup ==="

# Backend setup
echo ""
echo "--- Setting up Backend ---"
cd backend
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created backend/.env from .env.example"
fi
poetry install
echo "Backend dependencies installed"
cd ..

# Frontend setup
echo ""
echo "--- Setting up Frontend ---"
cd apps/web
if [ ! -f .env.local ]; then
    cp .env.example .env.local
    echo "Created apps/web/.env.local from .env.example"
fi
npm install
echo "Frontend dependencies installed"
cd ../..

# Shared types
echo ""
echo "--- Setting up Shared Types ---"
cd packages/shared-types
npm install
echo "Shared types ready"
cd ../..

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "  1. Start services:     docker compose up -d db redis"
echo "  2. Run migrations:     cd backend && poetry run alembic upgrade head"
echo "  3. Start backend:      cd backend && poetry run uvicorn app.main:app --reload"
echo "  4. Start frontend:     cd apps/web && npm run dev"
echo "  5. Or use Docker:      docker compose up"
