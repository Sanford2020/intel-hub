"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { ArrowLeft, Cpu, ExternalLink } from "lucide-react";
import {
  analyzeArticle,
  getArticle,
  getArticleReport,
} from "@/lib/intel-api";
import type { Article, IntelligenceReport } from "@/types/intel";
import { SurfaceCard } from "@/components/ui/SurfaceCard";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { LoadingBlock } from "@/components/ui/LoadingBlock";
import { scoreBadgeClass } from "@/lib/intel-ui";

export default function ArticleDetailPage() {
  const params = useParams();
  const id = Number(params.id);

  const [article, setArticle] = useState<Article | null>(null);
  const [report, setReport] = useState<IntelligenceReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const a = await getArticle(id);
      setArticle(a);
      if (a.report) {
        setReport({
          id: 0,
          article_id: id,
          summary: a.report.summary,
          tags: a.report.tags,
          entities: [],
          relevance_score: a.report.relevance_score,
          sentiment: null,
          language: a.language,
          model: null,
          created_at: a.updated_at,
          updated_at: a.updated_at,
        });
      } else {
        try {
          const r = await getArticleReport(id);
          setReport(r.data);
        } catch {
          setReport(null);
        }
      }
    } catch (e) {
      const msg = e instanceof Error ? e.message : "加载失败";
      setError(msg.includes("Internal Server Error") || msg.includes("Failed to fetch") ? "无法连接后端服务，请确认 API 已启动" : msg);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    if (!Number.isNaN(id)) load();
  }, [id, load]);

  async function runAnalyze() {
    setAnalyzing(true);
    try {
      const res = await analyzeArticle(id);
      setReport(res.data);
      await load();
    } catch (e) {
      const msg = e instanceof Error ? e.message : "分析失败";
      setError(msg.includes("Internal Server Error") ? "后端服务异常，请稍后重试" : msg);
    } finally {
      setAnalyzing(false);
    }
  }

  if (loading) {
    return (
      <main className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
        <LoadingBlock lines={5} />
      </main>
    );
  }

  if (error && !article) {
    return (
      <main className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
        <ErrorBanner message={error} onRetry={load} />
        <Link href="/articles" className="mt-4 inline-block text-sm text-primary-600 hover:underline">
          ← 返回列表
        </Link>
      </main>
    );
  }

  if (!article) return null;

  return (
    <main className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
      <Link
        href="/articles"
        className="mb-6 inline-flex items-center gap-1 text-sm text-slate-500 hover:text-slate-800 dark:hover:text-slate-200"
      >
        <ArrowLeft className="h-4 w-4" /> 返回资讯列表
      </Link>

      <SurfaceCard padding="lg">
        <h1 className="text-2xl font-bold leading-snug text-slate-950 dark:text-white">{article.title}</h1>
        <div className="mt-2 flex flex-wrap gap-3 text-xs text-slate-500">
          <span>来源 #{article.source_id}</span>
          {article.published_at && (
            <span>{new Date(article.published_at).toLocaleString()}</span>
          )}
          {article.url && (
            <a
              href={article.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-primary-600 hover:underline"
            >
              原文 <ExternalLink className="h-3 w-3" />
            </a>
          )}
        </div>
        {article.content && (
          <p className="mt-6 whitespace-pre-wrap text-sm leading-relaxed text-slate-700 dark:text-slate-300">
            {article.content}
          </p>
        )}
      </SurfaceCard>

      <SurfaceCard className="mt-5" padding="lg">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="flex items-center gap-2 font-semibold text-slate-950 dark:text-white">
            <Cpu className="h-5 w-5 text-primary-600" /> AI 情报摘要
          </h2>
          <button
            onClick={runAnalyze}
            disabled={analyzing}
            className="primary-action"
          >
            {analyzing ? "分析中…" : report ? "重新分析" : "开始分析"}
          </button>
        </div>

        {report ? (
          <>
            <p className="text-sm leading-relaxed text-slate-700 dark:text-slate-300">{report.summary}</p>
            <div className="mt-4 flex flex-wrap gap-2">
              {report.tags.map((t) => (
                <span
                  key={t}
                  className="rounded-md bg-primary-50 px-2 py-0.5 text-xs text-primary-700 dark:bg-primary-900/30 dark:text-primary-300"
                >
                  {t}
                </span>
              ))}
            </div>
            <div className="mt-4 flex items-center gap-2 text-xs text-slate-500">
              <span className={`rounded-full px-2 py-0.5 font-semibold ${scoreBadgeClass(report.relevance_score)}`}>
                {report.relevance_score.toFixed(1)}
              </span>
              <span>/ 10</span>
              {report.model && <span>· {report.model}</span>}
            </div>
          </>
        ) : (
          <p className="text-sm text-slate-500">尚无 AI 报告，点击「开始分析」生成。</p>
        )}
      </SurfaceCard>
    </main>
  );
}
