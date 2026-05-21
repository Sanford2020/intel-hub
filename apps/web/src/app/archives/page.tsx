"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { Archive, ChevronRight, Loader2, RefreshCw } from "lucide-react";
import { listArchives } from "@/lib/intel-api";
import type { ArchiveSummary } from "@/types/intel";

const CATEGORY_LABELS: Record<string, string> = {
  wire: "通讯社/主流",
  geopolitical: "地缘/OSINT",
  cyber: "网络安全",
  social: "社交/UGC",
  aggregator: "聚合/API",
  other: "其他",
};

function categoryLabel(code: string | null): string {
  if (!code) return "—";
  return CATEGORY_LABELS[code] ?? code;
}

export default function ArchivesPage() {
  const [rows, setRows] = useState<ArchiveSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await listArchives(1, 60);
      setRows(res.data);
    } catch (err) {
      const msg =
        err instanceof Error && err.message
          ? err.message
          : "加载归档列表失败，请确认后端 API 已启动。";
      setError(msg);
      setRows([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <Archive className="h-7 w-7 text-primary-600" />
            <h1 className="text-2xl font-bold">每日归档</h1>
          </div>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            按<span className="font-medium">北京时间</span>日历日保存简报快照与业务分类热度指标
          </p>
        </div>
        <div className="flex gap-2">
          <Link
            href="/trends"
            className="rounded-lg border px-3 py-2 text-sm hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800"
          >
            查看趋势
          </Link>
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
          加载归档…
        </div>
      )}

      {!loading && error && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-center dark:border-red-900/50 dark:bg-red-950/20">
          <p className="text-red-700 dark:text-red-300">{error}</p>
        </div>
      )}

      {!loading && !error && rows.length === 0 && (
        <div className="rounded-xl border border-dashed p-12 text-center dark:border-gray-700">
          <p className="text-gray-600 dark:text-gray-400">暂无归档记录。</p>
          <p className="mt-2 text-sm text-gray-500">
            运行 Celery Beat 任务 <code className="rounded bg-gray-100 px-1 dark:bg-gray-800">archive_daily_snapshot</code>{" "}
            或脚本 <code className="rounded bg-gray-100 px-1 dark:bg-gray-800">backfill-archives.py</code>
          </p>
        </div>
      )}

      {!loading && !error && rows.length > 0 && (
        <div className="overflow-hidden rounded-xl border dark:border-gray-800">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-800">
            <thead className="bg-gray-50 dark:bg-gray-900/80">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">
                  归档日 (北京)
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">
                  简报条数
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">
                  新增资讯
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">
                  最热分类
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">
                  热度
                </th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 bg-white dark:divide-gray-800 dark:bg-gray-950/30">
              {rows.map((row) => (
                <tr key={row.archive_date} className="hover:bg-gray-50 dark:hover:bg-gray-900/50">
                  <td className="px-4 py-3 font-medium">{row.archive_date}</td>
                  <td className="px-4 py-3">{row.item_count}</td>
                  <td className="px-4 py-3">{row.articles_created}</td>
                  <td className="px-4 py-3">{categoryLabel(row.top_category)}</td>
                  <td className="px-4 py-3 font-mono">
                    {row.top_heat_score != null ? row.top_heat_score.toFixed(1) : "—"}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Link
                      href={`/archives/${row.archive_date}`}
                      className="inline-flex items-center gap-1 text-sm text-primary-600 hover:underline"
                    >
                      详情
                      <ChevronRight className="h-4 w-4" />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}
