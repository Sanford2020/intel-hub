"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  ChevronLeft,
  ChevronRight,
  FileText,
  Loader2,
  Play,
  RadioTower,
  ScrollText,
} from "lucide-react";
import { ingestSource, listIngestLogs, listSources, updateSource } from "@/lib/intel-api";
import type { IngestLog, Source } from "@/types/intel";

const PAGE_SIZE = 20;

type PendingIngest = {
  prevIngestedAt: string | null;
  logCount: number;
};

const INGESTIBLE_TYPES = new Set(["rss", "x", "reddit", "hn", "polymarket", "aihot", "apify"]);

const TYPE_LABELS: Record<string, string> = {
  rss: "RSS",
  x: "X",
  reddit: "Reddit",
  hn: "HN",
  polymarket: "Polymarket",
  aihot: "AI HOT",
  apify: "Apify",
};

function isIngestible(source: Source): boolean {
  return source.enabled && INGESTIBLE_TYPES.has(source.source_type) && Boolean(source.url);
}

function ingestSkipReason(source: Source): string {
  const reasons: string[] = [];
  if (!source.enabled) reasons.push("来源未启用");
  if (!INGESTIBLE_TYPES.has(source.source_type)) {
    reasons.push(`类型为 ${source.source_type}，仅支持 ${Object.values(TYPE_LABELS).join(" / ")}`);
  }
  if (!source.url) reasons.push("未配置 URL / 账号 / 搜索词");
  return reasons.join("；");
}

export default function SourcesPage() {
  const [sources, setSources] = useState<Source[]>([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [tierFilter, setTierFilter] = useState<string>("");
  const [enabledFilter, setEnabledFilter] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState<number | null>(null);
  const [ingestingId, setIngestingId] = useState<number | null>(null);
  const [pendingIngest, setPendingIngest] = useState<Map<number, PendingIngest>>(new Map());
  const [ingestNotice, setIngestNotice] = useState<string | null>(null);
  const [logsSource, setLogsSource] = useState<Source | null>(null);
  const [logs, setLogs] = useState<IngestLog[]>([]);
  const [logsLoading, setLogsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const pendingRef = useRef(pendingIngest);
  const logsSourceRef = useRef(logsSource);

  pendingRef.current = pendingIngest;
  logsSourceRef.current = logsSource;

  const sourceFilters = useMemo(() => ({
    tier: tierFilter === "" ? undefined : Number(tierFilter),
    enabled: enabledFilter === "" ? undefined : enabledFilter === "true",
  }), [tierFilter, enabledFilter]);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await listSources(page, PAGE_SIZE, sourceFilters);
      setSources(res.data);
      setTotal(res.total);
      setTotalPages(res.total_pages);
    } catch (e) {
      const msg = e instanceof Error ? e.message : "加载失败";
      setError(msg.includes("Internal Server Error") || msg.includes("Failed to fetch") ? "无法连接后端服务，请确认 API 已启动" : msg);
    } finally {
      setLoading(false);
    }
  }, [page, sourceFilters]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    if (pendingIngest.size === 0) return;

    let cancelled = false;

    const poll = async () => {
      const current = pendingRef.current;
      if (current.size === 0 || cancelled) return;

      try {
        const res = await listSources(page, PAGE_SIZE, sourceFilters);
        if (cancelled) return;

        setSources(res.data);
        setTotal(res.total);
        setTotalPages(res.total_pages);

        const next = new Map(current);
        for (const [sourceId, pending] of current) {
          const updated = res.data.find((s) => s.id === sourceId);
          if (updated && updated.last_ingested_at !== pending.prevIngestedAt) {
            next.delete(sourceId);
            continue;
          }
          const logsRes = await listIngestLogs(sourceId);
          if (cancelled) return;
          if (logsRes.total > pending.logCount) {
            next.delete(sourceId);
            if (logsSourceRef.current?.id === sourceId) {
              setLogs(logsRes.data);
            }
          }
        }

        if (next.size === 0) {
          setIngestNotice(null);
        }
        setPendingIngest((prev) => (next.size === prev.size ? prev : next));
      } catch {
        // keep polling; user can refresh manually
      }
    };

    const interval = setInterval(poll, 3000);
    poll();
    const timeout = setTimeout(() => {
      setPendingIngest(new Map());
      setIngestNotice(null);
    }, 120_000);

    return () => {
      cancelled = true;
      clearInterval(interval);
      clearTimeout(timeout);
    };
  }, [pendingIngest.size, page, sourceFilters]);

  async function toggleEnabled(source: Source) {
    setBusyId(source.id);
    try {
      await updateSource(source.id, { enabled: !source.enabled });
      await load();
    } finally {
      setBusyId(null);
    }
  }

  async function runIngest(source: Source) {
    if (!isIngestible(source)) {
      setError(`${source.name} 无法采集：${ingestSkipReason(source)}`);
      return;
    }

    setIngestingId(source.id);
    setError(null);
    try {
      const result = await ingestSource(source.id);
      if (result.status === "queued") {
        const logsBefore = await listIngestLogs(source.id).catch(() => ({ total: 0 }));
        setPendingIngest((prev) =>
          new Map(prev).set(source.id, {
            prevIngestedAt: source.last_ingested_at,
            logCount: logsBefore.total,
          }),
        );
        setIngestNotice(`${source.name} 已加入采集队列，后台执行中（Reddit 约 1–2 分钟）`);
      } else {
        await load();
      }
    } catch (e) {
      const msg = e instanceof Error ? e.message : "采集失败";
      setError(msg.includes("Internal Server Error") ? "后端服务异常，请稍后重试" : msg);
    } finally {
      setIngestingId(null);
    }
  }

  async function openLogs(source: Source) {
    setLogsSource(source);
    setLogs([]);
    setLogsLoading(true);
    try {
      const res = await listIngestLogs(source.id);
      setLogs(res.data);
    } catch (e) {
      const msg = e instanceof Error ? e.message : "加载日志失败";
      setError(msg.includes("Internal Server Error") ? "后端服务异常，无法加载日志" : msg);
    } finally {
      setLogsLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <div className="mb-5 flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="muted-label">运营</div>
          <h1 className="mt-1 text-3xl font-semibold tracking-normal">来源管理</h1>
          <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
            共 {total} 个来源
            {totalPages > 0 && ` · 第 ${page} / ${totalPages} 页`}
            {" · "}启用源、手动触发 RSS 采集、查看采集日志
          </p>
        </div>
        <div className="surface flex items-center gap-3 px-4 py-3 text-sm text-slate-600 dark:text-slate-300">
          <RadioTower className="h-4 w-4 text-slate-400" />
          <span>本页 {sources.filter((source) => source.enabled).length} 个已启用</span>
        </div>
      </div>

      <div className="surface mb-4 flex flex-wrap gap-3 p-4">
        <select
          value={tierFilter}
          onChange={(e) => {
            setTierFilter(e.target.value);
            setPage(1);
          }}
          className="field min-w-36"
        >
          <option value="">全部 Tier</option>
          <option value="0">Tier 0</option>
          <option value="1">Tier 1</option>
          <option value="2">Tier 2</option>
        </select>
        <select
          value={enabledFilter}
          onChange={(e) => {
            setEnabledFilter(e.target.value);
            setPage(1);
          }}
          className="field min-w-36"
        >
          <option value="">全部状态</option>
          <option value="true">已启用</option>
          <option value="false">已停用</option>
        </select>
      </div>

      {totalPages > 1 && !loading && (
        <div className="mb-4 flex items-center justify-end gap-4">
          <button
            disabled={page <= 1}
            onClick={() => setPage((p) => p - 1)}
            className="icon-action"
            aria-label="上一页"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
          <span className="text-sm text-slate-600 dark:text-slate-400">
            第 {page} / {totalPages} 页
          </span>
          <button
            disabled={page >= totalPages}
            onClick={() => setPage((p) => p + 1)}
            className="icon-action"
            aria-label="下一页"
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      )}

      {ingestNotice && (
        <div className="mb-4 flex items-center gap-2 rounded-lg border border-sky-200 bg-sky-50 px-4 py-3 text-sm text-sky-800 dark:border-sky-900 dark:bg-sky-950/30 dark:text-sky-200">
          <Loader2 className="h-4 w-4 shrink-0 animate-spin" />
          {ingestNotice}
        </div>
      )}

      {error && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/30 dark:text-red-300">
          {error}
        </div>
      )}

      {loading ? (
        <div className="surface flex items-center gap-2 p-5 text-slate-500">
          <Loader2 className="h-4 w-4 animate-spin" /> 加载中…
        </div>
      ) : sources.length === 0 ? (
        <div className="surface p-8 text-center">
          <RadioTower className="mx-auto h-8 w-8 text-slate-300" />
          <p className="mt-3 text-sm text-slate-500">当前筛选下暂无来源</p>
        </div>
      ) : (
        <div className="surface overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-slate-50 text-xs uppercase tracking-normal text-slate-500 dark:bg-slate-900 dark:text-slate-400">
              <tr>
                <th className="px-4 py-3 font-medium">名称</th>
                <th className="px-4 py-3 font-medium">分类</th>
                <th className="px-4 py-3 font-medium">Tier</th>
                <th className="px-4 py-3 font-medium">状态</th>
                <th className="px-4 py-3 font-medium">上次采集</th>
                <th className="px-4 py-3 font-medium">操作</th>
              </tr>
            </thead>
            <tbody>
              {sources.map((s) => {
                const ingestible = isIngestible(s);
                return (
                <tr key={s.id} className="border-t border-slate-100 transition hover:bg-slate-50/80 dark:border-slate-800 dark:hover:bg-slate-900/60">
                  <td className="px-4 py-3">
                    <div className="font-medium text-slate-950 dark:text-white">{s.name}</div>
                    <div className="text-xs text-slate-500">{s.slug}</div>
                    {!ingestible && (
                      <div className="mt-1 text-xs text-amber-600 dark:text-amber-400">
                        不可采集：{ingestSkipReason(s)}
                      </div>
                    )}
                  </td>
                  <td className="px-4 py-3">{s.category}</td>
                  <td className="px-4 py-3">{s.tier}</td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => toggleEnabled(s)}
                      disabled={busyId === s.id}
                      className={`rounded-lg px-2.5 py-1 text-xs font-medium ${
                        s.enabled
                          ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300"
                          : "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400"
                      }`}
                    >
                      {s.enabled ? "已启用" : "已停用"}
                    </button>
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-500">
                    {s.last_ingested_at
                      ? new Date(s.last_ingested_at).toLocaleString()
                      : "—"}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2">
                      <button
                        onClick={() => runIngest(s)}
                        disabled={
                          ingestingId === s.id ||
                          pendingIngest.has(s.id) ||
                          !ingestible
                        }
                        title={!ingestible ? ingestSkipReason(s) : undefined}
                        className="inline-flex h-8 min-w-[5.5rem] items-center justify-center gap-1 rounded-lg bg-slate-950 px-2.5 text-xs font-medium text-white hover:bg-slate-800 disabled:opacity-50 dark:bg-white dark:text-slate-950"
                      >
                        {ingestingId === s.id ? (
                          <>
                            <Loader2 className="h-3 w-3 animate-spin" /> 排队中…
                          </>
                        ) : pendingIngest.has(s.id) ? (
                          <>
                            <Loader2 className="h-3 w-3 animate-spin" /> 采集中…
                          </>
                        ) : (
                          <>
                            <Play className="h-3 w-3" /> 采集
                          </>
                        )}
                      </button>
                      <button
                        onClick={() => openLogs(s)}
                        className="inline-flex h-8 items-center gap-1 rounded-lg border border-slate-300 px-2.5 text-xs font-medium hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-800"
                      >
                        <ScrollText className="h-3 w-3" /> 日志
                      </button>
                      {s.last_ingested_at && (
                        <Link
                          href={`/articles?source_id=${s.id}`}
                          className="inline-flex h-8 items-center gap-1 rounded-lg border border-sky-300 px-2.5 text-xs font-medium text-sky-800 hover:bg-sky-50 dark:border-sky-800 dark:text-sky-200 dark:hover:bg-sky-950/40"
                        >
                          <FileText className="h-3 w-3" /> 资讯
                        </Link>
                      )}
                    </div>
                  </td>
                </tr>
              );
              })}
            </tbody>
          </table>
        </div>
      )}

      {totalPages > 1 && (
        <div className="mt-6 flex items-center justify-center gap-4">
          <button
            disabled={page <= 1 || loading}
            onClick={() => setPage((p) => p - 1)}
            className="icon-action"
            aria-label="上一页"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
          <span className="text-sm text-slate-600 dark:text-slate-400">
            第 {page} / {totalPages} 页 · 本页 {sources.length} 条
          </span>
          <button
            disabled={page >= totalPages || loading}
            onClick={() => setPage((p) => p + 1)}
            className="icon-action"
            aria-label="下一页"
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      )}

      {logsSource !== null && (
        <div className="surface mt-6 p-4">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="font-semibold">
              采集日志 · {logsSource.name}
              <span className="ml-2 text-xs font-normal text-slate-500">#{logsSource.id}</span>
            </h2>
            <button
              onClick={() => setLogsSource(null)}
              className="text-xs font-medium text-slate-500 hover:text-slate-800 dark:hover:text-slate-200"
            >
              关闭
            </button>
          </div>
          {logsLoading ? (
            <div className="flex items-center gap-2 text-sm text-slate-500">
              <Loader2 className="h-4 w-4 animate-spin" /> 加载日志…
            </div>
          ) : logs.length === 0 ? (
            <p className="text-sm text-slate-500">
              {isIngestible(logsSource)
                ? "暂无采集记录，配置 RSS 后点击「采集」开始。"
                : `无法采集：${ingestSkipReason(logsSource)}`}
            </p>
          ) : (
            <ul className="space-y-2 text-sm">
              {logs.map((log) => (
                <li
                  key={log.id}
                  className="flex flex-wrap gap-x-4 gap-y-1 rounded-lg bg-slate-50 px-3 py-2 dark:bg-slate-950"
                >
                  <span className="font-medium">{log.status}</span>
                  <span>found {log.items_found}</span>
                  <span>+{log.items_created}</span>
                  <span>skip {log.items_skipped}</span>
                  {log.duration_ms != null && <span>{log.duration_ms}ms</span>}
                  {log.error_message && (
                    <span className="basis-full text-amber-700 dark:text-amber-300">
                      {log.error_message}
                    </span>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </main>
  );
}
