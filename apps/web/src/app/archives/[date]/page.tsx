"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { ArrowLeft, ExternalLink } from "lucide-react";
import { getArchive } from "@/lib/intel-api";
import type { ArchiveDetail, BriefingItem } from "@/types/intel";
import { PageHeader } from "@/components/ui/PageHeader";
import { SurfaceCard } from "@/components/ui/SurfaceCard";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { LoadingBlock } from "@/components/ui/LoadingBlock";
import { categoryLabel } from "@/lib/intel-labels";
import { scoreBadgeClass } from "@/lib/intel-ui";
import { formatDateTimeZh } from "@/lib/format";

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
      setError(`未找到 ${params.date} 的归档记录`);
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
    <main className="app-shell">
      <Link
        href="/archives"
        className="mb-6 inline-flex items-center gap-2 text-sm text-slate-500 hover:text-primary-600 dark:text-slate-400"
      >
        <ArrowLeft className="h-4 w-4" />
        返回归档列表
      </Link>

      {loading && <LoadingBlock lines={5} />}

      {!loading && error && <ErrorBanner message={error} onRetry={load} />}

      {!loading && archive && (
        <div className="space-y-6">
          <PageHeader
            title={`${archive.archive_date} 归档`}
            description={`时区 ${archive.timezone} · 窗口 ${formatDateTimeZh(archive.window_start ?? "")} — ${formatDateTimeZh(archive.window_end ?? "")}`}
          />

          {categoryHeat.length > 0 && (
            <SurfaceCard>
              <h2 className="mb-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                业务分类热度
              </h2>
              <ul className="space-y-3">
                {categoryHeat.slice(0, 12).map((row) => (
                  <li key={row.category}>
                    <div className="mb-1 flex justify-between text-sm">
                      <span className="text-slate-700 dark:text-slate-300">
                        {row.category_label || categoryLabel(row.category)}
                      </span>
                      <span className="font-mono font-semibold text-slate-900 dark:text-white">{row.heat_score.toFixed(1)}</span>
                    </div>
                    <div className="h-2 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
                      <div
                        className="h-full rounded-full bg-primary-500"
                        style={{ width: `${(row.heat_score / maxHeat) * 100}%` }}
                      />
                    </div>
                    <p className="mt-0.5 text-xs text-slate-500">
                      {row.articles} 篇 · 高相关 {row.high_relevance} · 均分{" "}
                      {row.avg_relevance.toFixed(1)}
                    </p>
                  </li>
                ))}
              </ul>
            </SurfaceCard>
          )}

          {archive.briefing?.overview && (
            <SurfaceCard>
              <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
                简报总览
              </h2>
              <p className="leading-relaxed text-slate-800 dark:text-slate-200">
                {archive.briefing.overview}
              </p>
            </SurfaceCard>
          )}

          {briefingItems.length > 0 && (
            <section>
              <h2 className="mb-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                简报条目 ({briefingItems.length})
              </h2>
              <ol className="space-y-3">
                {briefingItems.map((item) => (
                  <li key={item.article_id}>
                    <SurfaceCard padding="sm">
                      <div className="flex flex-wrap items-start justify-between gap-2">
                        <div className="min-w-0 flex-1">
                          <p className="text-xs text-slate-500">
                            #{item.rank} · {item.source_name}
                          </p>
                          <h3 className="font-semibold text-slate-900 dark:text-white">
                            <Link
                              href={`/articles/${item.article_id}`}
                              className="hover:text-primary-600 dark:hover:text-primary-400"
                            >
                              {item.title}
                            </Link>
                            {item.url && (
                              <a
                                href={item.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="ml-2 inline-flex align-middle text-slate-400 hover:text-primary-600"
                              >
                                <ExternalLink className="h-4 w-4" />
                              </a>
                            )}
                          </h3>
                        </div>
                        <span className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-semibold ${scoreBadgeClass(item.relevance_score)}`}>
                          {item.relevance_score.toFixed(1)}
                        </span>
                      </div>
                      <p className="mt-2 line-clamp-3 text-sm text-slate-700 dark:text-slate-300">
                        {item.summary}
                      </p>
                    </SurfaceCard>
                  </li>
                ))}
              </ol>
            </section>
          )}
        </div>
      )}
    </main>
  );
}
