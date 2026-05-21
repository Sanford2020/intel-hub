# 采集优先级矩阵

## Tier 0 — 商业基线（~80 源，Sprint 1–2）

| 类别 | 数量 | 接入方式 |
|------|------|----------|
| 全球通讯社/主流 RSS | 25 | rss |
| 地缘/防务 RSS | 15 | rss |
| 智库 RSS | 10 | rss |
| 科技/安全 RSS | 15 | rss |
| 新闻 API | 2 | rest_api (NewsAPI + GNews) |
| 政府官方 RSS | 10 | rss |
| GDELT | 1 | rest_api |

## Tier 1 — 扩展（+220 源，Sprint 3–5）

- 分洲媒体、财经 API、中国/亚太、垂直行业
- Event Registry、Reddit、部分 Telegram 频道
- FRED、SEC EDGAR、OpenSanctions

## Tier 2 — 全量（+500 源）

- 社交 API、OSINT 全量、海事/航空、卫星
- 付费通讯社 API、垂直数据库
- 多语言本地媒体长尾

## 开发顺序

```
Sprint 1: Source 表 + OPML 导入 + Tier 0 清单录入
Sprint 2: RSS 采集 Worker（Tier 0）
Sprint 3: NewsAPI/GNews + GDELT
Sprint 4: 分洲/垂直扩展（Tier 1）
Sprint 5: OSINT/社交/海事（Tier 2 按需）
```
