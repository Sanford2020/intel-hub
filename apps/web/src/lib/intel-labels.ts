/**
 * Unified business category and status labels.
 */

export const CATEGORY_LABELS: Record<string, string> = {
  wire: "通讯社/主流",
  geopolitical: "地缘/OSINT",
  cyber: "网络安全",
  finance: "财经",
  tech: "科技",
  defense: "军事/国防",
  energy: "能源",
  health: "公共卫生",
  climate: "气候/环境",
};

export function categoryLabel(category: string): string {
  return CATEGORY_LABELS[category] || category;
}

export const TIER_LABELS: Record<number, string> = {
  0: "核心",
  1: "高频",
  2: "常规",
  3: "低频",
};

export function tierLabel(tier: number): string {
  return TIER_LABELS[tier] || `Tier ${tier}`;
}

export const SENTIMENT_LABELS: Record<string, string> = {
  positive: "正面",
  negative: "负面",
  neutral: "中立",
  mixed: "混合",
};

export function sentimentLabel(sentiment: string | null): string {
  if (!sentiment) return "—";
  return SENTIMENT_LABELS[sentiment] || sentiment;
}
