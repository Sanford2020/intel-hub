# M4 — 外部情报栈接入规划

> **Master:** Cursor · **Backend:** Windsurf · **Test/Deploy:** Codex  
> 目标：把 38 项工具清单里 **能接进 Intel Hub 的** 全部纳入统一 ingest / delivery 管道。

## 分工（SKILLS.md）

| Phase | Owner | Skill | 产出 |
| --- | --- | --- | --- |
| 规划 / ADR | Cursor | Architecture | 本文、`TASKS.md` |
| 连接器 / Seeds / Worker | Windsurf | Backend | parsers、pipeline、seeds、docker |
| 测试 / 脚本 / 文档 | Codex | Test + Documentation | pytest、`.env.example`、`run-daily-intel` |
| UI 类型标签 | Windsurf | Frontend | `sources/page.tsx` |

## 38 项映射（能接 / 已接 / 跳过）

| # | 工具/方案 | 状态 | Intel Hub 接入方式 |
| --- | --- | --- | --- |
| 1 | last30days / Bird X | ✅ 已接 | `source_type=x` + `X_AUTH_TOKEN`/`X_CT0` |
| 2 | AI HOT 聚合站 | ✅ 已接 | RSS seeds + **`source_type=aihot`** REST 轮询 |
| 3 | Reddit / HN | ✅ 已接 | `reddit` / `hn` parsers |
| 4 | Polymarket | ✅ 已接 | `polymarket`（需 VPN） |
| 5 | RSS 多源 | ✅ 已接 | `rss` + tier-0 seeds |
| 6 | RSSHub 自建 | 🆕 M4-A | Docker `rsshub` + `seeds/rsshub-x-sources.json` |
| 7 | Apify Tweet Scraper | 🆕 M4-B | `source_type=apify` + `APIFY_TOKEN` |
| 8 | n8n 工作流 | 🆕 M4-C | 简报 **`N8N_WEBHOOK_URL`** 出站 JSON |
| 9 | Telegram Bot | 🆕 M4-C | **`TELEGRAM_BOT_TOKEN`** + `TELEGRAM_CHAT_ID` |
| 10 | 飞书 | ✅ 已接 | `FEISHU_WEBHOOK_URL` |
| 11 | Notion | 📋 脚本 | `scripts/sync-sources-to-notion.py`（已有） |
| 12 | OSINT RSS 精选 | 🆕 M4-A | `seeds/osint-rss-sources.json` |
| **BestBlogs 策展 RSS** | 🆕 M4-E | `seeds/bestblogs-sources.json`（7 条，借 AI 六维分） |
| 13 | xcancel 公共桥 | ⛔ 跳过 | 白名单/失效，改 RSSHub 或 AI HOT |
| 14 | X API v2 付费 | ✅ 可选 | `X_BEARER_TOKEN` |
| 15 | Playwright / Botasaurus | ⛔ 跳过 | 维护成本高，与 Celery 管道重复 |
| 16 | Agent-Reach / OpenClaw | 📋 外围 | 研究 CLI，不进 core ingest |
| 17 | Huginn | ⛔ 跳过 | 与 Intel Hub 调度重复 |
| 18–38 | 其余 n8n 模板 / 重复聚合 | 📋 文档 | 经 n8n webhook 消费 Intel Hub 出站 |

## 实施阶段

### Phase A — 采集扩展（P0）

1. `docker-compose.yml` 增加可选 **RSSHub** 服务（`RSSHUB_BASE_URL`）
2. `scripts/generate-rsshub-x-seeds.py`：从 `x-curated-accounts.json` 生成 RSS 源
3. `seeds/osint-rss-sources.json`：Bellingcat / ISW / Defense One 等 Tier-0 OSINT RSS
4. `batch-ingest-rss.py` / `run-daily-intel.ps1` 纳入 social-fast 队列

### Phase B — 新 source_type（P1）

- **`aihot`**：`aihot_parser.py`，REST `/api/public/items`（RSS 去重互补）
- **`apify`**：`apify_parser.py`，Apify Actor 同步跑取 X 时间线

### Phase C — 出站推送（P1）

- `delivery/webhook.py` → n8n 通用 JSON
- `delivery/telegram.py` → Telegram `sendMessage`
- `BriefingDeliveryService.deliver_all()` 多通道并行日志

### Phase D — 验证（Codex）

```powershell
cd backend
$env:PYTHONPATH=".."
python -m pytest -q
python ../scripts/generate-rsshub-x-seeds.py
python ../scripts/seed-sources.py --seed ../seeds/osint-rss-sources.json
```

## 环境变量（新增）

| 变量 | 用途 |
| --- | --- |
| `RSSHUB_BASE_URL` | 自建 RSSHub，默认 `http://localhost:1200` |
| `APIFY_TOKEN` | Apify 源 ingest |
| `APIFY_TWITTER_ACTOR` | Actor ID，默认 `apidojo~tweet-scraper` |
| `AIHOT_API_BASE` | AI HOT API 根 URL |
| `N8N_WEBHOOK_URL` | 简报 JSON 出站 |
| `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` | Telegram 推送 |
| `BRIEFING_PUSH_ENABLED` / `FEISHU_*` | 已有推送开关（补全 config） |

## 老板验收（零手动）

1. 配好 `.env` 后跑 `.\scripts\run-daily-intel.ps1`
2. 打开 `/articles` 看 OSINT + AI HOT 新条目
3. 配 webhook 后简报自动到飞书 / n8n / Telegram
