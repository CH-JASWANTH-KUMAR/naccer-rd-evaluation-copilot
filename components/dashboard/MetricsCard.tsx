import React from "react";
import { LucideIcon } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface MetricsCardProps {
  title: string;
  value: number | string;
  subtitle: string;
  icon: LucideIcon;
  variant?: "default" | "amber" | "emerald" | "slate";
}

export function MetricsCard({ title, value, subtitle, icon: Icon, variant = "default" }: MetricsCardProps) {
  const variantStyles = {
    default: "border-slate-200 bg-white text-slate-900",
    amber: "border-amber-200 bg-amber-50/40 text-amber-950",
    emerald: "border-emerald-200 bg-emerald-50/40 text-emerald-950",
    slate: "border-slate-300 bg-slate-100/50 text-slate-900",
  };

  const iconStyles = {
    default: "bg-slate-100 text-slate-700",
    amber: "bg-amber-100 text-amber-800",
    emerald: "bg-emerald-100 text-emerald-800",
    slate: "bg-slate-200 text-slate-800",
  };

  return (
    <Card className={cn("shadow-xs transition-shadow hover:shadow-sm", variantStyles[variant])}>
      <CardContent className="p-5">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-600 uppercase tracking-wider font-mono">
            {title}
          </span>
          <div className={cn("p-2 rounded-md", iconStyles[variant])}>
            <Icon className="h-4 w-4" />
          </div>
        </div>
        <div className="mt-3 flex items-baseline justify-between">
          <span className="text-2xl font-bold tracking-tight text-slate-900">{value}</span>
        </div>
        <p className="mt-1 text-[11px] text-slate-500 font-normal">{subtitle}</p>
      </CardContent>
    </Card>
  );
}
