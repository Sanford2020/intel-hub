# Intel Hub — 老板一页纸

> 你不需要看代码。打开下面链接或跑一条命令即可验收。

## 日常看什么

| 看什么 | 地址 / 命令 |
| --- | --- |
| **每日简报（主交付）** | http://localhost:3000/briefing |
| **今日精选资讯** | http://localhost:3000/articles → 点「今日精选」 |
| **系统概况** | http://localhost:3000 |
| **API 文档** | http://localhost:8000/docs |

## 一键跑今日情报（推荐）

前提：Docker（Postgres+Redis）已起，且另开终端跑过 `.\scripts\dev.ps1 worker` 与 `beat`（或 `all`）。

```powershell
cd C:\Users\sanford\Desktop\ai_code_new\intel-hub
.\scripts\run-daily-intel.ps1
```

然后打开 **http://localhost:3000/briefing**。

## 首次启动（本机）

```powershell
.\scripts\setup.ps1          # 依赖
docker compose up -d         # 数据库
.\scripts\dev.ps1 all        # 后端+前端+Worker+Beat（多窗口见 deployment.md）
```

## 飞书推送（可选）

在 `backend/.env` 配置：

```env
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/...
BRIEFING_PUBLIC_BASE_URL=http://你的前端地址:3000
```

Beat 每天 UTC 06:00 自动生成简报并推送；也可：

```powershell
.\scripts\run-daily-intel.ps1 -SkipIngest   # 仅生成+推送
```

## 健康检查

```powershell
.\scripts\validate_project.ps1 -Quick -SkipDocker
```

## AI 团队分工（你不用管）

- **Cursor**：总调度、Review、架构
- **Windsurf**：写功能
- **Codex**：测试、部署文档、脚本

任务看板：`TASKS.md` · 风险：`REVIEW.md`
