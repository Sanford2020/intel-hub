# Review Skill

## 绑定工具

Cursor / 独立 Review 会话

## 检查项

1. **功能符合性** vs TASK 验收标准
2. **架构一致性** vs `ARCHITECTURE.md` / ADR
3. **重复代码 / 技术债**
4. **安全**：secrets、SSRF（RSS URL）、webhook
5. **性能**：N+1、阻塞 ingest、分页
6. **可维护性**：命名、模块边界、测试

## Verdict

`APPROVE` | `REQUEST_CHANGES` | `BLOCK`

## 输出格式

```markdown
### [P0|P1|P2] Title
- File:
- Issue:
- Suggestion:
```

## 禁止

- Review 中大规模重写（开新 TASK）

## 启动语

```
Review Skill：审查 TASK-[ID] diff。P0/P1/P2 + Verdict。不改代码。
```
