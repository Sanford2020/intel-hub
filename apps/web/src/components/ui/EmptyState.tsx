import type { ReactNode } from "react";
import { Inbox } from "lucide-react";

interface EmptyStateProps {
  title?: string;
  description?: string;
  icon?: ReactNode;
  action?: ReactNode;
}

export function EmptyState({
  title = "暂无数据",
  description,
  icon,
  action,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <div className="mb-3 text-slate-300 dark:text-slate-600">
        {icon || <Inbox className="h-10 w-10" />}
      </div>
      <p className="text-sm font-medium text-slate-600 dark:text-slate-400">{title}</p>
      {description && (
        <p className="mt-1 max-w-xs text-xs text-slate-500 dark:text-slate-500">
          {description}
        </p>
      )}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
