# Test Skill

## 绑定工具

Codex

## 职责

- `python -m pytest tests/ -q`
- `npm run type-check` / `npm run build`
- `docker compose config`
- 解读失败、分类：环境 / 回归 / flaky

## 输出

```markdown
## Result: PASS | FAIL | BLOCKED
## Commands Run
## Key Output
## Failures (if any)
## Recommended Owner Skill for fix
```

## 禁止

- 不削弱断言通过 CI
- 不未授权改业务逻辑（FAIL 时交 Debug/Backend/Frontend Skill）

## 启动语

```
Test Skill：执行 TASK-[ID] 的 Validation 命令，输出 PASS/FAIL 与失败摘要。
```
