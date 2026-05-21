# Debug Skill

## 绑定工具

Codex（首选）、Cursor（复杂定位）

## 流程

1. **复现**：环境、步骤、期望 vs 实际
2. **定位**：最小文件/函数范围
3. **最小修复**：单 TASK 单根因
4. **验证**：相关 pytest / 手动步骤
5. **记录**：`TASKS.md`、`REVIEW.md` 或 ADR

## 禁止

- 不顺手重构
- 不绕过测试
- 不未定位就大改

## Intel Hub 常见入口

- API 超时 → 同步 ingest 阻塞
- 无文章 → Worker/Beat、RSS URL
- 无报告 → analyze 任务注册、OPENAI_API_KEY

## 启动语

```
Debug Skill：复现并定位 [问题描述]。最小修复 + 验证命令。记录根因。
```
