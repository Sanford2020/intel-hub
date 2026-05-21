# Frontend Skill

## 绑定工具

Windsurf（首选）

## 职责

- `apps/web/` 页面与组件
- `apps/web/src/lib/intel-api.ts` 与 types 同步
- UI 状态：loading、error、分页、筛选

## 范围

| 允许 | 禁止 |
| --- | --- |
| `apps/web/**` | `backend/**` |
| 前端测试 | 数据库 / Alembic |
| 样式与交互 | 无关重构 |

## 完成后输出

- 修改文件列表
- 风险说明
- 验证：`npm run type-check`、`npm run build`

## 启动语

```
Frontend Skill：仅实现 TASK-[ID] 中 apps/web 范围。禁止改 backend。完成后列出文件与验证命令。
```
