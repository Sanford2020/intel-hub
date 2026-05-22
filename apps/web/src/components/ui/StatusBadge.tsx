import { cn } from "@/lib/utils";
import { type Tone, toneClasses } from "@/lib/intel-ui";

interface StatusBadgeProps {
  tone: Tone;
  label: string;
  dot?: boolean;
  className?: string;
}

export function StatusBadge({ tone, label, dot = true, className }: StatusBadgeProps) {
  const classes = toneClasses[tone];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-md px-2 py-0.5 text-xs font-medium",
        classes.bg,
        classes.text,
        className,
      )}
    >
      {dot && <span className={cn("h-1.5 w-1.5 rounded-full", classes.dot)} />}
      {label}
    </span>
  );
}
