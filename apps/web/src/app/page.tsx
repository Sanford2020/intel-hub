"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  ArrowRight,
  Bell,
  FileText,
  RadioTower,
  Shield,
} from "lucide-react";
import type { APIResponse, HealthData } from "@opc/shared-types";
import { apiClient } from "@/lib/api";
import { getDailyBriefing, getOverviewStats } from "@/lib/intel-api";
import type { BriefingItem, DailyBriefing, OverviewStats } from "@/types/intel";
import { PageHeader } from "@/components/ui/PageHeader";
import { MetricCard } from "@/components/ui/MetricCard";
import { SurfaceCard } from "@/components/ui/SurfaceCard";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { LoadingBlock } from "@/components/ui/LoadingBlock";
import { scoreTone } from "@/lib/intel-ui";
import { relativeTime } from "@/lib/format";

export default function Home() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [stats, setStats] = useState<OverviewStats | null>(null);
  const [briefing, setBriefing] = useState<DailyBriefing | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 3000);

    Promise.allSettled([
      apiClient
        .get<APIResponse<HealthData>>("/api/v1/health", { signal: controller.signal })
        .then((res) => { if (!cancelled) setHealth(res.data ?? null); }),
      getOverviewStats()
        .then((res) => { if (!cancelled) setStats(res.data); }),
      getDailyBriefing({ hours: 24, limit: 5 })
        .then((res) => { if (!cancelled) setBriefing(res.data); }),
    ])
      .catch(() => { if (!cancelled) setError("部分数据加载失败"); })
      .finally(() => {
        window.clearTimeout(timeout);
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
      window.clearTimeout(timeout);
      controller.abort();
    };
  }, []);

  return (
    <main className="min-h-[calc(100vh-3.5rem)] min-w-0 overflow-x-hidden">
      <section className="app-shell">
        <PageHeader
          title="今日情报工作台"
          description="过去 24 小时情报概览"
          meta={
            <div className="flex flex-wrap items-center gap-2">
              {health ? (
                <StatusBadge tone="success" label={`Backend v${health.version}`} />
              ) : loading ? (
                <StatusBadge tone="warning" label="连接中…" />
              ) : (
                <StatusBadge tone="danger" label="Backend 离线" />
              )}
              {briefing?.meta.ai_mode === "mock" && (
                <StatusBadge tone="warning" label="Mock AI 模式" dot={false} />
              )}
            </div>
          }
        />
      </section>

      {error && (
        <section className="app-shell pt-0">
          <ErrorBanner message={error} />
        </section>
      )}

      {/* Metric cards */}
      <section className="app-shell pt-0">
        {loading ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <SurfaceCard key={i}><LoadingBlock lines={2} /></SurfaceCard>
            ))}
          </div>
        ) : stats ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <MetricCard
              label="今日入库"
              value={stats.articles_total}
              sub="资讯总量"
              icon={FileText}
              tone="text-blue-700 bg-blue-50 dark:bg-blue-950/40 dark:text-blue-300"
            />
            <MetricCard
              label="已分析"
              value={stats.reports_total}
              sub="AI 分析报告"
              icon={Shield}
              tone="text-emerald-700 bg-emerald-50 dark:bg-emerald-950/40 dark:text-emerald-300"
            />
            <MetricCard
              label="高相关"
              value={briefing?.meta.item_count ?? 0}
              sub="相关度 ≥ 6.0"
              icon={RadioTower}
              tone="text-amber-700 bg-amber-50 dark:bg-amber-950/40 dark:text-amber-300"
            />
            <MetricCard
              label="告警事件"
              value={stats.alert_events_total}
              sub={`${stats.alert_rules_enabled} 条规则启用`}
              icon={Bell}
              tone="text-rose-700 bg-rose-50 dark:bg-rose-950/40 dark:text-rose-300"
            />
          </div>
        ) : (
          <SurfaceCard>
            <EmptyState
              title="无法加载统计数据"
              description="请确认后端服务已启动"
            />
          </SurfaceCard>
        )}
      </section>

      {/* Top intel + System status */}
      <section className="app-shell pt-0">
        <div className="grid gap-4 lg:grid-cols-[1.5fr_1fr]">
          {/* Top 情报 */}
          <SurfaceCard padding="none">
            <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4 dark:border-slate-800">
              <h2 className="text-sm font-semibold text-slate-900 dark:text-white">
                今日 Top 情报
              </h2>
              <Link
                href="/briefing"
                className="inline-flex items-center gap-1 text-xs font-medium text-primary-600 hover:text-primary-700 dark:text-primary-400"
              >
                完整简报 <ArrowRight className="h-3 w-3" />
              </Link>
            </div>
            <div className="divide-y divide-slate-100 dark:divide-slate-800">
              {loading ? (
                <div className="px-5 py-4">
                  <LoadingBlock lines={4} />
                </div>
              ) : briefing && briefing.items.length > 0 ? (
                briefing.items.slice(0, 5).map((item) => (
                  <TopIntelItem key={item.article_id} item={item} />
                ))
              ) : (
                <EmptyState
                  title="暂无高相关情报"
                  description="系统正常运行后将自动展示今日 Top 资讯"
                  action={
                    <Link href="/sources" className="secondary-action text-xs">
                      配置来源
                    </Link>
                  }
                />
              )}
            </div>
          </SurfaceCard>

          {/* System status */}
          <SurfaceCard padding="none">
            <div className="border-b border-slate-100 px-5 py-4 dark:border-slate-800">
              <h2 className="text-sm font-semibold text-slate-900 dark:text-white">
                系统状态
              </h2>
            </div>
            <div className="space-y-0 divide-y divide-slate-100 px-5 dark:divide-slate-800">
              <StatusRow label="Backend" loading={loading} value={health ? `${health.status} · v${health.version}` : "离线"} ok={!!health} />
              <StatusRow label="采集调度" loading={false} value="5 min (Beat)" ok={true} />
              <StatusRow label="分析调度" loading={false} value="AI 入库后触发" ok={true} />
              <StatusRow
                label="AI 模式"
                loading={false}
                value={briefing?.meta.ai_mode === "mock" ? "Mock (无 API Key)" : briefing?.meta.ai_mode ?? "—"}
                ok={briefing?.meta.ai_mode !== "mock"}
              />
              <StatusRow
                label="情报源"
                loading={!stats && loading}
                value={stats ? `${stats.sources_enabled} / ${stats.sources_total} 启用` : "—"}
                ok={stats ? stats.sources_enabled > 0 : false}
              />
              <StatusRow
                label="告警规则"
                loading={!stats && loading}
                value={stats ? `${stats.alert_rules_enabled} 条启用` : "—"}
                ok={stats ? stats.alert_rules_enabled > 0 : false}
              />
            </div>
            <div className="border-t border-slate-100 px-5 py-3 dark:border-slate-800">
              <div className="flex flex-wrap gap-2">
                <Link href="/sources" className="text-xs font-medium text-primary-600 hover:text-primary-700 dark:text-primary-400">
                  来源运营 →
                </Link>
                <Link href="/alerts" className="text-xs font-medium text-primary-600 hover:text-primary-700 dark:text-primary-400">
                  告警规则 →
                </Link>
              </div>
            </div>
          </SurfaceCard>
        </div>
      </section>
    </main>
  );
}

function TopIntelItem({ item }: { item: BriefingItem }) {
  const tone = scoreTone(item.relevance_score);
  return (
    <Link
      href={`/articles/${item.article_id}`}
      className="block px-5 py-3 transition-colors hover:bg-slate-50 dark:hover:bg-slate-800/50"
    >
      <div className="flex items-start gap-3">
        <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded text-xs font-semibold text-slate-500 dark:text-slate-400">
          {item.rank}
        </span>
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-medium text-slate-900 dark:text-white">
            {item.title}
          </p>
          <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
            <span>{item.source_name}</span>
            <StatusBadge tone={tone} label={item.relevance_score.toFixed(1)} dot={false} className="text-[10px]" />
            {item.published_at && <span>{relativeTime(item.published_at)}</span>}
          </div>
        </div>
      </div>
    </Link>
  );
}

function StatusRow({
  label,
  value,
  ok,
  loading,
}: {
  label: string;
  value: string;
  ok: boolean;
  loading: boolean;
}) {
  return (
    <div className="flex items-center justify-between py-3 text-sm">
      <span className="text-slate-600 dark:text-slate-400">{label}</span>
      {loading ? (
        <div className="h-4 w-20 animate-pulse rounded bg-slate-200 dark:bg-slate-700" />
      ) : (
        <span className={ok ? "font-medium text-slate-900 dark:text-white" : "font-medium text-amber-600 dark:text-amber-400"}>
          {value}
        </span>
      )}
    </div>
  );
}
