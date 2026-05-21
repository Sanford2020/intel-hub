# Intel Hub 数据源种子文件

| 文件 | 说明 |
|------|------|
| `all-sources.json` | 506 条结构化源（由 `scripts/parse-data-sources.py` 生成） |
| `all-sources.csv` | 同上，**可导入 Notion** |

## 导入 Notion（三选一）

### 方式 A — Cursor Notion 插件（推荐）

1. 在 Cursor 弹窗中点击 **Allow / 授权** Notion MCP（上次被跳过了）
2. 授权后告诉我，我会自动创建 **「Intel Hub — 情报数据源」** 数据库并写入 506 行

### 方式 B — CSV 手动导入（最快）

1. Notion 新建页面 → **Import** → **CSV**
2. 选择 `seeds/all-sources.csv`
3. 将首列 `name` 设为 **Title** 类型
4. 按需调整列类型（Tier → Select，Enabled → Checkbox，URL → URL）

### 方式 C — Notion API 脚本

1. [创建 Integration](https://www.notion.so/my-integrations) → 复制 token
2. 在 Notion 新建空白页 → **Connect to** 你的 Integration
3. 复制页面 ID（URL 中 32 位 hex）

```powershell
cd C:\Users\sanford\Desktop\ai_code_new\intel-hub
$env:NOTION_API_KEY = "secret_xxx"
$env:NOTION_PARENT_PAGE_ID = "页面ID"
python scripts/parse-data-sources.py
python scripts/sync-sources-to-notion.py
```

## 重新生成

```powershell
python scripts/parse-data-sources.py
```

文档更新后重新运行，再同步 Notion（脚本会按 `slug` 去重跳过已存在行）。
