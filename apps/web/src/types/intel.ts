export interface ReportSummary {
  summary: string;
  tags: string[];
  relevance_score: number;
}

export interface Source {
  id: number;
  name: string;
  slug: string;
  category: string;
  source_type: string;
  url: string | null;
  tier: number;
  enabled: boolean;
  fetch_interval_minutes: number;
  last_ingested_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface SourceListResponse {
  success: boolean;
  data: Source[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface Article {
  id: number;
  source_id: number;
  title: string;
  url: string | null;
  content: string | null;
  content_hash: string;
  published_at: string | null;
  language: string | null;
  created_at: string;
  updated_at: string;
  report: ReportSummary | null;
}

export interface ArticleListResponse {
  success: boolean;
  data: Article[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface IntelligenceReport {
  id: number;
  article_id: number;
  summary: string;
  tags: string[];
  entities: { name: string; type?: string | null }[];
  relevance_score: number;
  sentiment: string | null;
  language: string | null;
  model: string | null;
  created_at: string;
  updated_at: string;
}

export interface AnalyzeArticleResponse {
  success: boolean;
  data: IntelligenceReport;
}

export interface IngestResult {
  source_id: number;
  status: string;
  items_found?: number;
  items_created?: number;
  items_skipped?: number;
  created_article_ids?: number[];
  error_message?: string | null;
  duration_ms?: number | null;
  task_id?: string | null;
}

export interface IngestLog {
  id: number;
  source_id: number;
  status: string;
  items_found: number;
  items_created: number;
  items_skipped: number;
  error_message: string | null;
  duration_ms: number | null;
  finished_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface IngestLogListResponse {
  success: boolean;
  data: IngestLog[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ArticleListParams {
  page?: number;
  page_size?: number;
  source_id?: number;
  tag?: string;
  published_from?: string;
  published_to?: string;
  has_report?: boolean;
  min_relevance?: number;
  q?: string;
}

/** Default threshold aligned with backend BRIEFING_MIN_RELEVANCE / briefing_min_relevance */
export const DEFAULT_MIN_RELEVANCE = 6.0;

export interface AlertRule {
  id: number;
  name: string;
  keywords: string[];
  enabled: boolean;
  match_in: "title" | "content" | "tags" | "all";
  channel: "log" | "webhook" | "email_stub";
  channel_config: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface AlertRuleListResponse {
  success: boolean;
  data: AlertRule[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface AlertEvent {
  id: number;
  rule_id: number;
  article_id: number;
  matched_keywords: string[];
  notification_status: string;
  notification_detail: string | null;
  article_title: string | null;
  rule_name: string | null;
  created_at: string;
  updated_at: string;
}

export interface AlertEventListResponse {
  success: boolean;
  data: AlertEvent[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface OverviewStats {
  sources_total: number;
  sources_enabled: number;
  articles_total: number;
  reports_total: number;
  alert_rules_total: number;
  alert_rules_enabled: number;
  alert_events_total: number;
}

export interface OverviewStatsResponse {
  success: boolean;
  data: OverviewStats;
}

export interface BriefingMeta {
  generated_at: string;
  window_hours: number;
  window_start: string;
  window_end: string;
  item_count: number;
  limit: number;
  min_relevance: number | null;
  ai_mode: string;
  sort: string;
}

export interface BriefingItem {
  rank: number;
  article_id: number;
  source_id: number;
  source_name: string;
  title: string;
  url: string | null;
  published_at: string | null;
  summary: string;
  tags: string[];
  relevance_score: number;
  sentiment: string | null;
  model: string | null;
}

export interface DailyBriefing {
  meta: BriefingMeta;
  overview: string;
  items: BriefingItem[];
  markdown?: string | null;
  html?: string | null;
}

export interface DailyBriefingResponse {
  success: boolean;
  data: DailyBriefing;
}

export interface DailyBriefingParams {
  hours?: number;
  limit?: number;
  min_relevance?: number;
  lang?: string;
  format?: "json" | "markdown";
}

export interface ArchiveSummary {
  archive_date: string;
  timezone: string;
  status: string;
  item_count: number;
  articles_created: number;
  high_relevance_count: number;
  top_category: string | null;
  top_heat_score: number | null;
}

export interface ArchiveListResponse {
  success: boolean;
  data: ArchiveSummary[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ArchiveDetail {
  id: number;
  archive_date: string;
  timezone: string;
  window_start: string;
  window_end: string;
  status: string;
  error_message: string | null;
  briefing: DailyBriefing | null;
  metrics: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface ArchiveDetailResponse {
  success: boolean;
  data: ArchiveDetail;
}

export interface CategoryHeatPoint {
  date: string;
  heat_score: number;
  articles: number;
  high_relevance: number;
  avg_relevance: number;
  category_label: string | null;
}

export interface CategoryHeatTrends {
  timezone: string;
  days: number;
  start_date: string;
  end_date: string;
  categories: string[];
  points_by_category: Record<string, CategoryHeatPoint[]>;
}

export interface CategoryHeatTrendsResponse {
  success: boolean;
  data: CategoryHeatTrends;
}
