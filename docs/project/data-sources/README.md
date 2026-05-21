# Intel Hub — 情报数据源总目录

> **开发前阶段：先定源、后写码。** 每个源在实现时录入 `sources` 表，字段见 [source-schema.md](./source-schema.md)。

## 快速入口

| 文档 | 用途 |
|------|------|
| [00-intelligence-taxonomy.md](./00-intelligence-taxonomy.md) | 情报信号分类体系、管道视角、合规分级 |
| [tier-0-commercial-seed.md](./tier-0-commercial-seed.md) | **~80 个商业版种子源**（Sprint 1 导入基准） |
| [priority-matrix.md](./priority-matrix.md) | Tier 0/1/2 与 Sprint 映射 |
| [source-schema.md](./source-schema.md) | 统一 Source 数据模型 |

## 目录结构（15 类数据源）

| 文件 | 覆盖范围 | 已录入约 |
|------|----------|----------|
| [00-intelligence-taxonomy.md](./00-intelligence-taxonomy.md) | 分类体系与统计 | — |
| [01-global-news-wire.md](./01-global-news-wire.md) | 通讯社、全球主流媒体 | 55+ |
| [02-regional-by-geography.md](./02-regional-by-geography.md) | 分洲/分国家媒体 | 45+ |
| [03-government-official.md](./03-government-official.md) | 政府、国际机构、监管 | 55+ |
| [04-financial-economic.md](./04-financial-economic.md) | 财经、宏观、市场、公司 | 40+ |
| [05-osint-geopolitical.md](./05-osint-geopolitical.md) | OSINT、冲突、地缘 | 35+ |
| [06-cyber-threat-intel.md](./06-cyber-threat-intel.md) | 网络安全、威胁情报 | 40+ |
| [07-social-sentiment-ugc.md](./07-social-sentiment-ugc.md) | 社交、论坛、UGC | 35+ |
| [08-academic-research-patents.md](./08-academic-research-patents.md) | 学术、专利、预印本 | 25+ |
| [09-industry-verticals.md](./09-industry-verticals.md) | 能源、半导体、医药等垂直 | 50+ |
| [10-aggregators-apis.md](./10-aggregators-apis.md) | 新闻/数据聚合 API | 25+ |
| [11-maritime-aviation-satellite.md](./11-maritime-aviation-satellite.md) | 船舶、航空、卫星 | 35+ |
| [12-sanctions-legal-pep.md](./12-sanctions-legal-pep.md) | 制裁、PEP、法律 | 35+ |
| [13-humanitarian-disaster-weather.md](./13-humanitarian-disaster-weather.md) | 人道、灾害、气象 | 35+ |
| [14-china-greater-china.md](./14-china-greater-china.md) | 中国及大中华区 | 45+ |
| [15-think-tanks-policy.md](./15-think-tanks-policy.md) | 智库、政策研究 | 45+ |
| [tier-0-commercial-seed.md](./tier-0-commercial-seed.md) | 商业版种子清单 | ~80 |

## 统计

| 层级 | 已录入 | 目标 | 说明 |
|------|--------|------|------|
| 文档合计 | **~580 命名源** | 800+ | 01–15 各文件表格之和 |
| Tier 0 商业基线 | **~80**（见 seed 清单） | 80 | Sprint 1–2 可接入 |
| Tier 1 扩展 | ~200 候选 | 300 | 政府/垂直/中文/Reddit |
| Tier 2 全量 | 长尾 + 付费 | 800+ | 海事/社交/商业 API |

## 推荐工作流（当前阶段）

```
1. 通读 00-taxonomy → 理解信号分类
2. 审阅 tier-0-commercial-seed → 确认/删减商业版 80 源
3. 按主题深入 01–15 → 标记 Tier 1 优先级
4. 确认 API Key 与合规边界
5. 生成 seeds/tier-0-sources.json → 进入 Sprint 1 开发
```

## 使用方式（开发期）

1. 每条源字段：`name, slug, type, url, region, language, category, tier, license_notes`  
2. OPML / JSON 批量导入 `sources` 表  
3. Worker 按 `type` 路由到 RSS / API / GDELT 采集器
