import React from "react";
import { cn } from "@/lib/utils";

export function Progress({
  value = 0,
  max = 100,
  className,
}: {
  value?: number;
  max?: number;
  className?: string;
}) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

  return (
    <div className={cn("relative h-2 w-full overflow-hidden rounded-full bg-slate-200", className)}>
      <div
        className="h-full bg-slate-900 transition-all duration-300 ease-in-out"
        style={{ width: `${percentage}%` }}
      />
    </div>
  );
}
