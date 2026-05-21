# SKILLS.md — Skill System Definition

Intel Hub 采用 **Single Master Agent + Multiple Skills** 架构，避免多自治 Agent 互相覆盖、Context 失控。

## Skill ≠ Agent

| 概念 | 定义 |
| --- | --- |
| **Master Agent** | 唯一决策者：Cursor（AI Tech Lead） |
| **Skill** | 可复用的能力模块 + Prompt + 约束边界 |
| **Tool Binding** | Skill 由 Cursor 调度，在 Windsurf/Codex 等工具上执行 |

Skill 不是独立人格；Skill 是 **受 Master 分配、范围受限的工作模式**。

## Skill 生命周期

```text
Master 读 TASKS.md
  → 选择 Skill
  → 注入 Scope + Context（最小必要文件）
  → 执行（Windsurf/Codex/Claude…）
  → 输出结构化结果
  → Master Review
  → 更新 TASKS / DECISIONS / docs
  → Skill 上下文丢弃（不污染 Master Context）
```

## Skill 输入 / 输出

| 阶段 | 输入 | 输出 |
| --- | --- | --- |
| 分配 | TASK 条目、Scope、禁止项 | — |
| 执行 | 相关文件路径、验收标准 | 改动 diff / 命令日志 / Review 报告 |
| 收尾 | 验证结果 | TASK 状态、文档 patch 建议 |

## Skill 协作规则

1. **一次一个 Skill 活跃**于同一 TASK（除非 Master 显式并行且文件不重叠）。
2. **Frontend Skill 不碰 Backend**；**Backend Skill 不碰 UI**（Debug/Test 除外）。
3. 跨层改动必须由 **Architecture Skill + Master ADR** 批准。
4. Skill 不得自行扩展 Scope；阻塞则返回 Master，写入 `TASKS.md` → BLOCKED。

## 避免 Context 污染

- Master 只保留：TASK 摘要、ADR 索引、REVIEW 开放项。
- Skill 会话只加载任务相关文件，不加载全仓库。
- 长日志放终端/文件引用，不粘贴进 Master 首轮 Context。
- 完成后用 **5 行摘要** 回传 Master，而非完整对话。

---

## Skill Catalog

| Skill | 绑定工具 | Prompt | 职责 |
| --- | --- | --- | --- |
| Product Skill | Cursor / 人类 | `prompts/skill-product.md` | PRD、范围、优先级、验收定义 |
| Architecture Skill | Cursor | `prompts/skill-architecture.md` | 模块边界、数据流、ADR |
| Frontend Skill | Windsurf | `prompts/skill-frontend.md` | Next.js UI、页面、前端 API 封装 |
| Backend Skill | Windsurf | `prompts/skill-backend.md` | FastAPI、模块、Worker、Schema |
| Debug Skill | Codex / Cursor | `prompts/skill-debug.md` | 复现、定位、最小修复 |
| Test Skill | Codex | `prompts/skill-test.md` | pytest、type-check、build、e2e |
| Review Skill | Cursor / 专用 Review | `prompts/skill-review.md` | 功能/架构/安全/性能审查 |
| Documentation Skill | Codex / Cursor | `prompts/skill-documentation.md` | api/deployment/prd 同步 |
| Deployment Skill | Codex | `prompts/skill-deployment.md` | Docker、迁移、环境、发布 |

## Legacy Prompts（保留，不删除）

早期 Agent 命名 Prompt 仍可用，由 Master 映射到 Skill：

| Legacy | Maps To |
| --- | --- |
| `prompts/cursor-master.md` | Master Agent |
| `prompts/windsurf-feature-agent.md` | Frontend + Backend Skill |
| `prompts/codex-execution-agent.md` | Test + Debug + Deployment Skill |
| `prompts/review-agent.md` | Review Skill |

## Master Agent Prompt

见 `prompts/master-agent.md` 与 `.cursor/rules/00-master-agent.mdc`。
