import React from "react";
import { cn } from "@/lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "secondary" | "outline" | "success" | "warning" | "danger" | "info";
}

export function Badge({ className, variant = "default", ...props }: BadgeProps) {
  const base =
    "inline-flex items-center rounded-md px-2.5 py-0.5 text-xs font-semibold tracking-wide transition-colors focus:outline-none focus:ring-2 focus:ring-slate-950 focus:ring-offset-2";

  const variants = {
    default: "bg-slate-900 text-slate-50 border border-slate-800",
    secondary: "bg-slate-100 text-slate-800 border border-slate-200",
    outline: "text-slate-700 border border-slate-300 bg-white",
    success: "bg-emerald-50 text-emerald-800 border border-emerald-200",
    warning: "bg-amber-50 text-amber-800 border border-amber-200",
    danger: "bg-red-50 text-red-800 border border-red-200",
    info: "bg-sky-50 text-sky-800 border border-sky-200",
  };

  return <div className={cn(base, variants[variant], className)} {...props} />;
}
