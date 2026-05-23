import type { ReactNode } from "react";

interface PageHeaderProps {
  title: string;
  description?: string;
  actions?: ReactNode;
  meta?: ReactNode;
}

export function PageHeader({ title, description, actions, meta }: PageHeaderProps) {
  return (
    <div className="flex min-w-0 flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 className="text-xl font-semibold text-slate-950 dark:text-white sm:text-2xl">
          {title}
        </h1>
        {description && (
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{description}</p>
        )}
        {meta && <div className="mt-2">{meta}</div>}
      </div>
      {actions && (
        <div className="mt-3 flex min-w-0 flex-wrap items-center gap-2 sm:mt-0 sm:justify-end">
          {actions}
        </div>
      )}
    </div>
  );
}
