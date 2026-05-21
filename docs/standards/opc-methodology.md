# OPC Methodology (Business Layer)

Source: [easychen/opc-methodology](https://github.com/easychen/opc-methodology) (CC-BY-NC-SA-4.0)

《一人企业方法论》— defines **what** to build and **how** to operate a one-person company.

> License note: methodology text is CC-BY-NC-SA. Link and use skills locally; verify terms before commercial redistribution.

## Skills (synced to `skills/opc/`)

| Skill | Purpose |
|-------|---------|
| opc-orchestrator | Full workflow orchestration |
| opc-resource-audit | Resource inventory (stage 01) |
| opc-niche-positioning | Niche positioning (stage 02) |
| opc-value-proposition | Value proposition (stage 03) |
| opc-business-model-design | Business model canvas (stage 04) |
| opc-mvp-designer | MVP scope (stage 06) |
| opc-conversion-loop | Conversion funnel (stage 07) |
| opc-asset-ops | Asset systematization (stage 08) |
| opc-dashboard-review | Operations review (stage 09) |

## Output directory: `opc-doc/`

```
opc-doc/
├── state/           # current-stage.json, decisions.json
├── inputs/          # user inputs
└── outputs/         # per-stage deliverables
```

Scaffold provides template structure; skills populate content during OPC workflow.

## When to use

- **Before coding**: run opc-orchestrator to define MVP and business model
- **During ops**: opc-dashboard-review, opc-asset-ops
- **With engineering**: hand off `opc-doc/outputs/06-mvp-design/` to Agency engineering agents

Resources: [在线阅读](https://ft07.com/opb-methodology-new-version-and-author) · [技能集网站](https://opc-skills.ft07.com/)
