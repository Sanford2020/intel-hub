"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  Activity,
  ArrowRight,
  Bell,
  Bot,
  Cpu,
  Database,
  FileText,
  Layers,
  RadioTower,
} from "lucide-react";
import type { APIResponse, HealthData } from "@opc/shared-types";
import { apiClient } from "@/lib/api";
import { getOverviewStats } from "@/lib/intel-api";
import type { OverviewStats } from "@/types/intel";

export default function Home() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [stats, setStats] = useState<OverviewStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 2500);

    apiClient
      .get<APIResponse<HealthData>>("/api/v1/health", { signal: controller.signal })
      .then((res) => setHealth(res.data ?? null))
      .catch(() => setHealth(null))
      .finally(() => {
        window.clearTimeout(timeout);
        setLoading(false);
      });

    getOverviewStats()
      .then((res) => setStats(res.data))
      .catch(() => setStats(null));

    return () => {
      window.clearTimeout(timeout);
      controller.abort();
    };
  }, []);

  const features = [
    {
      icon: <Layers className="h-6 w-6" />,
      title: "多源采集",
      description: "RSS / API / Webhook，Celery 定时入库",
    },
    {
      icon: <Database className="h-6 w-6" />,
      title: "资讯归一",
      description: "去重、清洗、PostgreSQL 持久化",
    },
    {
      icon: <Cpu className="h-6 w-6" />,
      title: "AI 情报分析",
      description: "摘要、标签、实体抽取，结构化 JSON",
    },
    {
      icon: <Bot className="h-6 w-6" />,
      title: "Agent 工作流",
      description: "OPC + Agency + 12-Factor 三库整合",
    },
    {
      icon: <Bell className="h-6 w-6" />,
      title: "关键词告警",
      description: "规则匹配 + Webhook / 日志通知",
    },
    {
      icon: <Activity className="h-6 w-6" />,
      title: "检索分发",
      description: "过滤检索、订阅告警、Dashboard",
    },
  ];

  const statCards = stats
    ? [
        {
          label: "情报源",
          value: stats.sources_total,
          sub: `${stats.sources_enabled} 启用`,
          icon: RadioTower,
          tone: "text-blue-700 bg-blue-50 dark:bg-blue-950/40 dark:text-blue-300",
        },
        {
          label: "资讯条目",
          value: stats.articles_total,
          sub: `${stats.reports_total} 已分析`,
          icon: FileText,
          tone: "text-emerald-700 bg-emerald-50 dark:bg-emerald-950/40 dark:text-emerald-300",
        },
        {
          label: "告警规则",
          value: stats.alert_rules_total,
          sub: `${stats.alert_rules_enabled} 启用`,
          icon: Bell,
          tone: "text-amber-700 bg-amber-50 dark:bg-amber-950/40 dark:text-amber-300",
        },
        {
          label: "告警事件",
          value: stats.alert_events_total,
          sub: "累计触发",
          icon: Activity,
          tone: "text-rose-700 bg-rose-50 dark:bg-rose-950/40 dark:text-rose-300",
        },
      ]
    : [];

  return (
    <main className="min-h-[calc(100vh-4rem)]">
      <section className="app-shell">
        <div className="grid gap-6 lg:grid-cols-[1.25fr_0.75fr]">
          <div className="surface overflow-hidden p-6 sm:p-8">
            <div className="flex flex-wrap items-center gap-2">
              <span className="rounded-lg bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-600 dark:bg-slate-800 dark:text-slate-300">
                Global intelligence desk
              </span>
              <span className="rounded-lg bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300">
                Commercial Edition
              </span>
            </div>
            <h1 className="mt-8 max-w-2xl text-3xl font-semibold leading-tight tracking-normal text-slate-950 sm:text-4xl lg:text-5xl dark:text-white">
              分散资讯，统一采集、分析与告警。
            </h1>
            <p className="mt-5 max-w-2xl text-base leading-7 text-slate-600 dark:text-slate-300">
              Intel Hub 面向商业情报团队，汇总 RSS 与开放源信息，完成去重入库、AI 摘要、标签提取和关键词告警，帮助分析员更快进入判断。
            </p>

            <div className="mt-8 flex flex-wrap items-center gap-3">
              <Link href="/articles" className="primary-action">
                查看资讯 <ArrowRight className="h-4 w-4" />
              </Link>
              <Link href="/sources" className="secondary-action">
                管理来源
              </Link>
              <Link href="/alerts" className="secondary-action">
                告警规则
              </Link>
            </div>
          </div>

          <aside className="surface p-5">
            <div className="flex items-center justify-between">
              <div>
                <div className="muted-label">System status</div>
                <h2 className="mt-1 text-lg font-semibold">运行状态</h2>
              </div>
              <Activity className="h-5 w-5 text-slate-400" />
            </div>
            <div className="mt-5">
          {loading ? (
            <div className="flex items-center gap-2 rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-700 dark:bg-amber-950/30 dark:text-amber-300">
              <div className="h-2 w-2 animate-pulse rounded-full bg-yellow-400" />
              Connecting...
            </div>
          ) : health ? (
            <div className="flex items-center gap-2 rounded-lg bg-emerald-50 px-3 py-2 text-sm font-medium text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300">
              <div className="h-2 w-2 rounded-full bg-green-500" />
              Backend: {health.status} · v{health.version}
            </div>
          ) : (
            <div className="flex items-center gap-2 rounded-lg bg-rose-50 px-3 py-2 text-sm font-medium text-rose-700 dark:bg-rose-950/40 dark:text-rose-300">
              <div className="h-2 w-2 rounded-full bg-red-500" />
              Backend: offline
            </div>
          )}
            </div>
            <div className="mt-5 space-y-3 text-sm text-slate-600 dark:text-slate-300">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3 dark:border-slate-800">
                <span>采集调度</span>
                <span className="font-medium text-slate-900 dark:text-white">5 min</span>
              </div>
              <div className="flex items-center justify-between border-b border-slate-100 pb-3 dark:border-slate-800">
                <span>分析调度</span>
                <span className="font-medium text-slate-900 dark:text-white">10 min</span>
              </div>
              <div className="flex items-center justify-between">
                <span>AI 模式</span>
                <span className="font-medium text-slate-900 dark:text-white">
                  OpenAI / mock
                </span>
              </div>
            </div>
          </aside>
        </div>
      </section>

      <section className="app-shell pt-0">
        {stats && (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {statCards.map((item) => {
              const Icon = item.icon;

              return (
                <div key={item.label} className="surface p-5">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="muted-label">{item.label}</div>
                      <div className="mt-2 text-3xl font-semibold tracking-normal">
                        {item.value}
                      </div>
                      <div className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                        {item.sub}
                      </div>
                    </div>
                    <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${item.tone}`}>
                      <Icon className="h-5 w-5" />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="surface p-5 transition hover:-translate-y-0.5 hover:shadow-md hover:shadow-slate-200/80 dark:hover:shadow-none"
            >
              <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-200">
                {feature.icon}
              </div>
              <h3 className="font-semibold text-slate-950 dark:text-white">{feature.title}</h3>
              <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-400">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
