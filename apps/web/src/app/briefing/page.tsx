"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { AlertCircle, ExternalLink, RefreshCw } from "lucide-react";
import { getDailyBriefing } from "@/lib/intel-api";
import type { DailyBriefing } from "@/types/intel";
import { PageHeader } from "@/components/ui/PageHeader";
import { SurfaceCard } from "@/components/ui/SurfaceCard";
import { SegmentedControl } from "@/components/ui/SegmentedControl";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { LoadingBlock } from "@/components/ui/LoadingBlock";
import { EmptyState } from "@/components/ui/EmptyState";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { scoreBadgeClass } from "@/lib/intel-ui";
import { formatDateTimeZh } from "@/lib/format";

const HOUR_OPTIONS = [
  { value: 24, label: "24h" },
  { value: 48, label: "48h" },
  { value: 72, label: "72h" },
];

export default function BriefingPage() {
  const [briefing, setBriefing] = useState<DailyBriefing | null>(null);
  const [hours, setHours] = useState<number>(24);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<Record<number, boolean>>({});

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getDailyBriefing({ hours, limit: 20 });
      setBriefing(res.data);
    } catch {
      setError("无法连接后端服务，请确认 API 已启动");
      setBriefing(null);
    } finally {
      setLoading(false);
    }
  }, [hours]);

  useEffect(() => {
    load();
  }, [load]);

  function toggleExpand(articleId: number) {
    setExpanded((prev) => ({ ...prev, [articleId]: !prev[articleId] }));
  }

  return (
    <main className="app-shell">
      <PageHeader
        title="每日情报简报"
        description={`过去 ${hours} 小时内、相关度 ≥ ${briefing?.meta.min_relevance?.toFixed(1) ?? "6.0"} 的已分析资讯`}
        meta={
          briefing ? (
            <p className="text-xs text-slate-500">
              时间窗：{formatDateTimeZh(briefing.meta.window_start ?? "")} —{" "}
              {formatDateTimeZh(briefing.meta.window_end ?? "")}
            </p>
          ) : undefined
        }
        actions={
          <div className="flex flex-wrap items-center gap-2">
            <SegmentedControl options={HOUR_OPTIONS} value={hours} onChange={setHours} />
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

      {briefing?.meta.ai_mode === "mock" && (
        <div className="mt-5 flex items-start gap-3 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900 dark:border-amber-900/50 dark:bg-amber-950/30 dark:text-amber-200">
          <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
          <span>当前为 Mock AI 分析模式，摘要与相关度仅供演示。</span>
        </div>
      )}

      {loading && (
        <div className="mt-6">
          <LoadingBlock lines={5} />
        </div>
      )}

      {!loading && error && (
        <div className="mt-6">
          <ErrorBanner message={error} onRetry={load} />
        </div>
      )}

      {!loading && !error && briefing && (
        <div className="mt-6 space-y-6">
          <SurfaceCard>
            <div className="mb-2 flex items-center gap-2">
              <h2 className="text-xs font-semibold uppercase tracking-wide text-slate-500">总览</h2>
              {briefing.meta.ai_mode && (
                <StatusBadge
                  tone={briefing.meta.ai_mode === "mock" ? "warning" : "success"}
                  label={briefing.meta.ai_mode === "mock" ? "Mock" : "AI"}
                  dot={false}
                />
              )}
            </div>
            <p className="text-base leading-relaxed text-slate-800 dark:text-slate-200">
              {briefing.overview}
            </p>
          </SurfaceCard>

          {briefing.items.length === 0 ? (
            <EmptyState
              title="暂无已分析资讯"
              description="请先采集来源并运行 AI 分析"
              action={
                <div className="flex gap-4 text-sm">
                  <Link href="/sources" className="text-primary-600 hover:underline">管理来源</Link>
                  <Link href="/articles" className="text-primary-600 hover:underline">浏览资讯</Link>
                </div>
              }
            />
          ) : (
            <ol className="space-y-3">
              {briefing.items.map((item) => {
                const isExpanded = expanded[item.article_id];
                const summary =
                  isExpanded || item.summary.length <= 280
                    ? item.summary
                    : `${item.summary.slice(0, 280)}…`;

                return (
                  <li key={item.article_id}>
                    <SurfaceCard>
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <div className="min-w-0 flex-1">
                          <div className="mb-1 flex flex-wrap items-center gap-2 text-xs text-slate-500">
                            <span className="font-mono">#{item.rank}</span>
                            <span>{item.source_name}</span>
                            <span>{formatDateTimeZh(item.published_at ?? "")}</span>
                          </div>
                          <h3 className="text-base font-semibold leading-snug sm:text-lg">
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
                                aria-label="打开原文"
                              >
                                <ExternalLink className="h-4 w-4" />
                              </a>
                            )}
                          </h3>
                        </div>
                        <span
                          className={`shrink-0 rounded-full px-2.5 py-1 text-xs font-semibold ${scoreBadgeClass(item.relevance_score)}`}
                        >
                          {item.relevance_score.toFixed(1)}
                        </span>
                      </div>

                      {item.tags.length > 0 && (
                        <div className="mt-3 flex flex-wrap gap-2">
                          {item.tags.map((tag) => (
                            <span
                              key={tag}
                              className="rounded-md bg-slate-100 px-2 py-0.5 text-xs text-slate-700 dark:bg-slate-800 dark:text-slate-300"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}

                      <p className="mt-3 text-sm leading-relaxed text-slate-700 dark:text-slate-300">
                        {summary}
                      </p>
                      {item.summary.length > 280 && (
                        <button
                          type="button"
                          onClick={() => toggleExpand(item.article_id)}
                          className="mt-2 text-xs text-primary-600 hover:underline dark:text-primary-400"
                        >
                          {isExpanded ? "收起" : "展开全文"}
                        </button>
                      )}
                    </SurfaceCard>
                  </li>
                );
              })}
            </ol>
          )}
        </div>
      )}
    </main>
  );
}
