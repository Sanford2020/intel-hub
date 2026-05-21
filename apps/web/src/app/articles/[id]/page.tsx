"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { ArrowLeft, Cpu, ExternalLink, Loader2 } from "lucide-react";
import {
  analyzeArticle,
  getArticle,
  getArticleReport,
} from "@/lib/intel-api";
import type { Article, IntelligenceReport } from "@/types/intel";

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
      setError(e instanceof Error ? e.message : "加载失败");
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
      setError(e instanceof Error ? e.message : "分析失败");
    } finally {
      setAnalyzing(false);
    }
  }

  if (loading) {
    return (
      <main className="mx-auto flex max-w-3xl items-center gap-2 px-4 py-16 text-gray-500">
        <Loader2 className="h-4 w-4 animate-spin" /> 加载中…
      </main>
    );
  }

  if (error && !article) {
    return (
      <main className="mx-auto max-w-3xl px-4 py-16">
        <p className="text-red-600">{error}</p>
        <Link href="/articles" className="mt-4 inline-block text-sm text-primary-600">
          返回列表
        </Link>
      </main>
    );
  }

  if (!article) return null;

  return (
    <main className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
      <Link
        href="/articles"
        className="mb-6 inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-800"
      >
        <ArrowLeft className="h-4 w-4" /> 返回资讯列表
      </Link>

      <article className="rounded-xl border p-6 dark:border-gray-800">
        <h1 className="text-2xl font-bold leading-snug">{article.title}</h1>
        <div className="mt-2 flex flex-wrap gap-3 text-xs text-gray-500">
          <span>Source #{article.source_id}</span>
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
          <p className="mt-6 whitespace-pre-wrap text-sm leading-relaxed text-gray-700 dark:text-gray-300">
            {article.content}
          </p>
        )}
      </article>

      <section className="mt-6 rounded-xl border p-6 dark:border-gray-800">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="flex items-center gap-2 font-semibold">
            <Cpu className="h-5 w-5 text-primary-600" /> AI 情报摘要
          </h2>
          <button
            onClick={runAnalyze}
            disabled={analyzing}
            className="rounded-lg bg-primary-600 px-3 py-1.5 text-sm text-white hover:bg-primary-700 disabled:opacity-50"
          >
            {analyzing ? "分析中…" : report ? "重新分析" : "开始分析"}
          </button>
        </div>

        {report ? (
          <>
            <p className="text-sm leading-relaxed">{report.summary}</p>
            <div className="mt-4 flex flex-wrap gap-2">
              {report.tags.map((t) => (
                <span
                  key={t}
                  className="rounded-full bg-primary-50 px-2 py-0.5 text-xs text-primary-700 dark:bg-primary-900/30 dark:text-primary-300"
                >
                  {t}
                </span>
              ))}
            </div>
            <p className="mt-4 text-xs text-gray-500">
              相关度 {report.relevance_score.toFixed(1)} / 10
              {report.model && ` · ${report.model}`}
            </p>
          </>
        ) : (
          <p className="text-sm text-gray-500">尚无 AI 报告，点击「开始分析」生成。</p>
        )}
      </section>
    </main>
  );
}
