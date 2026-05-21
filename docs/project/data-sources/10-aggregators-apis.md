# 10 — 聚合器、API 与元数据源

## 新闻聚合 API

| name | url | tier | 免费额度 | notes |
|------|-----|------|----------|-------|
| NewsAPI.org | https://newsapi.org/ | 0 | 100 req/day dev | 80k+ 源 |
| GNews | https://gnews.io/ | 0 | 100 req/day | |
| Currents API | https://currentsapi.services/ | 1 | 600 req/day | |
| Mediastack | https://mediastack.com/ | 1 | 500/mo | |
| NewsData.io | https://newsdata.io/ | 1 | 200/day | |
| Bing News Search | Azure | 2 | 付费 | |
| Google News RSS | `{lang}/rss/search?q=` | 0 | 无官方 API | 按关键词 |
| Event Registry | https://eventregistry.org/ | 0 | 2000 tokens/day | 事件聚类 |
| Aylien News API | 付费 | 2 | | NLP 增强 |
| ContextualWeb News | 付费 | 2 | | |

## 全球事件与 NLP

| name | url | tier |
|------|-----|------|
| GDELT 2.0 | https://blog.gdeltproject.org/gdelt-2-0-our-global-world-in-realtime/ | 0 |
| GDELT GKG | 全球知识图谱 | 0 |
| Common Crawl News | 存档 | 2 |
| Media Cloud | https://mediacloud.org/ | 1 |
| CrowdTangle (Meta) | 受限 | 2 |

## RSS/OPML 工具链

| tool | 用途 |
|------|------|
| FreshRSS / Miniflux | 自建 RSS 阅读器 → Webhook |
| Feedly API | 付费聚合 |
| Inoreader API | 付费 |
| RSSHub | https://github.com/DIYgod/RSSHub | 任意站转 RSS |
| Huginn | 自动化 Agent |
| n8n / Zapier | 工作流 |

## 元数据与实体

| name | tier | 用途 |
|------|------|------|
| Wikidata SPARQL | 0 | 实体链接 |
| DBpedia | 1 | |
| GeoNames | 0 | 地名 |
| OpenStreetMap Nominatim | 0 | 地理编码 |
| spaCy NER | 0 | 实体抽取 |
| OpenAI / Claude | 1 | 摘要分类 |

## 推荐架构

```
Tier 0: 直连 RSS/API（低延迟、可控）
Tier 1: Event Registry + GDELT（事件发现）
Tier 2: NewsAPI/GNews（补全长尾）
自建: RSSHub 补无 RSS 站点
```
