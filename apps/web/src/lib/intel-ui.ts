/**
 * Unified UI tone/score helpers for intel components.
 */

export type Tone = "success" | "warning" | "danger" | "neutral" | "info";

export function scoreTone(score: number): Tone {
  if (score >= 8) return "danger";
  if (score >= 6) return "warning";
  if (score >= 4) return "info";
  return "neutral";
}

export const toneClasses: Record<Tone, { bg: string; text: string; dot: string }> = {
  success: {
    bg: "bg-emerald-50 dark:bg-emerald-950/40",
    text: "text-emerald-700 dark:text-emerald-300",
    dot: "bg-emerald-500",
  },
  warning: {
    bg: "bg-amber-50 dark:bg-amber-950/40",
    text: "text-amber-700 dark:text-amber-300",
    dot: "bg-amber-500",
  },
  danger: {
    bg: "bg-rose-50 dark:bg-rose-950/40",
    text: "text-rose-700 dark:text-rose-300",
    dot: "bg-rose-500",
  },
  neutral: {
    bg: "bg-slate-100 dark:bg-slate-800",
    text: "text-slate-700 dark:text-slate-300",
    dot: "bg-slate-400",
  },
  info: {
    bg: "bg-blue-50 dark:bg-blue-950/40",
    text: "text-blue-700 dark:text-blue-300",
    dot: "bg-blue-500",
  },
};

export function scoreBadgeClass(score: number): string {
  const tone = scoreTone(score);
  return `${toneClasses[tone].bg} ${toneClasses[tone].text}`;
}
