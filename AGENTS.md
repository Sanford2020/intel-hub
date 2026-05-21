# AGENTS.md

Intel Hub **AI 软件工程操作系统**总规范。架构：**Single Master Agent (Cursor) + Multiple Skills**。

| 文档 | 用途 |
| --- | --- |
| `SKILLS.md` | Skill 定义与生命周期 |
| `TASKS.md` | 任务看板 |
| `prompts/master-agent.md` | Master Prompt |
| `prompts/skill-*.md` | 各 Skill Prompt |
| `workflows/*.md` | 标准/Debug/Review/Release 流程 |
| `.cursor/rules/00-master-agent.mdc` | Cursor 默认规则 |
| `.windsurfrules` | Windsurf 默认规则 |

---

## AI 工作原则

1. **先 TASK 后代码** — 无 `TASKS.md` 条目不改业务逻辑。
2. **Master 决策、Skill 执行** — Cursor 规划/审查；Windsurf/Codex 在 Scope 内执行。
3. **最小 Context** — 只加载任务相关文件；Skill 输出摘要回传 Master。
4. **小步可验证** — 每 TASK 有 Validation 命令。
5. **问题只记录或开 TASK** — 结构问题写 `REVIEW.md`，不在无关任务中偷改。
6. **不确定写 TODO/UNKNOWN** — 禁止编造模块或 API。

## 工具分工

| 工具 | 角色 | Skills |
| --- | --- | --- |
| **Cursor** | Master Agent / AI Tech Lead | Product, Architecture, Review（+ 规划/Debug 协调） |
| **Windsurf** | Feature 执行 | Frontend, Backend |
| **Codex** | Execution / DevOps | Test, Debug, Deployment, Documentation（机械更新） |

**老板模式：** Human 只验收里程碑与可运行结果；Master 按 `workflows/autonomous-delivery.md` 自主调度，**不向老板请示实现细节**。老板入口见 `docs/OWNER.md`。

Claude/GPT/未来 Agent：**绑定同一 Skill Prompt**，由 Master 调度，不新增自治角色。

## Context 管理规则

- Master 会话保留：当前 TASK、开放 REVIEW 项、ADR 索引。
- Skill 会话仅含：Scope 文件 + 验收标准 + 禁止项。
- 终端大日志用路径引用，不全文粘贴。
- 任务结束丢弃 Skill 细节，仅 5–10 行摘要写入 TASK Notes。

## 禁止事项

- 无 TASK 改业务代码 / 删文件 / 加 major 依赖
- 改 API 不同步 `docs/api.md` 与 frontend types
- 改 schema 无 Alembic 迁移与 rollback 说明
- 多 Skill 同时改同一文件
- 一次性全项目重构
- 绕过失败测试或隐藏已知问题
- 提交 secrets、`.env` 真实值

## 修改代码前

1. 确认 `TASKS.md` 条目（Goal、Scope、Owner Skill）
2. 读 `ARCHITECTURE.md` + 相关 `docs/`
3. 架构/契约变更 → 起草 `DECISIONS.md` ADR
4. 定义 Validation（Test Skill 命令）
5. 检查 git 状态，避免覆盖他人工作

## 修改代码后

1. 运行 Validation（Test Skill）
2. 更新文档（Documentation Skill：`docs/api.md` 等）
3. TASK → REVIEW → Review Skill → DONE
4. 未解风险 → `REVIEW.md` 或新 TASK

## 测试规则

```powershell
# Backend
cd backend
$env:PYTHONPATH="C:\Users\sanford\Desktop\ai_code_new\intel-hub"
python -m pytest tests/ -q

# Frontend
cd apps\web
npm run type-check
npm run build
```

E2E 浏览器：**TODO**。发布前见 `workflows/release-workflow.md`。

## Review 规则

- Review Skill 输出 P0/P1/P2 + Verdict（APPROVE / REQUEST_CHANGES / BLOCK）
- P0 必须修复；P1/P2 可转 TASK
- 流程见 `workflows/review-workflow.md`

## 文档规则

| 变更 | 更新 |
| --- | --- |
| 产品范围 | `docs/prd.md` |
| API | `docs/api.md` + types |
| 部署/命令 | `docs/deployment.md` |
| 架构细节 | `ARCHITECTURE.md`, `docs/architecture-details.md` |
| 决策 | `DECISIONS.md` |
| 风险 | `REVIEW.md` |

## Definition of Done

- [ ] 验收标准满足
- [ ] Validation PASS 或 BLOCKED 已记录
- [ ] 文档已同步
- [ ] Review APPROVE
- [ ] `TASKS.md` 已更新

## Legacy Prompts

`prompts/cursor-master.md`、`windsurf-feature-agent.md`、`codex-execution-agent.md`、`review-agent.md` 仍有效，映射见 `SKILLS.md`。
