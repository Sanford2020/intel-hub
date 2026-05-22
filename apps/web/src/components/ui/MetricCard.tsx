import type { ElementType } from "react";
import { cn } from "@/lib/utils";

interface MetricCardProps {
  label: string;
  value: number | string;
  sub?: string;
  icon?: ElementType;
  tone?: string;
}

export function MetricCard({ label, value, sub, icon: Icon, tone }: MetricCardProps) {
  return (
    <div className="surface p-5">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="muted-label">{label}</div>
          <div className="mt-2 text-3xl font-semibold tracking-normal text-slate-950 dark:text-white">
            {value}
          </div>
          {sub && (
            <div className="mt-1 text-sm text-slate-500 dark:text-slate-400">{sub}</div>
          )}
        </div>
        {Icon && (
          <div
            className={cn(
              "flex h-10 w-10 shrink-0 items-center justify-center rounded-lg",
              tone || "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300",
            )}
          >
            <Icon className="h-5 w-5" />
          </div>
        )}
      </div>
    </div>
  );
}
