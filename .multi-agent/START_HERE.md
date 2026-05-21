# Start Here

用这份清单启动一个多 agent 开发项目。

## 1. 填项目简报

复制 `templates/PROJECT_BRIEF.md` 到项目根目录，命名为 `PROJECT_BRIEF.md`。

必须填清楚：

- 项目一句话目标。
- 目标用户。
- 这次迭代要交付什么。
- 这次迭代不做什么。
- 如何判断完成。

## 2. 切任务边界

用 `templates/PRD_TO_TASKS.md` 把需求拆成任务。每个任务必须具备：

- 单一负责人。
- 明确输入。
- 明确输出。
- 文件或模块边界。
- 验收方式。

## 3. 分配 agent

参考 `docs/AGENT_ROLES.md` 选择 agent 组合。

推荐默认组合：

```text
Agent A: Architect / Planner
Agent B: Builder
Agent C: Verifier
```

## 4. 开工前对齐

每个 agent 开工前写清：

```text
Role:
Scope:
Files owned:
Files avoided:
Dependencies:
Expected output:
```

## 5. 合并前检查

运行：

```powershell
.\scripts\validate_project.ps1 -ProjectRoot "C:\path\to\project"
```

再按下面文档人工验收：

- `checklists/REVIEW_CHECKLIST.md`
- `checklists/DEFINITION_OF_DONE.md`
- `standards/QUALITY_GATES.md`

## 6. 交接

任何暂停、转交、合并前，都使用 `docs/HANDOFF_PROTOCOL.md` 的格式。

最小交接格式：

```text
Done:
Changed:
Verified:
Risks:
Next:
```
