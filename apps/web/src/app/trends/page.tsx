"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { Archive, Loader2, RefreshCw, TrendingUp } from "lucide-react";
import { getCategoryHeatTrends } from "@/lib/intel-api";
import type { CategoryHeatPoint, CategoryHeatTrends } from "@/types/intel";

const DAY_OPTIONS = [7, 14, 30] as const;

const CATEGORY_LABELS: Record<string, string> = {
  wire: "通讯社/主流",
  regional: "分地区媒体",
  official: "政府/机构",
  financial: "财经/宏观",
  geopolitical: "地缘/OSINT",
  cyber: "网络安全",
  social: "社交/UGC",
  research: "学术/研究",
  vertical: "行业垂直",
  aggregator: "聚合/API",
  maritime: "海事/航空",
  compliance: "制裁/合规",
  humanitarian: "人道/灾害",
  china: "大中华区",
  thinktank: "智库/政策",
  other: "其他",
};

function labelFor(category: string, points: CategoryHeatPoint[]): string {
  const fromApi = points.find((p) => p.category_label)?.category_label;
  return fromApi || CATEGORY_LABELS[category] || category;
}

function formatShortDate(iso: string): string {
  const d = new Date(`${iso}T12:00:00`);
  return d.toLocaleDateString("zh-CN", { month: "numeric", day: "numeric" });
}

function buildMatrix(trends: CategoryHeatTrends) {
  const dates = new Set<string>();
  for (const points of Object.values(trends.points_by_category)) {
    for (const p of points) dates.add(p.date);
  }
  const sortedDates = [...dates].sort();
  const rows = trends.categories
    .map((cat) => {
      const points = trends.points_by_category[cat] || [];
      const byDate = Object.fromEntries(points.map((p) => [p.date, p]));
      const latest = points[points.length - 1];
      const maxHeat = Math.max(...points.map((p) => p.heat_score), 1);
      return { cat, points, byDate, latest, maxHeat };
    })
    .sort((a, b) => (b.latest?.heat_score ?? 0) - (a.latest?.heat_score ?? 0));
  return { sortedDates, rows };
}

export default function TrendsPage() {
  const [days, setDays] = useState<number>(30);
  const [trends, setTrends] = useState<CategoryHeatTrends | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getCategoryHeatTrends(days);
      setTrends(res.data);
    } catch {
      setError("加载趋势失败。请先运行每日归档任务或回填历史数据。");
      setTrends(null);
    } finally {
      setLoading(false);
    }
  }, [days]);

  useEffect(() => {
    load();
  }, [load]);

  const matrix = useMemo(
    () => (trends ? buildMatrix(trends) : null),
    [trends],
  );

  const globalMax = useMemo(() => {
    if (!trends) return 1;
    let max = 1;
    for (const points of Object.values(trends.points_by_category)) {
      for (const p of points) max = Math.max(max, p.heat_score);
    }
    return max;
  }, [trends]);

  return (
    <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <TrendingUp className="h-7 w-7 text-primary-600" />
            <h1 className="text-2xl font-bold">业务分类热度趋势</h1>
          </div>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            按来源业务分类统计热度（articles + 3×高相关 + 平均相关度），归档日历为
            <span className="font-medium text-gray-800 dark:text-gray-200"> 北京时间 </span>
            ({trends?.timezone ?? "Asia/Shanghai"})
          </p>
          {trends && (
            <p className="mt-1 text-xs text-gray-500">
              {trends.start_date} — {trends.end_date} · {trends.categories.length} 个分类
            </p>
          )}
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <div className="flex rounded-lg border dark:border-gray-700">
            {DAY_OPTIONS.map((option) => (
              <button
                key={option}
                type="button"
                onClick={() => setDays(option)}
                className={`px-3 py-2 text-sm first:rounded-l-lg last:rounded-r-lg ${
                  days === option
                    ? "bg-primary-600 text-white"
                    : "bg-white text-gray-700 hover:bg-gray-50 dark:bg-gray-900 dark:text-gray-300 dark:hover:bg-gray-800"
                }`}
              >
                {option} 天
              </button>
            ))}
          </div>
          <button
            type="button"
            onClick={load}
            disabled={loading}
            className="inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm hover:bg-gray-50 disabled:opacity-50 dark:border-gray-700 dark:hover:bg-gray-800"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            刷新
          </button>
        </div>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-24 text-gray-500">
          <Loader2 className="mr-2 h-6 w-6 animate-spin" />
          加载趋势中…
        </div>
      )}

      {!loading && error && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-center dark:border-red-900/50 dark:bg-red-950/20">
          <p className="text-red-700 dark:text-red-300">{error}</p>
          <Link
            href="/archives"
            className="mt-4 inline-flex items-center gap-2 text-sm text-primary-600 hover:underline"
          >
            <Archive className="h-4 w-4" />
            查看归档列表
          </Link>
        </div>
      )}

      {!loading && !error && trends && matrix && (
        <>
          {matrix.rows.length === 0 ? (
            <div className="rounded-xl border border-dashed p-12 text-center dark:border-gray-700">
              <p className="text-gray-600 dark:text-gray-400">
                所选时间范围内暂无归档数据。请运行 Celery 归档任务或执行 backfill 脚本。
              </p>
            </div>
          ) : (
            <>
              <section className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {matrix.rows.slice(0, 6).map(({ cat, points, latest, maxHeat }) => (
                  <div
                    key={cat}
                    className="rounded-xl border bg-white p-4 dark:border-gray-800 dark:bg-gray-900/50"
                  >
                    <div className="mb-2 flex items-center justify-between gap-2">
                      <h3 className="truncate text-sm font-semibold">
                        {labelFor(cat, points)}
                      </h3>
                      <span className="shrink-0 font-mono text-lg font-bold text-primary-600">
                        {latest?.heat_score.toFixed(1) ?? "—"}
                      </span>
                    </div>
                    <div className="flex h-16 items-end gap-0.5">
                      {points.map((p) => (
                        <div
                          key={p.date}
                          className="min-w-[4px] flex-1 rounded-t bg-primary-500/80 dark:bg-primary-400/70"
                          style={{ height: `${Math.max(8, (p.heat_score / maxHeat) * 100)}%` }}
                          title={`${p.date}: ${p.heat_score}`}
                        />
                      ))}
                    </div>
                    <p className="mt-2 text-xs text-gray-500">
                      最新 {latest?.articles ?? 0} 篇 · 高相关 {latest?.high_relevance ?? 0}
                    </p>
                  </div>
                ))}
              </section>

              <section className="overflow-x-auto rounded-xl border bg-white dark:border-gray-800 dark:bg-gray-900/50">
                <table className="min-w-full text-sm">
                  <thead>
                    <tr className="border-b dark:border-gray-800">
                      <th className="sticky left-0 bg-white px-4 py-3 text-left font-semibold dark:bg-gray-900">
                        业务分类
                      </th>
                      {matrix.sortedDates.map((d) => (
                        <th key={d} className="px-2 py-3 text-center font-medium text-gray-500">
                          {formatShortDate(d)}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {matrix.rows.map(({ cat, points, byDate }) => (
                      <tr key={cat} className="border-b last:border-0 dark:border-gray-800">
                        <td className="sticky left-0 bg-white px-4 py-2 font-medium dark:bg-gray-900">
                          {labelFor(cat, points)}
                        </td>
                        {matrix.sortedDates.map((d) => {
                          const p = byDate[d];
                          const intensity = p ? p.heat_score / globalMax : 0;
                          return (
                            <td key={d} className="px-2 py-2 text-center">
                              {p ? (
                                <span
                                  className="inline-block min-w-[2.5rem] rounded px-1.5 py-0.5 font-mono text-xs"
                                  style={{
                                    backgroundColor: `rgba(37, 99, 235, ${0.12 + intensity * 0.55})`,
                                  }}
                                  title={`热度 ${p.heat_score} · ${p.articles} 篇`}
                                >
                                  {p.heat_score.toFixed(0)}
                                </span>
                              ) : (
                                <span className="text-gray-300 dark:text-gray-700">—</span>
                              )}
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </section>
            </>
          )}
        </>
      )}
    </main>
  );
}
