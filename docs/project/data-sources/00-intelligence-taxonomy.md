# 00 — 情报信号分类体系（Taxonomy）

> Intel Hub 采集的不是「新闻」单一维度，而是 **多类情报信号（Signals）**。本文件定义全量分类，各目录文件按此归类。

## 一级分类（Category）

| code | 名称 | 典型源 | 时效 | 目录 |
|------|------|--------|------|------|
| `wire` | 通讯社/主流快讯 | Reuters, AP, BBC | 分钟级 | 01 |
| `regional` | 分地区媒体 | Politico, Kyiv Independent | 分钟级 | 02 |
| `official` | 政府/监管/国际机构 | State Dept, UN, 国务院 | 小时级 | 03 |
| `financial` | 财经/宏观/市场 | FT, FRED, SEC | 分钟~日 | 04 |
| `geopolitical` | 地缘/OSINT/冲突 | ISW, ACLED, Bellingcat | 小时级 | 05 |
| `cyber` | 网络安全/威胁情报 | CISA, Krebs, OTX | 分钟~小时 | 06 |
| `social` | 社交/论坛/UGC | Reddit, X, 微博 | 实时 | 07 |
| `research` | 学术/专利/预印本 | arXiv, PubMed, USPTO | 日级 | 08 |
| `vertical` | 行业垂直 | OilPrice, STAT, SemiAnalysis | 小时级 | 09 |
| `aggregator` | 聚合 API/元数据 | NewsAPI, GDELT, Event Registry | 分钟级 | 10 |
| `maritime` | 海事/航空/卫星 | AIS, OpenSky, NASA FIRMS | 实时~小时 | 11 |
| `compliance` | 制裁/PEP/法律 | OFAC, OpenSanctions, EUR-Lex | 日级 | 12 |
| `humanitarian` | 人道/灾害/气象 | ReliefWeb, USGS, GDACS | 分钟~小时 | 13 |
| `china` | 中国/大中华区 | 新华社, 财新, CNA | 分钟级 | 14 |
| `thinktank` | 智库/政策研究 | RAND, CSIS, Brookings | 日~周 | 15 |

## 二级维度（Subcategory 示例）

| 维度 | 值示例 |
|------|--------|
| **主题** | conflict, trade, sanctions, election, energy, ai, health, climate |
| **信号类型** | event, statement, data-point, analysis, alert, rumor |
| **可信度** | official, wire, verified, single-source, unverified |
| **地理** | global, US, EU, CN, TW, MENA, ... |
| **语言** | en, zh, ar, ru, multi |

## 情报价值链（Pipeline 视角）

```
采集 (Ingest) → 归一 (Normalize) → 去重 (Dedupe) → 实体链接 (Entity)
     → 分类/标签 (Classify) → 摘要 (Summarize) → 关联 (Link Events)
     → 告警 (Alert) → 报告 (Brief)
```

| 阶段 | 适用源类型 |
|------|-----------|
| 快讯层 | wire, official, aggregator |
| 态势层 | geopolitical, maritime, humanitarian |
| 分析层 | thinktank, research, vertical |
| 弱信号层 | social, cyber TI feeds |
| 结构化层 | compliance, financial APIs, ACLED/GDELT |

## 源类型（type）与采集器映射

| type | 采集器 | 频率建议 |
|------|--------|----------|
| `rss` | RSSWorker | 5–15 min |
| `rest_api` | APIWorker | 按配额 |
| `gdelt` | GDELTWorker | 15 min |
| `acled` | ACLEDWorker | 1 day |
| `telegram` | TelegramWorker | 1–5 min |
| `scraper` | ScraperWorker | 按需 |
| `webhook` | WebhookReceiver | 实时 |
| `opml` | 批量导入，非运行时 type | — |

## 许可与合规分级

| 级别 | 说明 | 处理 |
|------|------|------|
| L0 开放 | RSS/API 明确允许聚合 | 默认启用 |
| L1 限制 | 有 rate limit / 非商用 | 标注 + 限频 |
| L2 付费 | 需订阅/API key | tier=2, 按需开通 |
| L3 敏感 | 社交爬虫/暗网/制裁查询 | 合规审查 + 审计日志 |

## 当前目录统计（已录入条目约数）

| 文件 | 条目约数 | Tier 0 约数 |
|------|----------|-------------|
| 01 通讯社/主流 | 55+ | 25 |
| 02 分地区 | 45+ | 10 |
| 03 政府/机构 | 55+ | 15 |
| 04 财经 | 40+ | 8 |
| 05 OSINT/地缘 | 35+ | 12 |
| 06 网安 | 40+ | 10 |
| 07 社交 | 35+ | 3 |
| 08 学术 | 25+ | 2 |
| 09 垂直 | 50+ | 5 |
| 10 聚合 API | 25+ | 4 |
| 11 海事/航空/卫星 | 35+ | 0 |
| 12 制裁/法律 | 35+ | 3 |
| 13 人道/灾害 | 35+ | 5 |
| 14 大中华区 | 45+ | 8 |
| 15 智库 | 45+ | 10 |
| **合计** | **~580 已命名源** | **~120 Tier 0 候选** |

> Tier 2 长尾（本地语言媒体、付费库）规划扩展至 **800+**，通过 NewsAPI/GNews + RSSHub + OPML 批量导入补充。

## 尚未单独成册、但已覆盖的子域

| 子域 | 归入 |
|------|------|
| 选举/民调 | official + thinktank + social |
| 加密货币/链上 | financial + cyber |
| 人口/移民 | humanitarian + official |
| 环境/ESG | vertical + official |
| 太空/军工 | vertical + geopolitical |
| 假新闻/信息战 | social + thinktank (标注) |

## 开发前确认清单

- [ ] 确认 Tier 0 商业基线范围（见 [tier-0-commercial-seed.md](./tier-0-commercial-seed.md)）
- [ ] 确认 API Key：NewsAPI、GNews、（可选）Event Registry、FRED
- [ ] 确认合规边界：社交采集、制裁数据存储
- [ ] 确认语言优先级：en 优先 / zh 同步 / multi 后续
- [ ] 确认告警主题：地缘、制裁、网安、中国政策
