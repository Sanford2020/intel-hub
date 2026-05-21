# Windows Local Development

Project path:

```powershell
C:\Users\sanford\Desktop\ai_code_new\intel-hub
```

## Setup

```powershell
cd C:\Users\sanford\Desktop\ai_code_new\intel-hub
.\scripts\setup.ps1
```

`setup.ps1` installs backend requirements with pip, installs frontend dependencies, and creates local env files from examples when missing.

## Infrastructure

```powershell
docker compose up -d db redis
```

## Database Migration

```powershell
cd C:\Users\sanford\Desktop\ai_code_new\intel-hub\backend
$env:PYTHONPATH="C:\Users\sanford\Desktop\ai_code_new\intel-hub"
alembic upgrade head
```

## Start Services

Use separate terminals:

```powershell
.\scripts\dev.ps1 backend
.\scripts\dev.ps1 worker
.\scripts\dev.ps1 beat
.\scripts\dev.ps1 frontend
```

## URLs

| Service | URL |
| --- | --- |
| Frontend | http://localhost:3000 |
| API docs | http://localhost:8000/docs |
| Health | http://localhost:8000/api/v1/health |
| Prompts | http://localhost:8000/api/v1/ai/prompts |

## Tests

```powershell
cd C:\Users\sanford\Desktop\ai_code_new\intel-hub\backend
$env:PYTHONPATH="C:\Users\sanford\Desktop\ai_code_new\intel-hub"
python -m pytest tests/ -q
```

```powershell
cd C:\Users\sanford\Desktop\ai_code_new\intel-hub\apps\web
npm run type-check
npm run test:run
npm run build
```

## Common Issues

- Poetry unavailable: use `pip install -r backend/requirements.txt`.
- Backend offline in the UI: start `.\scripts\dev.ps1 backend`.
- `ModuleNotFoundError: services`: ensure `PYTHONPATH` points to the repo root.
- Empty database: run Alembic migrations before starting workers.
- Real AI not enabled: set `OPENAI_API_KEY` in `backend/.env`; otherwise analysis uses the configured fallback behavior.
