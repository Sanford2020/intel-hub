"use client";

import { FormEvent, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { ApiError } from "@/lib/api";
import { useAuth } from "@/components/auth/AuthProvider";

export default function LoginForm() {
  const { login, loading: authLoading } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const nextPath = searchParams.get("next") || "/";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login({ email: email.trim(), password });
      router.replace(nextPath);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message || "登录失败，请检查邮箱和密码");
      } else {
        setError("无法连接服务器，请确认后端已启动");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="flex min-h-[calc(100vh-3.5rem)] items-center justify-center px-4 py-12">
      <div className="w-full max-w-sm rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="mb-6 text-center">
          <div className="mx-auto mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-primary-600 text-sm font-bold text-white">
            I
          </div>
          <h1 className="text-lg font-semibold text-slate-900 dark:text-white">
            登录 Intel Hub
          </h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            使用管理员或团队成员账号登录
          </p>
        </div>

        <form className="space-y-4" onSubmit={handleSubmit}>
          <label className="block space-y-1.5">
            <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
              邮箱
            </span>
            <input
              type="email"
              autoComplete="username"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none ring-primary-500 focus:ring-2 dark:border-slate-700 dark:bg-slate-950 dark:text-white"
              placeholder="admin@example.com"
            />
          </label>

          <label className="block space-y-1.5">
            <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
              密码
            </span>
            <input
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none ring-primary-500 focus:ring-2 dark:border-slate-700 dark:bg-slate-950 dark:text-white"
            />
          </label>

          {error ? (
            <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-950/40 dark:text-red-300">
              {error}
            </p>
          ) : null}

          <button
            type="submit"
            disabled={submitting || authLoading}
            className="w-full rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-primary-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {submitting ? "登录中…" : "登录"}
          </button>
        </form>
      </div>
    </main>
  );
}
