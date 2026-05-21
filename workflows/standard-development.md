# Standard Development Workflow

Single Master Agent + Skills。详见 `SKILLS.md`。

## 流程

```text
Cursor Master 规划（Product / Architecture Skill）
  → 写入 TASKS.md
  → Windsurf 执行 Frontend / Backend Skill
  → Codex 执行 Test / Debug / Deployment Skill
  → Cursor Master + Review Skill 审查
  → Documentation Skill 更新 docs
  → 更新 TASKS.md / DECISIONS.md
  → DONE
```

## 门禁

- [ ] TASK 有 Goal、Scope、Owner Skill、Validation
- [ ] 相关测试 PASS 或 BLOCKED 已记录
- [ ] `docs/api.md` 等已同步（如适用）
- [ ] Review Verdict = APPROVE
- [ ] 无未处理 P0

## 相关文件

- `AGENTS.md` — 全局规则
- `workflows/debug-workflow.md`
- `workflows/review-workflow.md`
- `workflows/release-workflow.md`

## Legacy

旧文件名 `standard-dev-workflow.md` 内容与本文件等价，保留不删。
