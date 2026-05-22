"use client";

import { ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

interface PaginationProps {
  page: number;
  totalPages: number;
  onPageChange: (_page: number) => void;
  className?: string;
}

export function Pagination({ page, totalPages, onPageChange, className }: PaginationProps) {
  if (totalPages <= 1) return null;

  return (
    <div className={cn("flex items-center gap-2 text-sm", className)}>
      <button
        onClick={() => onPageChange(page - 1)}
        disabled={page <= 1}
        className="icon-action"
        aria-label="上一页"
      >
        <ChevronLeft className="h-4 w-4" />
      </button>
      <span className="text-slate-600 dark:text-slate-400">
        {page} / {totalPages}
      </span>
      <button
        onClick={() => onPageChange(page + 1)}
        disabled={page >= totalPages}
        className="icon-action"
        aria-label="下一页"
      >
        <ChevronRight className="h-4 w-4" />
      </button>
    </div>
  );
}
