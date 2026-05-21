import { apiClient } from "@/lib/api";
import type {
  AlertEventListResponse,
  AlertRule,
  AlertRuleListResponse,
  AnalyzeArticleResponse,
  ArchiveDetailResponse,
  ArchiveListResponse,
  Article,
  ArticleListParams,
  ArticleListResponse,
  CategoryHeatTrendsResponse,
  DailyBriefingParams,
  DailyBriefingResponse,
  IngestLogListResponse,
  IngestResult,
  OverviewStatsResponse,
  Source,
  SourceListResponse,
} from "@/types/intel";

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === "true";

const MOCK_SOURCES: Source[] = [
  {
    id: 1,
    name: "Reuters World",
    slug: "reuters-world",
    category: "wire",
    source_type: "rss",
    url: "https://example.com/feed",
    tier: 0,
    enabled: true,
    fetch_interval_minutes: 15,
    last_ingested_at: null,
    created_at: "2026-05-01T00:00:00Z",
    updated_at: "2026-05-01T00:00:00Z",
  },
];

const MOCK_ARTICLES: Article[] = [
  {
    id: 1,
    source_id: 1,
    title: "Mock geopolitics headline",
    url: "https://example.com/a/1",
    content: "Sample body",
    content_hash: "abc",
    published_at: "2026-05-15T10:00:00Z",
    language: "en",
    created_at: "2026-05-15T10:00:00Z",
    updated_at: "2026-05-15T10:00:00Z",
    report: {
      summary: "Mock intelligence summary.",
      tags: ["geopolitics", "mock"],
      relevance_score: 8.2,
    },
  },
];

function paramsToRecord(params?: Record<string, string | number | boolean | undefined>) {
  if (!params) return undefined;
  const out: Record<string, string> = {};
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== "") out[k] = String(v);
  }
  return out;
}

export async function listSources(
  page = 1,
  pageSize = 20,
  filters?: { tier?: number; enabled?: boolean; category?: string },
): Promise<SourceListResponse> {
  if (USE_MOCK) {
    return {
      success: true,
      data: MOCK_SOURCES,
      total: MOCK_SOURCES.length,
      page: 1,
      page_size: pageSize,
      total_pages: 1,
    };
  }
  return apiClient.get<SourceListResponse>("/api/v1/sources", {
    params: paramsToRecord({
      page,
      page_size: pageSize,
      tier: filters?.tier,
      enabled: filters?.enabled,
      category: filters?.category,
    }),
  });
}

export async function updateSource(
  id: number,
  data: Partial<Pick<Source, "enabled" | "tier" | "fetch_interval_minutes">>,
): Promise<Source> {
  if (USE_MOCK) return { ...MOCK_SOURCES[0], ...data, id };
  return apiClient.patch<Source>(`/api/v1/sources/${id}`, data);
}

export async function ingestSource(id: number, asyncMode = true): Promise<IngestResult> {
  if (USE_MOCK) {
    return asyncMode
      ? { source_id: id, status: "queued", task_id: "mock-task" }
      : {
          source_id: id,
          status: "success",
          items_found: 5,
          items_created: 2,
          items_skipped: 3,
          created_article_ids: [1, 2],
          error_message: null,
          duration_ms: 800,
        };
  }
  return apiClient.post<IngestResult>(`/api/v1/sources/${id}/ingest`, undefined, {
    params: asyncMode ? { async: "true" } : undefined,
  });
}

export async function listIngestLogs(
  sourceId: number,
  page = 1,
): Promise<IngestLogListResponse> {
  if (USE_MOCK) {
    return {
      success: true,
      data: [],
      total: 0,
      page: 1,
      page_size: 20,
      total_pages: 0,
    };
  }
  return apiClient.get<IngestLogListResponse>(`/api/v1/sources/${sourceId}/ingest-logs`, {
    params: { page: String(page) },
  });
}

export async function listArticles(params: ArticleListParams = {}): Promise<ArticleListResponse> {
  if (USE_MOCK) {
    let data = MOCK_ARTICLES;
    if (params.min_relevance != null) {
      data = data.filter(
        (a) => a.report != null && a.report.relevance_score >= params.min_relevance!,
      );
    }
    if (params.has_report === true) {
      data = data.filter((a) => a.report != null);
    }
    return {
      success: true,
      data,
      total: data.length,
      page: 1,
      page_size: 20,
      total_pages: 1,
    };
  }
  return apiClient.get<ArticleListResponse>("/api/v1/articles", {
    params: paramsToRecord(params as Record<string, string | number | boolean | undefined>),
  });
}

export async function getArticle(id: number): Promise<Article> {
  if (USE_MOCK) return MOCK_ARTICLES[0];
  return apiClient.get<Article>(`/api/v1/articles/${id}`);
}

export async function analyzeArticle(id: number): Promise<AnalyzeArticleResponse> {
  if (USE_MOCK) {
    return {
      success: true,
      data: {
        id: 1,
        article_id: id,
        summary: "Re-analyzed mock summary.",
        tags: ["mock"],
        entities: [],
        relevance_score: 9.0,
        sentiment: null,
        language: "en",
        model: "mock",
        created_at: "2026-05-19T00:00:00Z",
        updated_at: "2026-05-19T00:00:00Z",
      },
    };
  }
  return apiClient.post<AnalyzeArticleResponse>(`/api/v1/articles/${id}/analyze`);
}

export async function getArticleReport(id: number): Promise<AnalyzeArticleResponse> {
  if (USE_MOCK) return analyzeArticle(id);
  return apiClient.get<AnalyzeArticleResponse>(`/api/v1/articles/${id}/report`);
}

export async function listAlertRules(page = 1): Promise<AlertRuleListResponse> {
  if (USE_MOCK) {
    return {
      success: true,
      data: [
        {
          id: 1,
          name: "Mock geopolitics",
          keywords: ["geopolitics"],
          enabled: true,
          match_in: "all",
          channel: "log",
          channel_config: null,
          created_at: "2026-05-19T00:00:00Z",
          updated_at: "2026-05-19T00:00:00Z",
        },
      ],
      total: 1,
      page: 1,
      page_size: 20,
      total_pages: 1,
    };
  }
  return apiClient.get<AlertRuleListResponse>("/api/v1/alerts/rules", {
    params: { page: String(page) },
  });
}

export async function createAlertRule(data: {
  name: string;
  keywords: string[];
  match_in?: string;
  channel?: string;
  enabled?: boolean;
}): Promise<AlertRule> {
  if (USE_MOCK) {
    return {
      id: 99,
      name: data.name,
      keywords: data.keywords,
      enabled: data.enabled ?? true,
      match_in: (data.match_in as AlertRule["match_in"]) ?? "all",
      channel: (data.channel as AlertRule["channel"]) ?? "log",
      channel_config: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
  }
  return apiClient.post<AlertRule>("/api/v1/alerts/rules", data);
}

export async function updateAlertRule(
  id: number,
  data: Partial<Pick<AlertRule, "enabled" | "keywords" | "name">>,
): Promise<AlertRule> {
  if (USE_MOCK) return { ...(await listAlertRules()).data[0], ...data, id };
  return apiClient.patch<AlertRule>(`/api/v1/alerts/rules/${id}`, data);
}

export async function deleteAlertRule(id: number): Promise<void> {
  if (USE_MOCK) return;
  await apiClient.delete(`/api/v1/alerts/rules/${id}`);
}

export async function listAlertEvents(page = 1): Promise<AlertEventListResponse> {
  if (USE_MOCK) {
    return {
      success: true,
      data: [],
      total: 0,
      page: 1,
      page_size: 20,
      total_pages: 0,
    };
  }
  return apiClient.get<AlertEventListResponse>("/api/v1/alerts/events", {
    params: { page: String(page) },
  });
}

export async function getOverviewStats(): Promise<OverviewStatsResponse> {
  if (USE_MOCK) {
    return {
      success: true,
      data: {
        sources_total: 12,
        sources_enabled: 8,
        articles_total: 340,
        reports_total: 120,
        alert_rules_total: 3,
        alert_rules_enabled: 2,
        alert_events_total: 15,
      },
    };
  }
  return apiClient.get<OverviewStatsResponse>("/api/v1/stats/overview");
}

export async function getDailyBriefing(
  params: DailyBriefingParams = {},
): Promise<DailyBriefingResponse> {
  if (USE_MOCK) {
    const now = new Date().toISOString();
    return {
      success: true,
      data: {
        meta: {
          generated_at: now,
          window_hours: params.hours ?? 24,
          window_start: now,
          window_end: now,
          item_count: 2,
          limit: params.limit ?? 20,
          min_relevance: params.min_relevance ?? null,
          ai_mode: "mock",
          sort: "relevance_score_desc",
        },
        overview: "过去时间窗内共 2 条高相关情报，主要主题：geopolitics, cyber。（当前为 Mock AI 分析模式）",
        items: [
          {
            rank: 1,
            article_id: 1,
            source_id: 1,
            source_name: "Reuters World",
            title: "Mock geopolitics headline",
            url: "https://example.com/a/1",
            published_at: now,
            summary: "Mock intelligence summary for briefing preview.",
            tags: ["geopolitics", "mock"],
            relevance_score: 8.5,
            sentiment: "neutral",
            model: "mock",
          },
          {
            rank: 2,
            article_id: 2,
            source_id: 1,
            source_name: "Reuters World",
            title: "Mock cyber security alert",
            url: "https://example.com/a/2",
            published_at: now,
            summary: "Second mock briefing item.",
            tags: ["cyber"],
            relevance_score: 7.2,
            sentiment: "negative",
            model: "mock",
          },
        ],
      },
    };
  }
  const query: Record<string, string> = {};
  if (params.hours != null) query.hours = String(params.hours);
  if (params.limit != null) query.limit = String(params.limit);
  if (params.min_relevance != null) query.min_relevance = String(params.min_relevance);
  if (params.lang) query.lang = params.lang;
  if (params.format) query.format = params.format;
  return apiClient.get<DailyBriefingResponse>("/api/v1/briefings/daily", { params: query });
}

export async function listArchives(
  page = 1,
  pageSize = 20,
): Promise<ArchiveListResponse> {
  if (USE_MOCK) {
    return {
      success: true,
      data: [
        {
          archive_date: "2026-05-20",
          timezone: "Asia/Shanghai",
          status: "success",
          item_count: 12,
          articles_created: 45,
          high_relevance_count: 8,
          top_category: "geopolitical",
          top_heat_score: 28.5,
        },
      ],
      total: 1,
      page: 1,
      page_size: pageSize,
      total_pages: 1,
    };
  }
  return apiClient.get<ArchiveListResponse>("/api/v1/archives", {
    params: { page: String(page), page_size: String(pageSize) },
  });
}

export async function getArchive(date: string): Promise<ArchiveDetailResponse> {
  if (USE_MOCK) {
    const briefing = (await getDailyBriefing()).data;
    return {
      success: true,
      data: {
        id: 1,
        archive_date: date,
        timezone: "Asia/Shanghai",
        window_start: briefing.meta.window_start,
        window_end: briefing.meta.window_end,
        status: "success",
        error_message: null,
        briefing,
        metrics: {
          category_heat: [
            {
              category: "geopolitical",
              category_label: "地缘/OSINT",
              articles: 10,
              heat_score: 28.5,
              high_relevance: 3,
              avg_relevance: 7.2,
            },
          ],
        },
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    };
  }
  return apiClient.get<ArchiveDetailResponse>(`/api/v1/archives/${date}`);
}

export async function getCategoryHeatTrends(
  days = 30,
): Promise<CategoryHeatTrendsResponse> {
  if (USE_MOCK) {
    return {
      success: true,
      data: {
        timezone: "Asia/Shanghai",
        days,
        start_date: "2026-05-01",
        end_date: "2026-05-20",
        categories: ["geopolitical", "cyber", "wire"],
        points_by_category: {
          geopolitical: [
            { date: "2026-05-19", heat_score: 22, articles: 12, high_relevance: 3, avg_relevance: 7, category_label: "地缘/OSINT" },
            { date: "2026-05-20", heat_score: 28, articles: 15, high_relevance: 4, avg_relevance: 7.5, category_label: "地缘/OSINT" },
          ],
          cyber: [
            { date: "2026-05-19", heat_score: 14, articles: 8, high_relevance: 2, avg_relevance: 6, category_label: "网络安全" },
            { date: "2026-05-20", heat_score: 18, articles: 10, high_relevance: 2, avg_relevance: 6.5, category_label: "网络安全" },
          ],
          wire: [
            { date: "2026-05-19", heat_score: 30, articles: 20, high_relevance: 2, avg_relevance: 8, category_label: "通讯社/主流" },
            { date: "2026-05-20", heat_score: 25, articles: 18, high_relevance: 1, avg_relevance: 7, category_label: "通讯社/主流" },
          ],
        },
      },
    };
  }
  return apiClient.get<CategoryHeatTrendsResponse>(
    "/api/v1/archives/trends/category-heat",
    { params: { days: String(days) } },
  );
}
