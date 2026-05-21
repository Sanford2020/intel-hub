"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { ChevronLeft, ChevronRight, Loader2, Search, Sparkles } from "lucide-react";
import { listArticles, listSources } from "@/lib/intel-api";
import type { Article, Source } from "@/types/intel";
import { DEFAULT_MIN_RELEVANCE } from "@/types/intel";

function scoreBadgeClass(score: number): string {
  if (score >= 8) {
    return "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300";
  }
  if (score >= DEFAULT_MIN_RELEVANCE) {
    return "bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300";
  }
  return "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300";
}

export default function ArticlesPage() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [sources, setSources] = useState<Source[]>([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [sourceId, setSourceId] = useState(() => {
    if (typeof window === "undefined") return "";
    return new URLSearchParams(window.location.search).get("source_id") ?? "";
  });
  const [tag, setTag] = useState("");
  const [q, setQ] = useState("");
  const [hasReport, setHasReport] = useState("");
  const [todayPicks, setTodayPicks] = useState(false);
  const [publishedFrom, setPublishedFrom] = useState("");
  const [publishedTo, setPublishedTo] = useState("");

  const sourceNameById = useMemo(
    () => Object.fromEntries(sources.map((s) => [s.id, s.name])),
    [sources],
  );

  const selectedSourceName = sourceId ? sourceNameById[Number(sourceId)] : undefined;

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const articleRes = await listArticles({
        page,
        page_size: 20,
        source_id: sourceId ? Number(sourceId) : undefined,
        tag: tag || undefined,
        q: q || undefined,
        has_report: todayPicks
          ? true
          : hasReport === ""
            ? undefined
            : hasReport === "true",
        min_relevance: todayPicks ? DEFAULT_MIN_RELEVANCE : undefined,
        published_from: publishedFrom ? `${publishedFrom}T00:00:00Z` : undefined,
        published_to: publishedTo ? `${publishedTo}T23:59:59Z` : undefined,
      });
      setArticles(articleRes.data);
      setTotal(articleRes.total);
      setTotalPages(articleRes.total_pages);

      listSources(1, 100)
        .then((sourceRes) => setSources(sourceRes.data))
        .catch(() => undefined);
    } catch (e) {
      setError(e instanceof Error ? e.message : "加载失败");
      setArticles([]);
      setTotal(0);
      setTotalPages(0);
    } finally {
      setLoading(false);
    }
  }, [page, sourceId, tag, q, hasReport, todayPicks, publishedFrom, publishedTo]);

  useEffect(() => {
    load();
  }, [load]);

  function applyFilters(e: React.FormEvent) {
    e.preventDefault();
    setPage(1);
    load();
  }

  function toggleTodayPicks() {
    setTodayPicks((prev) => !prev);
    setPage(1);
  }

  return (
    <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold">资讯列表</h1>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            {loading
              ? "加载中…"
              : `共 ${total} 篇资讯${selectedSourceName ? ` · 来源：${selectedSourceName}` : ""}`}
            {" · "}按来源、标签、日期与 AI 报告状态筛选
          </p>
        </div>
        <button
          type="button"
          onClick={toggleTodayPicks}
          className={`inline-flex items-center gap-2 rounded-lg border px-4 py-2 text-sm font-medium transition-colors ${
            todayPicks
              ? "border-primary-600 bg-primary-600 text-white"
              : "border-gray-300 bg-white hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900 dark:hover:bg-gray-800"
          }`}
        >
          <Sparkles className="h-4 w-4" />
          今日精选（≥{DEFAULT_MIN_RELEVANCE}）
        </button>
      </div>

      {todayPicks && (
        <p className="mb-4 text-sm text-primary-700 dark:text-primary-300">
          仅显示 AI 相关度 ≥ {DEFAULT_MIN_RELEVANCE} 的已分析资讯，按相关度排序。
        </p>
      )}

      {error && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/30 dark:text-red-300">
          {error}
        </div>
      )}

      <form
        onSubmit={applyFilters}
        className="mb-6 grid gap-3 rounded-xl border p-4 dark:border-gray-800 sm:grid-cols-2 lg:grid-cols-3"
      >
        <select
          value={sourceId}
          onChange={(e) => setSourceId(e.target.value)}
          disabled={todayPicks}
          className="rounded-lg border bg-white px-3 py-2 text-sm disabled:opacity-60 dark:border-gray-700 dark:bg-gray-900"
        >
          <option value="">全部来源</option>
          {sources.map((s) => (
            <option key={s.id} value={s.id}>
              {s.name}
            </option>
          ))}
        </select>
        <input
          value={tag}
          onChange={(e) => setTag(e.target.value)}
          placeholder="标签 e.g. geopolitics"
          disabled={todayPicks}
          className="rounded-lg border px-3 py-2 text-sm disabled:opacity-60 dark:border-gray-700 dark:bg-gray-900"
        />
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="标题关键词"
          className="rounded-lg border px-3 py-2 text-sm dark:border-gray-700 dark:bg-gray-900"
        />
        <select
          value={hasReport}
          onChange={(e) => setHasReport(e.target.value)}
          disabled={todayPicks}
          className="rounded-lg border px-3 py-2 text-sm disabled:opacity-60 dark:border-gray-700 dark:bg-gray-900"
        >
          <option value="">报告：全部</option>
          <option value="true">已有 AI 报告</option>
          <option value="false">无报告</option>
        </select>
        <input
          type="date"
          value={publishedFrom}
          onChange={(e) => setPublishedFrom(e.target.value)}
          className="rounded-lg border px-3 py-2 text-sm dark:border-gray-700 dark:bg-gray-900"
        />
        <input
          type="date"
          value={publishedTo}
          onChange={(e) => setPublishedTo(e.target.value)}
          className="rounded-lg border px-3 py-2 text-sm dark:border-gray-700 dark:bg-gray-900"
        />
        <button
          type="submit"
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-primary-600 px-4 py-2 text-sm text-white hover:bg-primary-700 sm:col-span-2 lg:col-span-1"
        >
          <Search className="h-4 w-4" /> 筛选
        </button>
      </form>

      {loading ? (
        <div className="flex items-center gap-2 text-gray-500">
          <Loader2 className="h-4 w-4 animate-spin" /> 加载中…
        </div>
      ) : articles.length === 0 ? (
        <div className="rounded-xl border border-dashed p-8 text-center dark:border-gray-800">
          <p className="text-sm text-gray-500">
            {todayPicks
              ? "暂无达到精选阈值的资讯，可关闭「今日精选」查看全部。"
              : sourceId
                ? `来源「${selectedSourceName ?? `#${sourceId}`}」下暂无资讯。若刚采集完，请确认该源有 RSS 且采集日志 status=success、items_created>0。`
                : "暂无资讯。请先在「来源」页对 RSS 源（如 CISA Advisories）点「采集」。"}
          </p>
          {(todayPicks || sourceId) && (
            <button
              type="button"
              onClick={() => {
                setTodayPicks(false);
                setSourceId("");
                setPage(1);
              }}
              className="mt-4 text-sm font-medium text-primary-600 hover:underline"
            >
              清除筛选，查看全部 {total > 0 ? "" : "资讯"}
            </button>
          )}
          {!sourceId && !todayPicks && (
            <Link
              href="/sources"
              className="mt-4 inline-block text-sm font-medium text-primary-600 hover:underline"
            >
              前往来源管理 →
            </Link>
          )}
        </div>
      ) : (
        <ul className="space-y-3">
          {articles.map((a) => (
            <li key={a.id}>
              <Link
                href={`/articles/${a.id}`}
                className="block rounded-xl border p-4 transition-shadow hover:shadow-md dark:border-gray-800"
              >
                <div className="flex items-start justify-between gap-3">
                  <h2 className="font-semibold">{a.title}</h2>
                  {a.report && (
                    <span
                      className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-semibold ${scoreBadgeClass(a.report.relevance_score)}`}
                    >
                      {a.report.relevance_score.toFixed(1)}
                    </span>
                  )}
                </div>
                <p className="mt-1 text-xs text-gray-500">
                  {sourceNameById[a.source_id] ?? `Source #${a.source_id}`}
                  {a.published_at && ` · ${new Date(a.published_at).toLocaleDateString()}`}
                </p>
                {a.report ? (
                  <p className="mt-2 line-clamp-2 text-sm text-gray-600 dark:text-gray-400">
                    {a.report.summary}
                  </p>
                ) : (
                  <span className="mt-2 inline-block text-xs text-amber-600">待 AI 分析</span>
                )}
              </Link>
            </li>
          ))}
        </ul>
      )}

      {totalPages > 1 && (
        <div className="mt-6 flex items-center justify-center gap-4">
          <button
            disabled={page <= 1}
            onClick={() => setPage((p) => p - 1)}
            className="rounded-lg border p-2 disabled:opacity-40"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
          <span className="text-sm">
            {page} / {totalPages}
          </span>
          <button
            disabled={page >= totalPages}
            onClick={() => setPage((p) => p + 1)}
            className="rounded-lg border p-2 disabled:opacity-40"
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      )}
    </main>
  );
}
