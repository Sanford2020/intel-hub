# Autonomous Delivery — 老板模式

Human（老板）只看**可运行的结果**与**里程碑摘要**。Cursor Master 负责规划、调度、Review、迭代，**不向老板请示实现细节**。

## 角色

| 角色 | 工具 | 职责 |
| --- | --- | --- |
| **老板** | 人 | 定方向（可选）；验收里程碑；配置 secrets（`.env`） |
| **Master** | Cursor | 拆 TASK、写 ADR、Review、合并方向、更新 TASKS/REVIEW |
| **Feature** | Windsurf | Backend / Frontend 实现（Scope 内） |
| **Execution** | Codex | Test、Deployment、文档机械同步、脚本 |

## Master 自主决策边界

**无需问老板：**

- TASK 拆分与优先级（P0/P1）
- Skill 分工与 Prompt 下发
- 测试 / Review / DONE 流转
- 文档、脚本、非 breaking 小修复
- 从 BACKLOG 拉入 Sprint 的 **M 级交付**（见下）

**必须记录、不阻塞交付：**

- 无 Auth 下的公网暴露风险 → `REVIEW.md`
- 商业 Auth / 多租户 → BACKLOG，除非老板明确要上线

**仅这些情况才找老板：**

- 需要真实密钥（`OPENAI_API_KEY`、`FEISHU_WEBHOOK_URL`）且未配置
- 不可逆生产操作（删库、force push、公网域名 DNS）
- 产品方向二选一且 ADR 无法消解（例如放弃 Platform 改做 Horizon 克隆）

## 里程碑（M）

| 里程碑 | 状态 | 老板可见结果 |
| --- | --- | --- |
| **M0** Platform MVP | DONE | 采集 / 文章 / AI / 告警 / Dashboard |
| **M1** Sticky Layer | DONE | `/briefing`、相关度精选、飞书推送链路 |
| **M2** Operator Closure | IN PROGRESS | 一键日报脚本、PRD 完整、老板一页纸 |
| **M3** Ops Hardening | BACKLOG | 源修复、24h Worker 观测、validate 全量 |
| **M4** Commercial | BACKLOG | Auth、限流、生产清单 |

## 标准迭代环（Master 自动跑）

```text
1. 从 BACKLOG 取 M2/M3 最高项 → TASKS.md TODO
2. Architecture（若需要）→ Windsurf 实现 → Codex Test
3. Review → DONE
4. 给老板：3 行摘要 + 怎么验（URL / 命令）
```

## 当前 Sprint（M2）

见 `TASKS.md` → DOING / TODO。Master 默认推进至 M2 DONE 后再开 M3。
