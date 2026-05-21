# Collaboration Protocol

本文件定义多 agent 并行开发时的协作规则，目标是减少覆盖、重复劳动、接口漂移和“看起来完成但无法交付”的问题。

## 核心原则

- 先定边界，再写内容。
- 先对齐接口，再并行实现。
- 每次改动都能说清输入、输出、验证方式。
- 不删除他人内容，不覆盖未理解的改动。
- 发现冲突先暂停相关文件修改，再通过 handoff 或 owner 决策处理。
- 交付以可运行、可检查、可复现为准，不以描述为准。

## 协作生命周期

```text
Brief -> Plan -> Claim -> Build -> Verify -> Handoff -> Integrate -> Release
```

### 1. Brief

项目启动时必须明确：

- 项目目标。
- 本轮迭代范围。
- 非目标。
- 目标用户。
- 交付物。
- 验收标准。
- 时间或资源限制。

推荐使用 `templates/PROJECT_BRIEF.md`。

### 2. Plan

拆分任务时，每个任务必须包含：

- 任务名称。
- 单一 owner。
- 输入材料。
- 输出结果。
- 文件或目录边界。
- 依赖对象。
- 验收方式。

推荐使用 `templates/PRD_TO_TASKS.md` 和 `templates/TASK_CARD.md`。

### 3. Claim

agent 开工前必须声明自己的占用范围：

```text
Agent:
Role:
Task:
Files owned:
Files avoided:
Expected changes:
Expected verification:
Dependencies:
```

如果发现文件已被其他 agent 占用，不要并行编辑同一位置。应选择以下方案之一：

- 改为编辑接口文档或说明文件。
- 请求该文件 owner 合并你的建议。
- 等待对方 handoff 后再接手。
- 将任务拆成更小边界。

### 4. Build

实现期间遵守：

- 只修改自己声明范围内的文件。
- 保留现有内容，除非任务明确要求替换。
- 新增结构要符合项目已有命名和目录习惯。
- 对外部接口变更必须同步到接口文档。
- 对测试、构建、部署有影响的改动必须写入验证说明。

### 5. Verify

完成前至少做一种验证：

- 阅读校验：文档结构、链接、路径、命名一致。
- 静态校验：lint、typecheck、格式检查。
- 单元测试：覆盖核心函数或组件。
- 集成测试：验证接口、页面、数据库协同。
- 手工测试：记录操作步骤和结果。
- 构建验证：确认项目可以 build 或启动。

验证结果必须包含命令或检查方式：

```text
Verified:
- Command: npm test
  Result: passed
- Manual: opened /dashboard and completed create flow
  Result: passed
```

如果无法验证，必须写明原因：

```text
Not verified:
- Reason: missing DATABASE_URL in local environment
- Risk: backend persistence flow not confirmed
```

### 6. Handoff

任何暂停、完成、转交、等待依赖、合并前，都必须使用 `docs/HANDOFF_PROTOCOL.md`。

最小格式：

```text
Done:
Changed:
Verified:
Risks:
Next:
```

### 7. Integrate

集成时关注：

- 文件冲突是否已解决。
- API 字段是否与前端使用一致。
- 数据库迁移是否与代码匹配。
- 文档命令是否可执行。
- 测试是否覆盖合并后的关键路径。
- 未完成项是否有 owner。

### 8. Release

发布前必须完成：

- Definition of Done 检查。
- Review Checklist 检查。
- Quality Gates 检查。
- Release notes 或变更摘要。
- 已知风险和回滚方式。

## 文件所有权规则

### 单 owner 规则

同一时间，一个文件只能有一个主要 owner。其他 agent 可以：

- 读取该文件。
- 在 handoff 中提出修改建议。
- 新建配套文件。
- 等 owner 完成交接后接手。

### 共享文件规则

以下文件经常被多个角色需要，应更加谨慎：

```text
README.md
package.json
.env.example
docs/API_CONTRACT.md
docs/ARCHITECTURE.md
database/migrations/**
src/routes/**
src/app/**
```

修改共享文件前必须说明：

```text
Shared file:
Why change is needed:
Affected agents:
Compatibility risk:
Verification:
```

### 禁止行为

- 删除他人刚写的内容。
- 为了让自己任务通过而降低验收标准。
- 未声明就改动共享配置。
- 在未理解上下文时批量格式化整个项目。
- 把失败验证写成通过。
- 用“应该可以”替代实际验证结果。

## 接口协作规则

前端和后端并行时，先建立接口契约。

### API 契约必须包含

```text
Endpoint:
Method:
Auth:
Request params:
Request body:
Response success:
Response error:
Status codes:
Empty state:
Permission rules:
Example:
Owner:
Last updated:
```

### 接口变更流程

1. 提出变更原因。
2. 更新契约文档。
3. 标注受影响页面、测试和调用方。
4. 后端实现或调整。
5. 前端同步调用。
6. QA 验证成功和失败路径。

未经契约更新，不应让前端或后端单方面改变字段含义。

## 任务状态标准

任务只能使用以下状态：

| 状态 | 含义 |
| --- | --- |
| Todo | 已定义，未开始 |
| Claimed | 已被 agent 占用 |
| In Progress | 正在实现 |
| Blocked | 被依赖、权限、环境或决策阻塞 |
| Ready for Review | 已完成自测，等待审查 |
| Changes Requested | 审查后需要修改 |
| Verified | 已通过指定验证 |
| Done | 已集成并满足验收 |

状态变化必须附带一句原因。

## 阻塞处理

agent 遇到阻塞时，不应静默等待。必须记录：

```text
Blocked by:
Impact:
Tried:
Need from:
Fallback:
```

如果阻塞不影响其他独立文件，可以继续处理未阻塞部分，但 handoff 中必须说明哪些未完成。

## 决策记录

对以下事项应写决策记录：

- 技术栈选择。
- 数据库结构重要变化。
- 鉴权和权限模型。
- 关键第三方服务。
- 放弃某个功能或延期。
- 与 PRD 不一致的实现取舍。

推荐格式：

```text
Decision:
Context:
Options considered:
Chosen option:
Consequences:
Owner:
Date:
```

## Review 规则

review 优先看风险，不优先夸完成度。

必须检查：

- 是否满足需求验收标准。
- 是否超出文件边界。
- 是否破坏已有行为。
- 是否有测试或验证记录。
- 是否引入安全、权限、数据丢失风险。
- 是否有清晰交接。

review 结论使用：

```text
Approved
Approved with risks
Changes requested
Blocked
```

## 多 agent 日常节奏

### 短任务节奏

```text
1. 读 brief 和任务卡。
2. 声明 role 与 file ownership。
3. 实现最小可交付范围。
4. 自测。
5. handoff。
```

### 长任务节奏

```text
1. 每 30-60 分钟更新状态。
2. 完成一个可验证子任务就记录一次。
3. 发现接口变化立即同步。
4. 被阻塞超过 15 分钟就写 blocked note。
5. 结束前整理 changed / verified / risks / next。
```

## 冲突处理流程

当发现多人修改同一文件或同一接口语义冲突：

1. 停止继续扩大冲突。
2. 确认当前 owner。
3. 对比各自目标，不直接覆盖。
4. 由 owner 选择合并方案。
5. QA 或 Integration Agent 验证冲突区域。
6. 在 handoff 中记录解决方式。

记录模板：

```text
Conflict:
Files:
Agents involved:
Owner:
Resolution:
Verification:
Remaining risk:
```

## 完成定义

一个 agent 的任务完成必须同时满足：

- 声明范围内的输出已完成。
- 修改文件列表清楚。
- 已运行或说明无法运行的验证。
- 已知风险写明。
- 下一步 owner 清楚。
- 没有留下未声明的跨边界改动。

一个项目迭代完成必须同时满足：

- Product 验收标准通过或有明确豁免。
- Architect 确认模块边界没有重大漂移。
- Builder 完成核心实现。
- QA 给出通过或带风险通过结论。
- Release 确认可启动、可配置、可交付。
- Documentation 更新启动、使用、验证说明。
