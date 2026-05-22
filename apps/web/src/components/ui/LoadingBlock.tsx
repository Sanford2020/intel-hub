import { cn } from "@/lib/utils";

interface LoadingBlockProps {
  lines?: number;
  className?: string;
}

export function LoadingBlock({ lines = 3, className }: LoadingBlockProps) {
  return (
    <div className={cn("animate-pulse space-y-3", className)} role="status" aria-label="加载中">
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className={cn(
            "h-4 rounded bg-slate-200 dark:bg-slate-700",
            i === lines - 1 ? "w-2/3" : "w-full",
          )}
        />
      ))}
      <span className="sr-only">加载中…</span>
    </div>
  );
}
