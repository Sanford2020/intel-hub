# Handoff Protocol

本文件定义多 agent 项目中的交接格式。任何暂停、完成、转交、等待依赖、合并前或发布前，都应留下 handoff，确保下一个 agent 能继续工作而不用重新猜上下文。

## 何时必须交接

- 完成一个任务后。
- 暂停工作超过一个协作周期。
- 需要另一个 agent 接手。
- 遇到阻塞并需要决策或依赖。
- 修改了共享文件或接口契约。
- 合并、发布或 QA 前。
- 发现风险但暂时不处理。

## 最小交接格式

```text
Done:
Changed:
Verified:
Risks:
Next:
```

适合小任务、纯文档修改、单文件修改。

## 标准交接格式

```text
Handoff ID:
From:
To:
Role:
Task:
Status:

Goal:

Done:

Changed files:

Decisions:

Verified:

Not verified:

Risks:

Blockers:

Next steps:

Suggested owner:

Notes:
```

## 字段说明

### Handoff ID

推荐格式：

```text
YYYYMMDD-HHMM-role-task
```

示例：

```text
20260519-1930-frontend-dashboard
```

### From / To

写清交接来源和目标。如果还没有明确接手对象，写 `Next available owner`。

### Role

使用 `docs/AGENT_ROLES.md` 中的角色名，例如：

```text
Frontend Agent
Backend Agent
QA Agent
Release Agent
```

### Task

写具体任务，不写泛泛描述。

推荐：

```text
Implement user login API according to docs/API_CONTRACT.md
```

不推荐：

```text
Backend work
```

### Status

只能使用：

```text
Todo
Claimed
In Progress
Blocked
Ready for Review
Changes Requested
Verified
Done
```

### Goal

说明这次任务原本要达成什么。

### Done

列出已经完成的事实，不写计划。

示例：

```text
Done:
- Added login form with email and password validation.
- Connected submit action to POST /api/auth/login.
- Added empty, loading and error states.
```

### Changed files

列出所有改动路径，并简述改动原因。

示例：

```text
Changed files:
- src/pages/Login.tsx: added login page UI and submit flow.
- src/api/auth.ts: added login client function.
- docs/API_CONTRACT.md: documented frontend assumptions for auth errors.
```

### Decisions

记录过程中做出的取舍，尤其是别人接手时必须知道的内容。

示例：

```text
Decisions:
- Kept password reset out of scope for this iteration.
- Used existing Button component instead of adding a new form library.
```

### Verified

记录已完成的验证。

示例：

```text
Verified:
- Command: npm run lint
  Result: passed
- Manual: submitted invalid email and saw validation message
  Result: passed
```

### Not verified

记录没有验证的内容和原因。

示例：

```text
Not verified:
- Backend login success response was not verified.
  Reason: backend endpoint is not implemented yet.
  Risk: frontend field mapping may need adjustment.
```

### Risks

写剩余风险，不要把风险藏在备注里。

示例：

```text
Risks:
- API error code names are still provisional.
- Mobile layout below 360px has not been checked.
```

### Blockers

如果状态是 `Blocked`，必须填写。

```text
Blockers:
- Need final auth response contract from Backend Agent.
- Need DATABASE_URL to run integration tests.
```

### Next steps

写可执行动作，并尽量指定 owner。

示例：

```text
Next steps:
- Backend Agent: implement POST /api/auth/login.
- QA Agent: verify invalid credentials and locked account cases.
- Frontend Agent: update field mapping if backend changes response shape.
```

### Suggested owner

明确下一个最适合接手的角色。

```text
Suggested owner:
Backend Agent
```

### Notes

只放补充背景，不放关键风险和阻塞。

## 交接类型

### 完成型交接

用于任务已完成并等待 review 或集成。

```text
Handoff ID:
From:
To:
Role:
Task:
Status: Ready for Review

Goal:

Done:

Changed files:

Verified:

Risks:

Next steps:
```

### 阻塞型交接

用于任务无法继续。

```text
Handoff ID:
From:
To:
Role:
Task:
Status: Blocked

Goal:

Done before blocked:

Changed files:

Blocked by:

Impact:

Tried:

Need from:

Fallback:

Next steps:
```

### 接口变更交接

用于 API、事件、数据模型、配置字段等共享契约变化。

```text
Handoff ID:
From:
To:
Role:
Task:
Status:

Contract changed:

Before:

After:

Affected files:

Affected agents:

Migration or compatibility notes:

Verification:

Required follow-up:
```

### QA 交接

用于测试完成、发现缺陷或发布建议。

```text
Handoff ID:
From:
To:
Role: QA Agent
Task:
Status:

Test scope:

Tested:

Passed:

Failed:

Defects:

Regression risk:

Release recommendation:

Next steps:
```

发布建议只能使用：

```text
Pass
Pass with risks
Do not release
Blocked
```

### Release 交接

用于部署、发布、交付前后。

```text
Handoff ID:
From:
To:
Role: Release Agent
Task:
Status:

Build:

Environment:

Deployment:

Config changes:

Release notes:

Rollback:

Known risks:

Next steps:
```

## 交接质量检查

提交 handoff 前检查：

- 是否列出了所有改动文件。
- 是否区分了已验证和未验证。
- 是否写明风险和阻塞。
- 是否给出下一步 owner。
- 是否避免了“差不多”“应该可以”等模糊词。
- 是否能让下一个 agent 不读完整聊天记录也能继续。

## 示例：前端到后端

```text
Handoff ID: 20260519-2015-frontend-auth
From: Agent C
To: Backend Agent
Role: Frontend Agent
Task: Build login page against provisional auth contract
Status: Ready for Review

Goal:
Create a login UI that can call the planned auth endpoint.

Done:
- Added login form with email and password validation.
- Added loading, invalid input and server error states.
- Added auth client function using POST /api/auth/login.

Changed files:
- src/pages/Login.tsx: login page UI and submit flow.
- src/api/auth.ts: auth request helper.
- docs/API_CONTRACT.md: provisional auth request and response shape.

Decisions:
- Password reset is out of scope for this iteration.
- Frontend expects error.code and error.message from backend.

Verified:
- Manual: invalid email shows validation message.
  Result: passed
- Command: npm run lint
  Result: passed

Not verified:
- Successful login with real backend.
  Reason: endpoint is not implemented yet.
  Risk: response field names may change.

Risks:
- Backend must confirm token field name before QA.

Next steps:
- Backend Agent: implement POST /api/auth/login using the documented shape.
- QA Agent: test invalid credentials, locked account and successful login after backend is ready.

Suggested owner:
Backend Agent
```

## 示例：后端到 QA

```text
Handoff ID: 20260519-2130-backend-auth
From: Agent D
To: QA Agent
Role: Backend Agent
Task: Implement login endpoint
Status: Ready for Review

Goal:
Provide POST /api/auth/login for the frontend login page.

Done:
- Added POST /api/auth/login.
- Added password verification and disabled-user check.
- Added structured error responses.

Changed files:
- backend/routes/auth.ts: login endpoint.
- backend/services/authService.ts: credential verification.
- tests/auth/login.test.ts: login success and failure tests.

Verified:
- Command: npm test -- auth/login.test.ts
  Result: passed
- Manual: called endpoint with invalid password
  Result: returned 401 INVALID_CREDENTIALS

Not verified:
- Production email login rate limits.
  Reason: rate limit middleware is planned but not added.

Risks:
- Brute-force protection is not complete.

Next steps:
- QA Agent: run end-to-end login flow with frontend.
- Architect Agent: decide whether rate limiting is required before MVP release.

Suggested owner:
QA Agent
```

## 示例：阻塞

```text
Handoff ID: 20260519-2200-release-env
From: Agent F
To: Architect Agent
Role: Release Agent
Task: Prepare staging deployment
Status: Blocked

Goal:
Deploy current build to staging.

Done before blocked:
- Confirmed build command.
- Added .env.example entries for public frontend variables.

Changed files:
- .env.example: added documented frontend variables.
- docs/RUNBOOK.md: added draft staging deployment steps.

Blocked by:
- Missing database connection string for staging.

Impact:
- Cannot verify backend startup or migrations in staging.

Tried:
- Checked README and deployment docs.
- Checked local environment examples.

Need from:
- Project owner or Backend Agent to provide staging DATABASE_URL.

Fallback:
- Can deploy frontend-only preview without backend verification.

Next steps:
- Backend Agent: confirm staging database provisioning.
- Release Agent: rerun deployment after env is available.
```

## 存放建议

小项目可以把 handoff 写在任务卡底部。

中大型项目建议建立：

```text
docs/handoffs/
  20260519-2015-frontend-auth.md
  20260519-2130-backend-auth.md
```

如果项目使用 issue 或项目管理工具，也可以把 handoff 贴到对应任务评论中，但必须保持字段完整。
