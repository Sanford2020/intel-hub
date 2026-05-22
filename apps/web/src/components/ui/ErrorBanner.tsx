import { AlertTriangle } from "lucide-react";

interface ErrorBannerProps {
  message: string;
  onRetry?: () => void;
}

export function ErrorBanner({ message, onRetry }: ErrorBannerProps) {
  return (
    <div className="flex items-center gap-3 rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700 dark:border-rose-900 dark:bg-rose-950/30 dark:text-rose-300">
      <AlertTriangle className="h-4 w-4 shrink-0" />
      <span className="min-w-0 flex-1">{message}</span>
      {onRetry && (
        <button
          onClick={onRetry}
          className="shrink-0 text-xs font-medium underline hover:no-underline"
        >
          重试
        </button>
      )}
    </div>
  );
}
