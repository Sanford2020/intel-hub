# Agent Roles

本文件定义多 agent 开发项目中的标准角色、职责边界、输入输出和验收口径。使用时可以按项目规模裁剪，但每个被启用的 agent 都必须有明确文件边界和交付物。

## 使用原则

- 一个 agent 只对自己声明的文件和模块负责。
- 一个任务只能有一个最终负责人，可以有多个咨询或评审角色。
- 角色不是职位，而是工作模式；同一个 agent 可以在不同时段切换角色，但必须重新声明范围。
- 所有角色都要产出可验证结果：文档、代码、测试、截图、日志、检查清单或风险结论。
- 如果角色之间发生边界冲突，先写接口或交接说明，再继续实现。

## 开工声明模板

每个 agent 开始前必须在任务说明或协作记录中写清：

```text
Role:
Goal:
Scope:
Files owned:
Files avoided:
Dependencies:
Expected output:
Verification:
Handoff target:
```

## 标准角色总览

| 角色 | 核心目标 | 典型负责内容 | 不应负责内容 |
| --- | --- | --- | --- |
| Product Agent | 把想法变成可验收需求 | 用户、场景、PRD、验收标准 | 未对齐技术方案时直接改架构 |
| Architect Agent | 定义系统边界和技术路线 | 模块划分、接口契约、数据流、风险 | 代替所有角色写完整实现 |
| Frontend Agent | 交付用户可操作界面 | 页面、组件、状态、交互、响应式 | 私自改后端 API 语义 |
| Backend Agent | 交付稳定服务能力 | API、数据库、鉴权、业务逻辑、任务 | 私自改产品验收口径 |
| QA Agent | 证明系统可用并暴露风险 | 测试计划、用例、回归、缺陷记录 | 在未授权时大规模重构 |
| Release Agent | 让项目可部署、可运行、可交付 | 环境、构建、部署、配置、发布说明 | 改动核心业务逻辑 |
| Documentation Agent | 让项目可理解、可复用 | README、操作手册、ADR、示例 | 替代 QA 做质量判断 |
| Integration Agent | 合并多角色产物 | 接口对接、冲突处理、端到端串联 | 无视原角色边界直接覆盖 |

## Product Agent

### 目标

把模糊想法转化为可拆解、可验收、可交付的产品定义。

### 输入

- 用户原始需求、业务背景、竞品或参考案例。
- 当前项目状态、技术限制、时间限制。
- 已有 PRD、用户故事、任务清单或反馈。

### 输出

- 项目目标和非目标。
- 用户画像和核心使用场景。
- 功能范围、优先级、验收标准。
- 关键流程、异常场景、空状态和错误提示要求。
- 需要技术角色判断的问题清单。

### 文件边界示例

```text
Files owned:
- PROJECT_BRIEF.md
- docs/PRD.md
- templates/PRD_TO_TASKS.md 的实例副本

Files avoided:
- src/**
- migrations/**
- deployment/**
```

### 完成标准

- 每个需求都能回答：谁使用、解决什么问题、成功标准是什么。
- 每个功能都有明确的验收方式。
- 明确说明本轮不做什么。
- 技术不确定项已交给 Architect 或对应 Builder。

## Architect Agent

### 目标

把需求拆成稳定的模块边界和可并行执行的技术方案。

### 输入

- Product Agent 的需求和验收标准。
- 现有代码结构、依赖、运行方式。
- 技术约束、部署目标、性能和安全要求。

### 输出

- 系统模块图或文字版模块说明。
- API、事件、数据模型、权限边界。
- 任务拆分和文件所有权建议。
- 风险清单和需要先验证的技术假设。
- 架构决策记录，必要时使用 ADR。

### 文件边界示例

```text
Files owned:
- docs/ARCHITECTURE.md
- docs/API_CONTRACT.md
- standards/PROJECT_STRUCTURE.md

Files avoided:
- 具体页面实现文件，除非任务明确授权
- 具体业务测试文件，除非任务明确授权
```

### 完成标准

- 前端、后端、测试角色能基于方案并行开工。
- 关键接口有字段、错误码、权限和状态说明。
- 对高风险决策给出备选方案或降级方案。
- 没有留下“大家自己看着办”的共享边界。

## Frontend Agent

### 目标

交付符合产品目标、接口契约和质量标准的用户界面。

### 输入

- PRD、用户流程、页面清单、设计参考。
- API 契约、数据结构、错误状态。
- 项目现有组件库、样式规范和路由结构。

### 输出

- 页面、组件、状态管理和交互逻辑。
- 加载、空状态、错误状态和权限状态。
- 响应式布局和基础可访问性处理。
- 前端验证结果：截图、交互检查、单元测试或端到端测试。

### 文件边界示例

```text
Files owned:
- src/pages/**
- src/components/**
- src/styles/**
- frontend/**

Files avoided:
- backend/**
- database/migrations/**
- docs/API_CONTRACT.md，除非只补充前端发现的问题
```

### 完成标准

- 用户能完成 PRD 中的核心路径。
- 页面在主要桌面和移动宽度下不溢出、不遮挡。
- API 错误、空数据、加载中都有明确呈现。
- 未完成项以 TODO 或交接说明记录，不伪装完成。

## Backend Agent

### 目标

交付可靠、清晰、可测试的服务端能力。

### 输入

- API 契约、数据模型、权限规则。
- 业务流程和异常场景。
- 现有数据库、服务框架、环境变量约定。

### 输出

- API 路由、服务层、数据访问、迁移脚本。
- 输入校验、错误处理、鉴权和权限检查。
- 后端测试、接口示例和运行说明。
- 对前端可用的字段和错误语义说明。

### 文件边界示例

```text
Files owned:
- backend/**
- server/**
- api/**
- database/migrations/**
- docs/API_CONTRACT.md 的接口实现状态部分

Files avoided:
- src/pages/**
- src/components/**
- 产品验收标准，除非反馈实现风险
```

### 完成标准

- 接口符合契约，字段命名和错误语义稳定。
- 关键路径有测试或可复现验证命令。
- 数据迁移可重复执行或有清晰回滚说明。
- 环境变量、启动命令和依赖已记录。

## QA Agent

### 目标

通过测试和审查证明项目是否达到可交付标准，并明确剩余风险。

### 输入

- PRD 验收标准。
- 架构和接口契约。
- 前后端交付物、运行说明、已知风险。

### 输出

- 测试计划和测试用例。
- 自动化测试、手工测试记录或缺陷清单。
- 回归范围、阻塞问题和发布建议。
- 未覆盖风险说明。

### 文件边界示例

```text
Files owned:
- tests/**
- e2e/**
- checklists/**
- docs/QA_REPORT.md

Files avoided:
- 大规模重写业务实现
- 修改 PRD 验收口径
```

### 完成标准

- 覆盖核心成功路径、失败路径和边界条件。
- 每个严重缺陷都有复现步骤、期望结果、实际结果。
- 明确区分阻塞问题和可接受风险。
- 给出发布建议：通过、带风险通过或不建议发布。

## Release Agent

### 目标

让项目可以被稳定构建、配置、部署、回滚和交付。

### 输入

- 已完成的代码和文档。
- 环境变量清单、部署目标、域名或运行环境。
- QA 结果和待发布版本范围。

### 输出

- 构建脚本、部署脚本、环境配置说明。
- 发布检查清单、版本说明、回滚方案。
- 运行健康检查和基础监控建议。
- 最终交付包说明。

### 文件边界示例

```text
Files owned:
- deployment/**
- scripts/**
- .env.example
- docs/RELEASE_NOTES.md
- docs/RUNBOOK.md

Files avoided:
- 未经授权修改核心产品逻辑
- 未经确认改动数据库生产结构
```

### 完成标准

- 新成员可以按文档启动项目。
- 构建和部署命令可执行。
- 环境变量有用途、示例值和保密说明。
- 发布风险和回滚步骤写清楚。

## Documentation Agent

### 目标

让项目知识可查、可复用、可交接。

### 输入

- 已有 README、PRD、架构说明、代码结构。
- 各角色交接记录和验证结果。
- 用户常见问题或部署使用反馈。

### 输出

- README、快速开始、开发指南、用户指南。
- ADR、FAQ、术语表、示例项目说明。
- 文档索引和维护规则。

### 文件边界示例

```text
Files owned:
- README.md
- START_HERE.md
- docs/**
- examples/**

Files avoided:
- src/**
- backend/**
- tests/**，除非补充说明性示例
```

### 完成标准

- 文档能回答如何启动、如何开发、如何验证、如何发布。
- 链接、命令、路径与实际项目一致。
- 重要决策有来源和日期。
- 文档不掩盖未完成或有风险的内容。

## Integration Agent

### 目标

把多个角色的产物合并成一致、可运行、可验证的整体。

### 输入

- 各角色 handoff。
- 已变更文件列表。
- 测试结果、接口契约和冲突说明。

### 输出

- 合并后的项目状态。
- 冲突解决记录。
- 端到端验证结果。
- 仍需原角色处理的问题清单。

### 文件边界示例

```text
Files owned:
- 跨模块集成文件
- docs/INTEGRATION_REPORT.md
- 必要的配置和入口文件

Files avoided:
- 未理解业务语义时重写单一角色的核心实现
```

### 完成标准

- 项目能从入口流程跑通。
- 前后端字段、状态和错误处理一致。
- 所有冲突解决都有说明。
- 剩余问题已分配给具体角色。

## 推荐编组

### 3 Agent MVP

```text
Agent A: Architect / Product
Agent B: Frontend / Backend Builder
Agent C: QA / Release
```

适合范围小、交付快、接口简单的项目。

### 5 Agent 标准项目

```text
Agent A: Product Agent
Agent B: Architect Agent
Agent C: Frontend Agent
Agent D: Backend Agent
Agent E: QA / Release Agent
```

适合完整 Web App、SaaS、内部工具、API 服务。

### 7 Agent 并行项目

```text
Agent A: Product Agent
Agent B: Architect Agent
Agent C: Frontend Agent
Agent D: Backend Agent
Agent E: QA Agent
Agent F: Release Agent
Agent G: Documentation / Integration Agent
```

适合模块多、多人并行、需要持续交接的项目。

## 角色冲突处理

当两个 agent 都需要修改同一文件时，按以下顺序处理：

1. 判断是否可以拆分为不同文件、配置或接口文档。
2. 如果必须修改同一文件，指定一个 owner，另一个 agent 提供 patch 建议或交接说明。
3. owner 合并后在 handoff 中说明采纳了什么、没有采纳什么。
4. QA 或 Integration Agent 验证冲突区域。

## 角色切换规则

agent 可以切换角色，但必须重新声明：

```text
Previous role:
New role:
Reason:
New files owned:
Files no longer touched:
Handoff from previous work:
```

未声明角色切换时，默认仍受原文件边界约束。
