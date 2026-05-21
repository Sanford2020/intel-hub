"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { ArrowLeft, ExternalLink, Loader2 } from "lucide-react";
import { getArchive } from "@/lib/intel-api";
import type { ArchiveDetail, BriefingItem } from "@/types/intel";

const CATEGORY_LABELS: Record<string, string> = {
  wire: "通讯社/主流",
  geopolitical: "地缘/OSINT",
  cyber: "网络安全",
  social: "社交/UGC",
  aggregator: "聚合/API",
};

function formatDateTime(value: string | null | undefined): string {
  if (!value) return "—";
  return new Date(value).toLocaleString("zh-CN", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

interface CategoryHeatRow {
  category: string;
  category_label?: string;
  articles: number;
  high_relevance: number;
  avg_relevance: number;
  heat_score: number;
}

export default function ArchiveDetailPage({ params }: { params: { date: string } }) {
  const [archive, setArchive] = useState<ArchiveDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getArchive(params.date);
      setArchive(res.data);
    } catch {
      setError(`未找到 ${params.date} 的归档记录。`);
      setArchive(null);
    } finally {
      setLoading(false);
    }
  }, [params.date]);

  useEffect(() => {
    load();
  }, [load]);

  const categoryHeat = (archive?.metrics?.category_heat as CategoryHeatRow[] | undefined) ?? [];
  const briefingItems = (archive?.briefing?.items as BriefingItem[] | undefined) ?? [];
  const maxHeat = Math.max(...categoryHeat.map((r) => r.heat_score), 1);

  return (
    <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <Link
        href="/archives"
        className="mb-6 inline-flex items-center gap-2 text-sm text-gray-600 hover:text-primary-600 dark:text-gray-400"
      >
        <ArrowLeft className="h-4 w-4" />
        返回归档列表
      </Link>

      {loading && (
        <div className="flex items-center justify-center py-24 text-gray-500">
          <Loader2 className="mr-2 h-6 w-6 animate-spin" />
          加载归档详情…
        </div>
      )}

      {!loading && error && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-center dark:border-red-900/50 dark:bg-red-950/20">
          <p className="text-red-700 dark:text-red-300">{error}</p>
        </div>
      )}

      {!loading && archive && (
        <>
          <header className="mb-8">
            <h1 className="text-2xl font-bold">{archive.archive_date} 归档</h1>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
              时区 {archive.timezone} · 窗口 {formatDateTime(archive.window_start)} —{" "}
              {formatDateTime(archive.window_end)}
            </p>
          </header>

          {categoryHeat.length > 0 && (
            <section className="mb-8 rounded-xl border bg-white p-6 dark:border-gray-800 dark:bg-gray-900/50">
              <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-gray-500">
                业务分类热度
              </h2>
              <ul className="space-y-3">
                {categoryHeat.slice(0, 12).map((row) => (
                  <li key={row.category}>
                    <div className="mb-1 flex justify-between text-sm">
                      <span>
                        {row.category_label || CATEGORY_LABELS[row.category] || row.category}
                      </span>
                      <span className="font-mono font-semibold">{row.heat_score.toFixed(1)}</span>
                    </div>
                    <div className="h-2 overflow-hidden rounded-full bg-gray-100 dark:bg-gray-800">
                      <div
                        className="h-full rounded-full bg-primary-500"
                        style={{ width: `${(row.heat_score / maxHeat) * 100}%` }}
                      />
                    </div>
                    <p className="mt-0.5 text-xs text-gray-500">
                      {row.articles} 篇 · 高相关 {row.high_relevance} · 均分{" "}
                      {row.avg_relevance.toFixed(1)}
                    </p>
                  </li>
                ))}
              </ul>
            </section>
          )}

          {archive.briefing?.overview && (
            <section className="mb-8 rounded-xl border bg-white p-6 dark:border-gray-800 dark:bg-gray-900/50">
              <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-gray-500">
                简报总览
              </h2>
              <p className="leading-relaxed text-gray-800 dark:text-gray-200">
                {archive.briefing.overview}
              </p>
            </section>
          )}

          {briefingItems.length > 0 && (
            <section>
              <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-gray-500">
                简报条目 ({briefingItems.length})
              </h2>
              <ol className="space-y-3">
                {briefingItems.map((item) => (
                  <li
                    key={item.article_id}
                    className="rounded-xl border bg-white p-4 dark:border-gray-800 dark:bg-gray-900/50"
                  >
                    <div className="flex flex-wrap items-start justify-between gap-2">
                      <div>
                        <p className="text-xs text-gray-500">
                          #{item.rank} · {item.source_name}
                        </p>
                        <h3 className="font-semibold">
                          <Link
                            href={`/articles/${item.article_id}`}
                            className="hover:text-primary-600"
                          >
                            {item.title}
                          </Link>
                          {item.url && (
                            <a
                              href={item.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="ml-2 inline-flex align-middle text-gray-400"
                            >
                              <ExternalLink className="h-4 w-4" />
                            </a>
                          )}
                        </h3>
                      </div>
                      <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-semibold text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300">
                        {item.relevance_score.toFixed(1)}
                      </span>
                    </div>
                    <p className="mt-2 line-clamp-3 text-sm text-gray-700 dark:text-gray-300">
                      {item.summary}
                    </p>
                  </li>
                ))}
              </ol>
            </section>
          )}
        </>
      )}
    </main>
  );
}
