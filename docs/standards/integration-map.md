# Three-Pillar Integration Map

OPC Scaffold integrates three open-source standards into one workflow:

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: OPC Methodology (easychen/opc-methodology)        │
│  WHAT to build · WHY · business model · MVP · conversion    │
│  → skills/opc/ · opc-doc/                                   │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: Agency Agents (msitarzewski/agency-agents)        │
│  WHO does the work · specialized personas · deliverables    │
│  → agents/agency/ · agents/registry.yaml                      │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: 12-Factor Agents (humanlayer/12-factor-agents)    │
│  HOW agents run in production · loop · state · tools          │
│  → services/agent/ · prompts/agents/                          │
├─────────────────────────────────────────────────────────────┤
│  OPC Scaffold (this repo)                                     │
│  Monorepo · FastAPI · Next.js · Celery · Docker               │
└─────────────────────────────────────────────────────────────┘
```

## Workflow

| Phase | Layer | Action |
|-------|-------|--------|
| 1. Discover | OPC Methodology | Run `skills/opc/opc-orchestrator` → outputs to `opc-doc/` |
| 2. Plan | Agency + Core | Pick agents from `agents/registry.yaml` |
| 3. Build | 12-Factor + Scaffold | Implement via Sprint; agent loop in `services/agent/` |
| 4. Ship | Scaffold | Docker, CI, tests |

## Sync external assets

```powershell
.\scripts\sync-integrations.ps1
```

See [integrations.yaml](../config/integrations.yaml) for repo URLs and licenses.
