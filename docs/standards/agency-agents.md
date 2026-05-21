# Agency Agents (Persona Layer)

Source: [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) (MIT)

Specialized AI agent personas with personality, workflows, and deliverables.

## Synced to `agents/agency/`

Run `.\scripts\sync-integrations.ps1` to pull divisions:

| Division | Use case |
|----------|----------|
| engineering | Backend, frontend, AI, DevOps implementation |
| design | UI/UX, visual design |
| product | Product management, specs |
| marketing | Growth, content, SEO |
| testing | QA, evidence-based review |
| project-management | Sprint planning, coordination |
| strategy | Architecture, business strategy |

## Integration with scaffold

- **Core agents** (`agents/roles/`) — minimal 8-role engineering team for any project
- **Agency agents** (`agents/agency/`) — extended roster from The Agency
- **Registry** (`agents/registry.yaml`) — unified index, maps role → file path → layer

## Cursor / Claude usage

After sync, reference agents in chat:

```
Activate Backend Architect from agents/agency/engineering/
Follow AGENTS.md and 12-factor agent loop for implementation.
```

Upstream install: `./scripts/install.sh --tool cursor` (in agency-agents repo)
