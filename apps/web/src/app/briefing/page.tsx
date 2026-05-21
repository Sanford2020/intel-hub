"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import {
  AlertCircle,
  ExternalLink,
  Loader2,
  Newspaper,
  RefreshCw,
} from "lucide-react";
import { getDailyBriefing } from "@/lib/intel-api";
import type { DailyBriefing } from "@/types/intel";

const HOUR_OPTIONS = [24, 48, 72] as const;

function formatDateTime(value: string | null | undefined): string {
  if (!value) return "—";
  return new Date(value).toLocaleString("zh-CN", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function scoreBadgeClass(score: number): string {
  if (score >= 8) {
    return "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300";
  }
  if (score >= 6) {
    return "bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300";
  }
  return "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300";
}

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
      setError("加载简报失败，请确认后端 API 已启动。");
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
    <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <Newspaper className="h-7 w-7 text-primary-600" />
            <h1 className="text-2xl font-bold">每日情报简报</h1>
          </div>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            过去 {hours} 小时内、相关度 ≥{" "}
            {briefing?.meta.min_relevance?.toFixed(1) ?? "6.0"} 的已分析资讯
          </p>
          {briefing && (
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-500">
              时间窗：{formatDateTime(briefing.meta.window_start)} —{" "}
              {formatDateTime(briefing.meta.window_end)}
            </p>
          )}
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <div className="flex rounded-lg border dark:border-gray-700">
            {HOUR_OPTIONS.map((option) => (
              <button
                key={option}
                type="button"
                onClick={() => setHours(option)}
                className={`px-3 py-2 text-sm first:rounded-l-lg last:rounded-r-lg ${
                  hours === option
                    ? "bg-primary-600 text-white"
                    : "bg-white text-gray-700 hover:bg-gray-50 dark:bg-gray-900 dark:text-gray-300 dark:hover:bg-gray-800"
                }`}
              >
                {option}h
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

      {briefing?.meta.ai_mode === "mock" && (
        <div className="mb-6 flex items-start gap-3 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900 dark:border-amber-900/50 dark:bg-amber-950/30 dark:text-amber-200">
          <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
          <span>当前为 Mock AI 分析模式，摘要与相关度仅供演示。</span>
        </div>
      )}

      {loading && (
        <div className="flex items-center justify-center py-24 text-gray-500">
          <Loader2 className="mr-2 h-6 w-6 animate-spin" />
          加载简报中…
        </div>
      )}

      {!loading && error && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-center dark:border-red-900/50 dark:bg-red-950/20">
          <p className="text-red-700 dark:text-red-300">{error}</p>
          <button
            type="button"
            onClick={load}
            className="mt-4 rounded-lg bg-red-600 px-4 py-2 text-sm text-white hover:bg-red-700"
          >
            重试
          </button>
        </div>
      )}

      {!loading && !error && briefing && (
        <>
          <section className="mb-8 rounded-xl border bg-white p-6 dark:border-gray-800 dark:bg-gray-900/50">
            <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-gray-500">
              总览
            </h2>
            <p className="text-base leading-relaxed text-gray-800 dark:text-gray-200">
              {briefing.overview}
            </p>
          </section>

          {briefing.items.length === 0 ? (
            <div className="rounded-xl border border-dashed p-12 text-center dark:border-gray-700">
              <p className="text-gray-600 dark:text-gray-400">
                暂无已分析资讯。请先采集来源并运行 AI 分析。
              </p>
              <div className="mt-4 flex justify-center gap-4 text-sm">
                <Link href="/sources" className="text-primary-600 hover:underline">
                  管理来源
                </Link>
                <Link href="/articles" className="text-primary-600 hover:underline">
                  浏览资讯
                </Link>
              </div>
            </div>
          ) : (
            <ol className="space-y-4">
              {briefing.items.map((item) => {
                const isExpanded = expanded[item.article_id];
                const summary =
                  isExpanded || item.summary.length <= 280
                    ? item.summary
                    : `${item.summary.slice(0, 280)}…`;

                return (
                  <li
                    key={item.article_id}
                    className="rounded-xl border bg-white p-5 dark:border-gray-800 dark:bg-gray-900/50"
                  >
                    <div className="flex flex-wrap items-start justify-between gap-3">
                      <div className="min-w-0 flex-1">
                        <div className="mb-1 flex flex-wrap items-center gap-2 text-xs text-gray-500">
                          <span className="font-mono">#{item.rank}</span>
                          <span>{item.source_name}</span>
                          <span>{formatDateTime(item.published_at)}</span>
                        </div>
                        <h3 className="text-lg font-semibold leading-snug">
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
                              className="ml-2 inline-flex align-middle text-gray-400 hover:text-primary-600"
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
                            className="rounded-full bg-gray-100 px-2.5 py-0.5 text-xs text-gray-700 dark:bg-gray-800 dark:text-gray-300"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}

                    <p className="mt-3 text-sm leading-relaxed text-gray-700 dark:text-gray-300">
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
                  </li>
                );
              })}
            </ol>
          )}
        </>
      )}
    </main>
  );
}
