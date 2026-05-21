# Source 统一数据模型（开发用）

```yaml
# sources 表 / OPML 导入字段
id: uuid
name: string              # 显示名
slug: string              # 唯一标识
type: enum                # rss | rest_api | webhook | scraper | opml | telegram | email | gdelt | acled | feed
category: enum            # wire | regional | official | financial | geopolitical | cyber | social | research | vertical | aggregator | maritime | compliance | humanitarian | china | thinktank
subcategory: string
region: string            # global | north-america | europe | middle-east | ...
language: string          # en | zh | ar | multi
url: string               # feed URL 或 API base
api_key_env: string       # 环境变量名，可空
poll_interval_minutes: int
tier: int                 # 0=商业版基线 1=扩展 2=全量
priority: int             # 1-10
enabled: bool
license_notes: string     # 版权/ToS 备注
tags: string[]
metadata: json            # 扩展配置
```

## type 说明

| type | 用途 |
|------|------|
| rss | RSS/Atom feed |
| rest_api | REST 新闻/数据 API |
| gdelt | GDELT 事件/新闻 |
| acled | 武装冲突数据 |
| webhook | 外部推送 |
| opml | 订阅包批量导入 |
