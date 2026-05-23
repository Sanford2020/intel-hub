"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { Bell, Loader2, Plus, Trash2 } from "lucide-react";
import {
  createAlertRule,
  deleteAlertRule,
  listAlertEvents,
  listAlertRules,
  updateAlertRule,
} from "@/lib/intel-api";
import type { AlertEvent, AlertRule } from "@/types/intel";
import { ErrorBanner } from "@/components/ui/ErrorBanner";

export default function AlertsPage() {
  const [rules, setRules] = useState<AlertRule[]>([]);
  const [events, setEvents] = useState<AlertEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [name, setName] = useState("");
  const [keywords, setKeywords] = useState("");
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [rulesRes, eventsRes] = await Promise.all([
        listAlertRules(1),
        listAlertEvents(1),
      ]);
      setRules(rulesRes.data);
      setEvents(eventsRes.data);
    } catch (e) {
      const msg = e instanceof Error ? e.message : "加载失败";
      setError(msg.includes("Internal Server Error") || msg.includes("Failed to fetch") ? "无法连接后端服务，请确认 API 已启动" : msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await createAlertRule({
        name,
        keywords: keywords.split(",").map((k) => k.trim()).filter(Boolean),
        match_in: "all",
        channel: "log",
      });
      setName("");
      setKeywords("");
      await load();
    } catch (err) {
      const msg = err instanceof Error ? err.message : "创建失败";
      setError(msg.includes("Internal Server Error") ? "后端服务异常，无法创建规则" : msg);
    }
  }

  async function toggleRule(rule: AlertRule) {
    await updateAlertRule(rule.id, { enabled: !rule.enabled });
    await load();
  }

  async function removeRule(id: number) {
    await deleteAlertRule(id);
    await load();
  }

  return (
    <main className="app-shell">
      <div className="mb-5 flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="muted-label">运营</div>
          <h1 className="mt-1 text-3xl font-semibold tracking-normal">关键词告警</h1>
          <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
            订阅关键词，匹配资讯标题 / 正文 / AI 标签后触发通知
          </p>
        </div>
        <div className="surface flex items-center gap-3 px-4 py-3 text-sm text-slate-600 dark:text-slate-300">
          <Bell className="h-4 w-4 text-amber-500" />
          <span>{rules.filter((rule) => rule.enabled).length} 个活跃规则</span>
        </div>
      </div>

      {error && (
        <div className="mb-4">
          <ErrorBanner message={error} onRetry={load} />
        </div>
      )}

      <form
        onSubmit={handleCreate}
        className="surface mb-6 grid gap-3 p-4 sm:grid-cols-3"
      >
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="规则名称"
          required
          className="field"
        />
        <input
          value={keywords}
          onChange={(e) => setKeywords(e.target.value)}
          placeholder="关键词，逗号分隔 e.g. Taiwan, AI, sanctions"
          required
          className="field sm:col-span-2"
        />
        <button
          type="submit"
          className="primary-action sm:col-span-3"
        >
          <Plus className="h-4 w-4" /> 新建规则
        </button>
      </form>

      {loading ? (
        <div className="surface flex items-center gap-2 p-5 text-slate-500">
          <Loader2 className="h-4 w-4 animate-spin" /> 加载中…
        </div>
      ) : (
        <div className="grid gap-8 lg:grid-cols-2">
          <section>
            <h2 className="mb-3 font-semibold">告警规则</h2>
            <ul className="space-y-2">
              {rules.map((rule) => (
                <li
                  key={rule.id}
                  className="surface flex items-start justify-between gap-4 p-4"
                >
                  <div>
                    <div className="font-medium text-slate-950 dark:text-white">{rule.name}</div>
                    <div className="mt-1 flex flex-wrap gap-1">
                      {rule.keywords.map((k) => (
                        <span
                          key={k}
                          className="rounded-lg bg-slate-100 px-2 py-0.5 text-xs text-slate-700 dark:bg-slate-800 dark:text-slate-300"
                        >
                          {k}
                        </span>
                      ))}
                    </div>
                    <div className="mt-2 text-xs text-slate-500">
                      {rule.match_in} · {rule.channel}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => toggleRule(rule)}
                      className={`rounded-lg px-2.5 py-1 text-xs font-medium ${
                        rule.enabled
                          ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300"
                          : "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400"
                      }`}
                    >
                      {rule.enabled ? "启用" : "停用"}
                    </button>
                    <button
                      onClick={() => removeRule(rule.id)}
                      className="icon-action text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/30"
                      aria-label="删除规则"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          </section>

          <section>
            <h2 className="mb-3 font-semibold">最近触发</h2>
            {events.length === 0 ? (
              <div className="surface p-8 text-center">
                <Bell className="mx-auto h-8 w-8 text-slate-300" />
                <p className="mt-3 text-sm text-slate-500">暂无告警事件</p>
              </div>
            ) : (
              <ul className="space-y-2">
                {events.map((ev) => (
                  <li
                    key={ev.id}
                    className="surface p-4 text-sm"
                  >
                    <div className="font-medium">{ev.rule_name ?? `Rule #${ev.rule_id}`}</div>
                    <Link
                      href={`/articles/${ev.article_id}`}
                      className="mt-1 block text-primary-600 hover:underline"
                    >
                      {ev.article_title ?? `Article #${ev.article_id}`}
                    </Link>
                    <div className="mt-2 flex flex-wrap gap-1">
                      {ev.matched_keywords.map((k) => (
                        <span
                          key={k}
                          className="rounded-lg bg-amber-50 px-2 py-0.5 text-xs text-amber-700"
                        >
                          {k}
                        </span>
                      ))}
                    </div>
                    <div className="mt-2 text-xs text-slate-500">
                      {ev.notification_status} · {new Date(ev.created_at).toLocaleString()}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </div>
      )}
    </main>
  );
}
