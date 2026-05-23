"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { ChevronRight, RefreshCw } from "lucide-react";
import { listArchives } from "@/lib/intel-api";
import type { ArchiveSummary } from "@/types/intel";
import { PageHeader } from "@/components/ui/PageHeader";
import { SurfaceCard } from "@/components/ui/SurfaceCard";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { LoadingBlock } from "@/components/ui/LoadingBlock";
import { EmptyState } from "@/components/ui/EmptyState";
import { categoryLabel as categoryLabelFn } from "@/lib/intel-labels";

function categoryLabel(code: string | null): string {
  if (!code) return "—";
  return categoryLabelFn(code);
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
      const raw =
        err instanceof Error && err.message
          ? err.message
          : "加载归档列表失败";
      setError(raw.includes("Internal Server Error") || raw.includes("Failed to fetch") ? "无法连接后端服务，请确认 API 已启动" : raw);
      setRows([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <main className="app-shell">
      <PageHeader
        title="每日归档"
        description="按北京时间日历日保存简报快照与业务分类热度指标"
        actions={
          <div className="flex gap-2">
            <Link
              href="/trends"
              className="rounded-lg border border-slate-200 px-3 py-1.5 text-sm hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-800"
            >
              查看趋势
            </Link>
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
          <LoadingBlock lines={4} />
        </div>
      )}

      {!loading && error && (
        <div className="mt-6">
          <ErrorBanner message={error} onRetry={load} />
        </div>
      )}

      {!loading && !error && rows.length === 0 && (
        <div className="mt-6">
          <EmptyState
            title="暂无归档记录"
            description="运行 Celery Beat 任务 archive_daily_snapshot 或脚本 backfill-archives.py"
          />
        </div>
      )}

      {!loading && !error && rows.length > 0 && (
        <SurfaceCard padding="none" className="mt-6 overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 text-sm dark:divide-slate-800">
            <thead className="bg-slate-50 dark:bg-slate-900/80">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-slate-500">
                  归档日 (北京)
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-slate-500">
                  简报条数
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-slate-500">
                  新增资讯
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-slate-500">
                  最热分类
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-slate-500">
                  热度
                </th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {rows.map((row) => (
                <tr key={row.archive_date} className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
                  <td className="px-4 py-3 font-medium text-slate-900 dark:text-white">{row.archive_date}</td>
                  <td className="px-4 py-3 text-slate-600 dark:text-slate-400">{row.item_count}</td>
                  <td className="px-4 py-3 text-slate-600 dark:text-slate-400">{row.articles_created}</td>
                  <td className="px-4 py-3 text-slate-600 dark:text-slate-400">{categoryLabel(row.top_category)}</td>
                  <td className="px-4 py-3 font-mono text-slate-600 dark:text-slate-400">
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
        </SurfaceCard>
      )}
    </main>
  );
}
