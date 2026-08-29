"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  FileText,
  Upload,
  Database,
  BookOpen,
  ClipboardCheck,
  BarChart3,
  Settings,
  ChevronDown,
  ChevronRight,
  User,
  Activity,
  Menu,
  X,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { appConfig } from "@/lib/config";

export function Sidebar() {
  const pathname = usePathname();
  const [proposalsOpen, setProposalsOpen] = useState(
    pathname.startsWith("/proposals") || pathname === "/upload"
  );
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const isActive = (path: string) => pathname === path;
  const isParentActive = (path: string) => pathname.startsWith(path);

  return (
    <>
      {/* Mobile Menu Toggle Button */}
      <div className="lg:hidden fixed top-3 left-3 z-50">
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="p-2 bg-slate-900 text-white rounded-md shadow-md focus:outline-none"
          aria-label="Toggle Navigation"
        >
          {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {/* Sidebar Overlay for Mobile */}
      {mobileMenuOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-slate-900/50 z-40"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar Navigation Shell */}
      <aside
        className={cn(
          "fixed top-0 left-0 bottom-0 z-40 w-64 bg-slate-900 text-slate-200 flex flex-col justify-between transition-transform duration-200 border-r border-slate-800",
          mobileMenuOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        )}
      >
        <div>
          {/* Top Brand Header */}
          <div className="h-16 flex items-center px-5 border-b border-slate-800 bg-slate-950">
            <div className="flex items-center space-x-3">
              <div className="h-8 w-8 rounded-md bg-emerald-600 flex items-center justify-center font-bold text-white text-xs tracking-wider shadow-sm">
                NaC
              </div>
              <div>
                <h1 className="text-sm font-bold tracking-tight text-white leading-none">
                  NaCCER Evaluation
                </h1>
                <p className="text-[10px] font-mono text-slate-400 mt-0.5">
                  Copilot Base v{appConfig.version}
                </p>
              </div>
            </div>
          </div>

          {/* Main Navigation Links */}
          <nav className="p-3 space-y-1">
            {/* Dashboard Link */}
            <Link
              href="/dashboard"
              onClick={() => setMobileMenuOpen(false)}
              className={cn(
                "flex items-center px-3 py-2 text-xs font-medium rounded-md transition-colors",
                isActive("/dashboard")
                  ? "bg-slate-800 text-white font-semibold shadow-xs"
                  : "text-slate-300 hover:bg-slate-800/60 hover:text-white"
              )}
            >
              <LayoutDashboard className="h-4 w-4 mr-2.5 text-slate-400" />
              Dashboard
            </Link>

            {/* Proposals Section (Collapsible Menu) */}
            <div>
              <button
                type="button"
                onClick={() => setProposalsOpen(!proposalsOpen)}
                className={cn(
                  "w-full flex items-center justify-between px-3 py-2 text-xs font-medium rounded-md transition-colors cursor-pointer",
                  isParentActive("/proposals") || pathname === "/upload"
                    ? "text-white bg-slate-800/50"
                    : "text-slate-300 hover:bg-slate-800/60 hover:text-white"
                )}
              >
                <div className="flex items-center">
                  <FileText className="h-4 w-4 mr-2.5 text-slate-400" />
                  <span>Proposals</span>
                </div>
                {proposalsOpen ? (
                  <ChevronDown className="h-3.5 w-3.5 text-slate-400" />
                ) : (
                  <ChevronRight className="h-3.5 w-3.5 text-slate-400" />
                )}
              </button>

              {proposalsOpen && (
                <div className="ml-6 mt-1 space-y-1 border-l border-slate-800 pl-2">
                  <Link
                    href="/proposals"
                    onClick={() => setMobileMenuOpen(false)}
                    className={cn(
                      "block px-3 py-1.5 text-xs rounded-md transition-colors",
                      isActive("/proposals")
                        ? "text-white font-semibold bg-slate-800"
                        : "text-slate-400 hover:text-white hover:bg-slate-800/40"
                    )}
                  >
                    All Proposals
                  </Link>
                  <Link
                    href="/upload"
                    onClick={() => setMobileMenuOpen(false)}
                    className={cn(
                      "flex items-center px-3 py-1.5 text-xs rounded-md transition-colors",
                      isActive("/upload")
                        ? "text-white font-semibold bg-slate-800"
                        : "text-slate-400 hover:text-white hover:bg-slate-800/40"
                    )}
                  >
                    <Upload className="h-3 w-3 mr-2" />
                    Upload Proposal
                  </Link>
                </div>
              )}
            </div>

            {/* Historical Projects */}
            <Link
              href="/projects"
              onClick={() => setMobileMenuOpen(false)}
              className={cn(
                "flex items-center px-3 py-2 text-xs font-medium rounded-md transition-colors",
                isParentActive("/projects")
                  ? "bg-slate-800 text-white font-semibold shadow-xs"
                  : "text-slate-300 hover:bg-slate-800/60 hover:text-white"
              )}
            >
              <Database className="h-4 w-4 mr-2.5 text-slate-400" />
              Historical Projects
            </Link>

            {/* Research Papers */}
            <Link
              href="/research-papers"
              onClick={() => setMobileMenuOpen(false)}
              className={cn(
                "flex items-center px-3 py-2 text-xs font-medium rounded-md transition-colors",
                isParentActive("/research-papers")
                  ? "bg-slate-800 text-white font-semibold shadow-xs"
                  : "text-slate-300 hover:bg-slate-800/60 hover:text-white"
              )}
            >
              <BookOpen className="h-4 w-4 mr-2.5 text-slate-400" />
              Research Papers
            </Link>

            {/* Evaluations */}
            <Link
              href="/evaluations"
              onClick={() => setMobileMenuOpen(false)}
              className={cn(
                "flex items-center px-3 py-2 text-xs font-medium rounded-md transition-colors",
                isParentActive("/evaluations")
                  ? "bg-slate-800 text-white font-semibold shadow-xs"
                  : "text-slate-300 hover:bg-slate-800/60 hover:text-white"
              )}
            >
              <ClipboardCheck className="h-4 w-4 mr-2.5 text-slate-400" />
              Evaluations
            </Link>

            {/* Reports */}
            <Link
              href="/reports"
              onClick={() => setMobileMenuOpen(false)}
              className={cn(
                "flex items-center px-3 py-2 text-xs font-medium rounded-md transition-colors",
                isActive("/reports")
                  ? "bg-slate-800 text-white font-semibold shadow-xs"
                  : "text-slate-300 hover:bg-slate-800/60 hover:text-white"
              )}
            >
              <BarChart3 className="h-4 w-4 mr-2.5 text-slate-400" />
              Reports
            </Link>

            {/* Settings */}
            <Link
              href="/settings"
              onClick={() => setMobileMenuOpen(false)}
              className={cn(
                "flex items-center px-3 py-2 text-xs font-medium rounded-md transition-colors",
                isActive("/settings")
                  ? "bg-slate-800 text-white font-semibold shadow-xs"
                  : "text-slate-300 hover:bg-slate-800/60 hover:text-white"
              )}
            >
              <Settings className="h-4 w-4 mr-2.5 text-slate-400" />
              Settings
            </Link>
          </nav>
        </div>

        {/* Bottom Sidebar Status & Reviewer Profile */}
        <div className="p-3 border-t border-slate-800 space-y-3 bg-slate-950">
          {/* System Status Card */}
          <div className="rounded-md bg-slate-900 p-2.5 border border-slate-800 text-xs">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-semibold text-slate-300 flex items-center">
                <Activity className="h-3 w-3 mr-1.5 text-emerald-400" />
                System Status
              </span>
              <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[9px] font-mono bg-emerald-950 text-emerald-300 border border-emerald-800">
                Frontend Active
              </span>
            </div>
            <p className="text-[10px] text-slate-400 mt-1">
              Backend REST API boundary initialized. AI Engine disconnected (Base Phase).
            </p>
          </div>

          {/* Reviewer Profile Placeholder */}
          <div className="flex items-center space-x-2.5 px-1 py-1">
            <div className="h-7 w-7 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300">
              <User className="h-4 w-4 text-slate-300" />
            </div>
            <div className="overflow-hidden">
              <p className="text-xs font-medium text-white truncate">Dr. A. Sharma</p>
              <p className="text-[10px] text-slate-400 truncate">Senior R&amp;D Reviewer</p>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
