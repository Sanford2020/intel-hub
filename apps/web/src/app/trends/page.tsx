"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { Archive, RefreshCw } from "lucide-react";
import { getCategoryHeatTrends } from "@/lib/intel-api";
import type { CategoryHeatPoint, CategoryHeatTrends } from "@/types/intel";
import { PageHeader } from "@/components/ui/PageHeader";
import { SurfaceCard } from "@/components/ui/SurfaceCard";
import { SegmentedControl } from "@/components/ui/SegmentedControl";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { LoadingBlock } from "@/components/ui/LoadingBlock";
import { EmptyState } from "@/components/ui/EmptyState";
import { categoryLabel } from "@/lib/intel-labels";

const DAY_OPTIONS = [
  { value: 7, label: "7 天" },
  { value: 14, label: "14 天" },
  { value: 30, label: "30 天" },
];

function labelFor(category: string, points: CategoryHeatPoint[]): string {
  const fromApi = points.find((p) => p.category_label)?.category_label;
  return fromApi || categoryLabel(category);
}

function formatShortDate(iso: string): string {
  const d = new Date(`${iso}T12:00:00`);
  return d.toLocaleDateString("zh-CN", { month: "numeric", day: "numeric" });
}

function dedupePointsByDate(points: CategoryHeatPoint[]): CategoryHeatPoint[] {
  const byDate = new Map<string, CategoryHeatPoint>();
  for (const p of points) byDate.set(p.date, p);
  return [...byDate.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([, p]) => p);
}

function buildMatrix(trends: CategoryHeatTrends) {
  const dates = new Set<string>();
  for (const points of Object.values(trends.points_by_category)) {
    for (const p of dedupePointsByDate(points)) dates.add(p.date);
  }
  const sortedDates = [...dates].sort();
  const rows = trends.categories
    .map((cat) => {
      const points = dedupePointsByDate(trends.points_by_category[cat] || []);
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
    <main className="app-shell">
      <PageHeader
        title="业务分类热度趋势"
        description={`按来源业务分类统计热度（articles + 3×高相关 + 平均相关度），归档日历为北京时间 (${trends?.timezone ?? "Asia/Shanghai"})`}
        meta={
          trends ? (
            <p className="text-xs text-slate-500">
              {trends.start_date} — {trends.end_date} · {trends.categories.length} 个分类
            </p>
          ) : undefined
        }
        actions={
          <div className="flex flex-wrap items-center gap-2">
            <SegmentedControl options={DAY_OPTIONS} value={days} onChange={setDays} />
            <button
              type="button"
              onClick={load}
              disabled={loading}
              className="inline-flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-1.5 text-sm hover:bg-slate-50 disabled:opacity-50 dark:border-slate-700 dark:hover:bg-slate-800"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
              刷新
            </button>
          </div>
        }
      />

      {loading && (
        <div className="mt-6">
          <LoadingBlock lines={5} />
        </div>
      )}

      {!loading && error && (
        <div className="mt-6">
          <ErrorBanner message={error} onRetry={load} />
          <Link
            href="/archives"
            className="mt-3 inline-flex items-center gap-2 text-sm text-primary-600 hover:underline"
          >
            <Archive className="h-4 w-4" />
            查看归档列表
          </Link>
        </div>
      )}

      {!loading && !error && trends && matrix && (
        <div className="mt-6">
          {matrix.rows.length === 0 ? (
            <EmptyState
              title="暂无归档数据"
              description="所选时间范围内暂无归档数据，请运行 Celery 归档任务或执行 backfill 脚本"
            />
          ) : (
            <div className="space-y-6">
              <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {matrix.rows.slice(0, 6).map(({ cat, points, latest, maxHeat }) => (
                  <SurfaceCard key={cat} padding="sm">
                    <div className="mb-2 flex items-center justify-between gap-2">
                      <h3 className="truncate text-sm font-semibold text-slate-900 dark:text-white">
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
                    <p className="mt-2 text-xs text-slate-500">
                      最新 {latest?.articles ?? 0} 篇 · 高相关 {latest?.high_relevance ?? 0}
                    </p>
                  </SurfaceCard>
                ))}
              </section>

              <SurfaceCard padding="none" className="overflow-x-auto">
                <table className="min-w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-200 dark:border-slate-800">
                      <th className="sticky left-0 bg-white px-4 py-3 text-left font-semibold dark:bg-slate-900">
                        业务分类
                      </th>
                      {matrix.sortedDates.map((d) => (
                        <th key={d} className="px-2 py-3 text-center font-medium text-slate-500">
                          {formatShortDate(d)}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {matrix.rows.map(({ cat, points, byDate }) => (
                      <tr key={cat} className="border-b border-slate-100 last:border-0 dark:border-slate-800">
                        <td className="sticky left-0 bg-white px-4 py-2 font-medium dark:bg-slate-900">
                          {labelFor(cat, points)}
                        </td>
                        {matrix.sortedDates.map((d) => {
                          const p = byDate[d];
                          const intensity = p ? p.heat_score / globalMax : 0;
                          return (
                            <td key={d} className="px-2 py-2 text-center">
                              {p ? (
                                <span
                                  className="inline-block min-w-[2.5rem] rounded px-1.5 py-0.5 font-mono text-xs text-white"
                                  style={{
                                    backgroundColor: `hsl(221, 83%, ${65 - intensity * 30}%)`,
                                  }}
                                  title={`热度 ${p.heat_score} · ${p.articles} 篇`}
                                >
                                  {p.heat_score.toFixed(0)}
                                </span>
                              ) : (
                                <span className="text-slate-300 dark:text-slate-700">—</span>
                              )}
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </SurfaceCard>
            </div>
          )}
        </div>
      )}
    </main>
  );
}
