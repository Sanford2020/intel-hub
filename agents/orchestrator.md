# Engineering Orchestrator

Coordinates **core engineering agents** after business planning is complete.

## Prerequisites

- Business phase done or skipped → see `opc-doc/state/current-stage.json`
- External assets synced → `.\scripts\sync-integrations.ps1`

## Three-layer dispatch

```
opc-doc/outputs/06-mvp-design/     ← Business (OPC)
        ↓
agents/agency/engineering/         ← Personas (Agency)
        ↓
POST /api/v1/agents/runs           ← Runtime (12-Factor)
        ↓
backend/ + apps/web/               ← Scaffold code
```

## Core team registry

See [registry.yaml](./registry.yaml) for full index.

| Agent | When |
|-------|------|
| product_manager | Requirements from opc-doc |
| architect | System design before Sprint |
| backend_engineer | API / services |
| frontend_engineer | UI pages |
| ai_engineer | Prompts + AI integration |
| devops_engineer | Docker / CI |
| qa_engineer | Tests before done |
| security_engineer | Review before merge |

## Sprint rules

1. One module per sprint — keep system runnable
2. Agent runs via 12-factor loop — no uncontrolled tool bags
3. `make test` before claiming complete
