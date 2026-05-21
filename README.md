# Intel Hub — 全球情报 · 资讯搜集中台



基于 OPC Scaffold 的全球情报与资讯聚合中台。当前定位为 **Commercial Edition 商业版**：面向研究、投资、媒体与小团队的日常情报运营工作台。


## 能力一览



| 能力 | 说明 |

|------|------|

| 多源采集 | RSS 定时 + 手动触发，Celery Beat |

| 资讯归一 | 去重 hash，PostgreSQL |

| AI 分析 | 摘要 / 标签 / 实体（OpenAI 或 mock） |

| 检索过滤 | 来源、标签、日期、关键词、报告状态 |

| 商业情报工作台 | 来源 / 资讯 / 详情 / 统计首页 |
| 关键词告警 | 规则 CRUD + log/webhook/email_stub 通知 |



## 快速开始



```powershell

cd C:\Users\sanford\Desktop\ai_code_new\intel-hub

.\scripts\setup.ps1

docker compose up -d db redis



# 迁移

cd backend

set PYTHONPATH=C:\Users\sanford\Desktop\ai_code_new\intel-hub

alembic upgrade head

cd ..



# 四个终端

.\scripts\dev.ps1 backend

.\scripts\dev.ps1 worker

.\scripts\dev.ps1 beat

.\scripts\dev.ps1 frontend



# 可选：导入 tier-0 情报源

python scripts\seed-sources.py

```



| 入口 | URL |

|------|-----|

| Dashboard | http://localhost:3000 |

| 来源 | http://localhost:3000/sources |

| 资讯 | http://localhost:3000/articles |

| 告警 | http://localhost:3000/alerts |

| API | http://localhost:8000/docs |



## 流水线



```

RSS 采集 → 文章入库 → AI 分析 → 关键词告警 → 通知

         ↑ beat 5min    ↑ queue      ↑ 自动匹配

```



## 测试



```powershell

cd backend

set PYTHONPATH=C:\Users\sanford\Desktop\ai_code_new\intel-hub

python -m pytest tests/ -q

cd ..\apps\web && npm run build

```



## 文档



- [产品简报](./docs/project/intel-hub-brief.md)

- [Sprint 计划](./docs/project/sprint-plan.md)

- [架构](./docs/project/intel-hub-architecture.md)

- [项目简报](./PROJECT_BRIEF.md)

- [多 Agent Sprint](./.multi-agent/sprint.md)

- [多 Agent 协作协议](./.multi-agent/docs/COLLABORATION_PROTOCOL.md)

## 多 Agent 开发

本项目已接入 `.multi-agent/` 工作区。新 agent 开工前先阅读：

1. `PROJECT_BRIEF.md`
2. `.multi-agent/sprint.md`
3. `.multi-agent/docs/AGENT_ROLES.md`
4. 对应任务卡：`.multi-agent/task-cards/*.md`

每个 agent 开工前必须声明 `Role / Scope / Files owned / Files avoided / Verification`，交付时写清 `Changed / Verified / Risks / Next`。
