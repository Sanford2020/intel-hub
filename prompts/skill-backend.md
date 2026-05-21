# Backend Skill

## 绑定工具

Windsurf（首选）

## 职责

- `backend/app/modules/**`、API 路由、Schema
- `workers/tasks/**` Celery 任务
- Alembic 迁移（仅 TASK 授权时）

## 范围

| 允许 | 禁止 |
| --- | --- |
| `backend/**`、`workers/**` | `apps/web/**` UI |
| `services/ai/**`（若 TASK 涉及） | 未授权新框架 |
| 后端 pytest | 顺手格式化全库 |

## 契约

- API 变更 → `docs/api.md` + 通知 Frontend Skill 更新 types

## 启动语

```
Backend Skill：仅实现 TASK-[ID] 中 backend/workers 范围。禁止改前端。含迁移则附 rollback 说明。
```
