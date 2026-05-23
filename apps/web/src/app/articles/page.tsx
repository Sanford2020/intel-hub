"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { Search, Sparkles } from "lucide-react";
import { listArticles, listSources } from "@/lib/intel-api";
import type { Article, Source } from "@/types/intel";
import { DEFAULT_MIN_RELEVANCE } from "@/types/intel";
import { PageHeader } from "@/components/ui/PageHeader";
import { SurfaceCard } from "@/components/ui/SurfaceCard";
import { Pagination } from "@/components/ui/Pagination";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { LoadingBlock } from "@/components/ui/LoadingBlock";
import { EmptyState } from "@/components/ui/EmptyState";
import { scoreBadgeClass } from "@/lib/intel-ui";

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
      const msg = e instanceof Error ? e.message : "加载失败";
      setError(msg.includes("Internal Server Error") || msg.includes("Failed to fetch") ? "无法连接后端服务，请确认 API 已启动" : msg);
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
    <main className="app-shell min-w-0">
      <PageHeader
        title="资讯列表"
        description={
          loading
            ? "加载中…"
            : `共 ${total} 篇资讯${selectedSourceName ? ` · 来源：${selectedSourceName}` : ""} · 按来源、标签、日期与 AI 报告状态筛选`
        }
        actions={
          <button
            type="button"
            onClick={toggleTodayPicks}
            className={`inline-flex items-center gap-2 rounded-lg border px-4 py-2 text-sm font-medium transition-colors ${
              todayPicks
                ? "border-primary-600 bg-primary-600 text-white"
                : "border-slate-300 bg-white hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 dark:hover:bg-slate-800"
            }`}
          >
            <Sparkles className="h-4 w-4" />
            今日精选（≥{DEFAULT_MIN_RELEVANCE}）
          </button>
        }
      />

      {todayPicks && (
        <p className="mt-4 text-sm text-primary-700 dark:text-primary-300">
          仅显示 AI 相关度 ≥ {DEFAULT_MIN_RELEVANCE} 的已分析资讯，按相关度排序。
        </p>
      )}

      {error && (
        <div className="mt-4">
          <ErrorBanner message={error} onRetry={load} />
        </div>
      )}

      <SurfaceCard className="mt-5" padding="sm">
        <form
          onSubmit={applyFilters}
          className="grid min-w-0 gap-3 sm:grid-cols-2 lg:grid-cols-3"
        >
          <select value={sourceId} onChange={(e) => setSourceId(e.target.value)} disabled={todayPicks} className="field w-full min-w-0">
            <option value="">全部来源</option>
            {sources.map((s) => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>
          <input value={tag} onChange={(e) => setTag(e.target.value)} placeholder="标签 e.g. geopolitics" disabled={todayPicks} className="field w-full min-w-0" />
          <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="标题关键词" className="field w-full min-w-0" />
          <select value={hasReport} onChange={(e) => setHasReport(e.target.value)} disabled={todayPicks} className="field w-full min-w-0">
            <option value="">报告：全部</option>
            <option value="true">已有 AI 报告</option>
            <option value="false">无报告</option>
          </select>
          <input type="date" value={publishedFrom} onChange={(e) => setPublishedFrom(e.target.value)} className="field w-full min-w-0" />
          <input type="date" value={publishedTo} onChange={(e) => setPublishedTo(e.target.value)} className="field w-full min-w-0" />
          <button type="submit" className="primary-action w-full min-w-0 sm:col-span-2 lg:col-span-1">
            <Search className="h-4 w-4" /> 筛选
          </button>
        </form>
      </SurfaceCard>

      <div className="mt-5">
        {loading ? (
          <LoadingBlock lines={4} />
        ) : articles.length === 0 ? (
          <EmptyState
            title={
              todayPicks
                ? "暂无达到精选阈值的资讯"
                : sourceId
                  ? `来源「${selectedSourceName ?? `#${sourceId}`}」下暂无资讯`
                  : "暂无资讯"
            }
            description={
              todayPicks
                ? "可关闭「今日精选」查看全部"
                : sourceId
                  ? "若刚采集完，请确认该源有 RSS 且采集日志 status=success"
                  : "请先在「来源」页对 RSS 源点「采集」"
            }
            action={
              todayPicks || sourceId ? (
                <button
                  type="button"
                  onClick={() => { setTodayPicks(false); setSourceId(""); setPage(1); }}
                  className="text-sm font-medium text-primary-600 hover:underline"
                >
                  清除筛选，查看全部
                </button>
              ) : (
                <Link href="/sources" className="text-sm font-medium text-primary-600 hover:underline">
                  前往来源管理 →
                </Link>
              )
            }
          />
        ) : (
          <ul className="space-y-3">
            {articles.map((a) => (
              <li key={a.id}>
                <SurfaceCard padding="sm">
                  <Link href={`/articles/${a.id}`} className="block">
                    <div className="flex items-start justify-between gap-3">
                      <h2 className="font-semibold text-slate-950 dark:text-white">{a.title}</h2>
                      {a.report && (
                        <span className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-semibold ${scoreBadgeClass(a.report.relevance_score)}`}>
                          {a.report.relevance_score.toFixed(1)}
                        </span>
                      )}
                    </div>
                    <p className="mt-1 text-xs text-slate-500">
                      {sourceNameById[a.source_id] ?? `来源 #${a.source_id}`}
                      {a.published_at && ` · ${new Date(a.published_at).toLocaleDateString()}`}
                    </p>
                    {a.report ? (
                      <p className="mt-2 line-clamp-2 text-sm text-slate-600 dark:text-slate-400">
                        {a.report.summary}
                      </p>
                    ) : (
                      <span className="mt-2 inline-block text-xs text-amber-600 dark:text-amber-400">待 AI 分析</span>
                    )}
                  </Link>
                </SurfaceCard>
              </li>
            ))}
          </ul>
        )}
      </div>

      {totalPages > 1 && (
        <div className="mt-6 flex justify-center">
          <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />
        </div>
      )}
    </main>
  );
}
