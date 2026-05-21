# Agent System

Three integrated layers — see [integration-map](../docs/standards/integration-map.md).

| Layer | Source | Location |
|-------|--------|----------|
| Business | [opc-methodology](https://github.com/easychen/opc-methodology) | `skills/opc/` |
| Personas | [agency-agents](https://github.com/msitarzewski/agency-agents) | `agents/agency/` |
| Runtime | [12-factor-agents](https://github.com/humanlayer/12-factor-agents) | `services/agent/` |

## Directories

```
agents/
├── registry.yaml       # Unified index
├── orchestrator.md     # Engineering multi-agent workflow
├── roles/              # Core 8 engineering roles (built-in)
└── agency/             # The Agency personas (sync required)

skills/
└── opc/                # OPC methodology skills (sync required)

opc-doc/                # OPC workflow outputs (created during use)
```

## Setup

```powershell
.\scripts\sync-integrations.ps1   # Pull opc skills + agency agents
```

## Usage flow

1. **Business** — `skills/opc/opc-orchestrator` → writes to `opc-doc/`
2. **Personas** — pick agent from `registry.yaml` or `agents/agency/`
3. **Runtime** — `POST /api/v1/agents/runs` for 12-factor agent loop
