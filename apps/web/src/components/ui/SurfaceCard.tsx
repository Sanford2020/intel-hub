import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface SurfaceCardProps {
  children: ReactNode;
  className?: string;
  padding?: "none" | "sm" | "md" | "lg";
}

const paddingMap = {
  none: "",
  sm: "p-4",
  md: "p-5",
  lg: "p-6 sm:p-8",
};

export function SurfaceCard({ children, className, padding = "md" }: SurfaceCardProps) {
  return (
    <div className={cn("surface", paddingMap[padding], className)}>
      {children}
    </div>
  );
}
