# Release Workflow

发布前检查清单（生产目标 **TODO / UNKNOWN**）。

## 1. 测试

```powershell
cd backend
$env:PYTHONPATH="C:\Users\sanford\Desktop\ai_code_new\intel-hub"
python -m pytest tests/ -q
```

```powershell
cd apps\web
npm run type-check
npm run build
```

## 2. Build

```powershell
docker compose build
docker compose config
```

## 3. Release Check

- [ ] `APP_ENV=production`、`APP_DEBUG=false`
- [ ] `SECRET_KEY` 已轮换
- [ ] `DATABASE_URL` / Redis / `OPENAI_API_KEY` 已配置
- [ ] `alembic upgrade head` 已在目标环境执行
- [ ] Worker + Beat 监督策略已定义（**TODO**）
- [ ] 备份策略（**TODO**）
- [ ] 监控/日志（**TODO**）

## 4. 文档同步

- [ ] `docs/deployment.md`
- [ ] `docs/api.md`
- [ ] `DECISIONS.md`（发布相关 ADR）
- [ ] `TASKS.md` 发布 TASK → DONE

## 5. 发布记录

在 `DECISIONS.md` 或 `docs/operations/`（**TODO 目录**）记录：

- 版本号 / 日期
- 迁移版本
- 已知问题
- 回滚步骤

## Verdict

`GO` | `NO-GO`（Master Agent + Deployment Skill 共同确认）
