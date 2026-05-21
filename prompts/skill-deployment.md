# Deployment Skill

## 绑定工具

Codex

## 职责

- Docker Compose、镜像构建
- Alembic `upgrade head`
- Worker/Beat 进程启动验证
- 环境变量检查（`.env.example` 对照）

## 参考

- `docs/deployment.md`
- `workflows/release-workflow.md`

## 禁止

- 不修改生产 secrets 入库
- 不 force push / 破坏性 git 操作

## 常用命令

见 `prompts/codex-execution-agent.md` 或 `docs/deployment.md`。

## 启动语

```
Deployment Skill：按 docs/deployment.md 验证 [环境/发布步骤]，输出检查结果与 BLOCKED 项。
```
