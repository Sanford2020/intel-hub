# M6 — Commercial Auth Foundation

> **Master:** Cursor · **Builder:** Windsurf · **Validation:** Codex  
> 状态：ADR Accepted · 2026-06-01 · **ADR-20260601-01**

## 1. 触发条件

- S1 (M5) DONE — live acceptance smoke PASS (2026-05-22).
- 老板需要将 Hub 交给外部账号使用（公网或 VPN 外可达）。

## 2. 目标

未登录用户 **不能** 访问 dashboard 与 `/api/v1/*`（除 health/login）。支持 Admin / Operator / Analyst 三角色 RBAC。

## 3. 非目标

多租户计费、SSO、OAuth、invite flow — 见 ADR-20260601-01。

## 4. 派单顺序（强串行）

```text
M6-ADR  Cursor   ADR + 任务卡 + TASKS  (DONE)
  └─→ M6-A  Windsurf Backend   User/Session/JWT + /auth/*
        └─→ M6-B  Windsurf Backend   保护现有 API + RBAC
              └─→ M6-C  Windsurf Frontend   /login + AuthProvider + middleware
                    └─→ M6-D  Codex   test_auth + docs + deployment + smoke
```

## 5. 任务卡

| Task | 文件 | Validation |
| --- | --- | --- |
| M6-A | `.multi-agent/task-cards/TASK-20260601-M6-A.md` | migration OK; login returns JWT; `/auth/me` 200 |
| M6-B | `.multi-agent/task-cards/TASK-20260601-M6-B.md` | 未带 token → 401；analyst 不能 POST sources |
| M6-C | `.multi-agent/task-cards/TASK-20260601-M6-C.md` | 未登录访问 `/` → `/login`；登录后进工作台 |
| M6-D | `.multi-agent/task-cards/TASK-20260601-M6-D.md` | `pytest tests/test_auth.py -q`；acceptance-smoke 含 login |

## 6. 老板验收

1. 公网部署后，未登录打开任意业务页 → 跳转 `/login`。
2. Admin 可创建 Operator / Analyst 账号。
3. Analyst 登录后只能浏览，不能改来源或告警规则。
4. `pytest -q` 与 acceptance-smoke 全绿（含鉴权步骤）。
