import { Suspense } from "react";
import LoginForm from "./LoginForm";

export default function LoginPage() {
  return (
    <Suspense
      fallback={
        <main className="flex min-h-[calc(100vh-3.5rem)] items-center justify-center px-4 py-12">
          <p className="text-sm text-slate-500">加载中…</p>
        </main>
      }
    >
      <LoginForm />
    </Suspense>
  );
}
