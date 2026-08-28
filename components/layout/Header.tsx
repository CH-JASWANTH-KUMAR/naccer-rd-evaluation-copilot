"use client";

import React from "react";
import { usePathname } from "next/navigation";
import { Search, Bell, Shield } from "lucide-react";
import { Input } from "@/components/ui/input";

export function Header() {
  const pathname = usePathname();

  const getBreadcrumbs = () => {
    const segments = pathname.split("/").filter(Boolean);
    if (segments.length === 0) return "Dashboard";
    return segments
      .map((s) => s.charAt(0).toUpperCase() + s.slice(1))
      .join(" / ");
  };

  return (
    <header className="h-16 border-b border-slate-200 bg-white px-6 flex items-center justify-between sticky top-0 z-30 shadow-xs">
      <div className="flex items-center space-x-3">
        <div className="text-xs font-medium text-slate-500 uppercase tracking-wider font-mono">
          NaCCER Evaluation Copilot
        </div>
        <span className="text-slate-300">/</span>
        <h2 className="text-sm font-semibold text-slate-900">{getBreadcrumbs()}</h2>
      </div>

      <div className="flex items-center space-x-4">
        {/* Global Search Bar Placeholder */}
        <div className="relative w-64 hidden sm:block">
          <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-slate-400" />
          <Input
            placeholder="Search proposals, institutions, IDs..."
            className="pl-8 h-8 text-xs bg-slate-50 border-slate-200"
            readOnly
          />
        </div>

        {/* Top Header Actions */}
        <button
          type="button"
          className="p-1.5 rounded-md text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition-colors"
          title="System Notifications Placeholder"
        >
          <Bell className="h-4 w-4" />
        </button>

        <button
          type="button"
          className="p-1.5 rounded-md text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition-colors"
          title="Platform Security & Audit Info"
        >
          <Shield className="h-4 w-4" />
        </button>
      </div>
    </header>
  );
}
