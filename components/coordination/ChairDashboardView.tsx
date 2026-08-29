"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  AlertCircle,
  Clock,
  ArrowRight,
} from "lucide-react";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { coordinationService, ChairDashboardResponse, ChairProposalCoordinationItem } from "@/lib/api/coordination";

export function ChairDashboardView() {
  const [dashboard, setDashboard] = useState<ChairDashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<"ALL" | "READY" | "BLOCKED">("ALL");

  useEffect(() => {
    async function fetchDashboard() {
      try {
        setLoading(true);
        setError(null);
        const data = await coordinationService.getChairDashboard("ADMIN");
        setDashboard(data);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Failed to load Chair coordination dashboard.");
      } finally {
        setLoading(false);
      }
    }
    fetchDashboard();
  }, []);

  if (loading) {
    return (
      <div className="p-12 text-center text-xs text-slate-500 flex flex-col items-center gap-2">
        <Clock className="h-8 w-8 animate-spin text-blue-600" />
        <span>Loading asynchronous reviewer coordination dashboard...</span>
      </div>
    );
  }

  if (error || !dashboard) {
    return (
      <div className="p-6 bg-red-50 border border-red-200 rounded-md text-xs text-red-900 flex items-start gap-2">
        <AlertTriangle className="h-4 w-4 text-red-600 flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-bold">Dashboard Error:</span>
          <p className="mt-1 text-slate-700">{error || "Unable to load Chair dashboard."}</p>
        </div>
      </div>
    );
  }

  const filteredItems = dashboard.items.filter((item) => {
    if (filter === "READY") return item.decisionReadiness === "READY";
    if (filter === "BLOCKED") return item.decisionReadiness !== "READY";
    return true;
  });

  return (
    <div className="space-y-6">
      {/* HEADER BAR */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <ShieldAlert className="h-5 w-5 text-blue-600" />
            <span>Chair Reviewer Coordination Dashboard</span>
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Asynchronous committee progress tracking, reviewer completion, score variance, and decision readiness.
          </p>
        </div>

        {/* METRICS SUMMARY BADGES */}
        <div className="flex items-center space-x-2 text-xs font-mono">
          <div className="px-3 py-1.5 bg-slate-100 rounded border border-slate-200 text-slate-700">
            Total: <span className="font-bold">{dashboard.totalProposals}</span>
          </div>
          <div className="px-3 py-1.5 bg-emerald-50 rounded border border-emerald-200 text-emerald-800">
            Ready: <span className="font-bold">{dashboard.readyCount}</span>
          </div>
          <div className="px-3 py-1.5 bg-amber-50 rounded border border-amber-200 text-amber-800">
            Blocked / Needs Attention: <span className="font-bold">{dashboard.notReadyCount + dashboard.needsAttentionCount}</span>
          </div>
        </div>
      </div>

      {/* FILTER BUTTONS */}
      <div className="flex items-center space-x-2 text-xs">
        <button
          onClick={() => setFilter("ALL")}
          className={`px-3 py-1.5 rounded-md font-medium transition-all ${
            filter === "ALL" ? "bg-slate-900 text-white shadow" : "bg-slate-100 text-slate-700 hover:bg-slate-200"
          }`}
        >
          All Proposals ({dashboard.items.length})
        </button>
        <button
          onClick={() => setFilter("READY")}
          className={`px-3 py-1.5 rounded-md font-medium transition-all ${
            filter === "READY" ? "bg-emerald-600 text-white shadow" : "bg-slate-100 text-slate-700 hover:bg-slate-200"
          }`}
        >
          Ready for Human Decision ({dashboard.readyCount})
        </button>
        <button
          onClick={() => setFilter("BLOCKED")}
          className={`px-3 py-1.5 rounded-md font-medium transition-all ${
            filter === "BLOCKED" ? "bg-amber-600 text-white shadow" : "bg-slate-100 text-slate-700 hover:bg-slate-200"
          }`}
        >
          Blocked / Pending ({dashboard.notReadyCount + dashboard.needsAttentionCount})
        </button>
      </div>

      {/* COORDINATION ITEMS TABLE / LIST */}
      <div className="space-y-4">
        {filteredItems.map((item) => (
          <ChairCoordinationCard key={item.proposalId} item={item} />
        ))}
      </div>
    </div>
  );
}

function ChairCoordinationCard({ item }: { item: ChairProposalCoordinationItem }) {
  const isReady = item.decisionReadiness === "READY";

  return (
    <Card className="border-slate-200 hover:border-blue-300 transition-all shadow-sm">
      <CardHeader className="py-3.5 bg-slate-50/80 border-b border-slate-200 flex flex-row items-center justify-between">
        <div className="flex items-center space-x-3">
          <Badge variant="outline" className="font-mono text-[10px] uppercase">
            {item.proposalReference}
          </Badge>
          <h3 className="font-bold text-sm text-slate-900">{item.proposalTitle}</h3>
          <span className="text-xs text-slate-500 font-mono hidden sm:inline">&bull; {item.institution}</span>
        </div>

        <Badge
          variant={isReady ? "success" : item.decisionReadiness === "NEEDS_ATTENTION" ? "danger" : "warning"}
          className="font-mono text-xs px-2.5 py-0.5 font-bold"
        >
          {isReady ? "READY FOR HUMAN DECISION" : item.decisionReadiness}
        </Badge>
      </CardHeader>

      <CardContent className="p-4 space-y-4 text-xs font-mono">
        {/* GRID OF STATUSES */}
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 bg-white p-3 rounded border border-slate-200 text-[11px]">
          {/* REVIEWERS STATUS */}
          <div>
            <span className="text-slate-400 text-[10px] uppercase block mb-1">Reviewers Progress</span>
            <div className="space-y-1">
              {item.reviewers && item.reviewers.length > 0 ? (
                item.reviewers.map((r, idx) => (
                  <div key={idx} className="flex items-center space-x-1.5 text-slate-800 font-semibold">
                    {r.status === "Submitted" ? (
                      <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 flex-shrink-0" />
                    ) : r.status === "COI Declared" ? (
                      <AlertTriangle className="h-3.5 w-3.5 text-amber-600 flex-shrink-0" />
                    ) : (
                      <Clock className="h-3.5 w-3.5 text-slate-400 flex-shrink-0" />
                    )}
                    <span>
                      {r.reviewerName} &mdash; {r.status}
                    </span>
                  </div>
                ))
              ) : (
                <span className="text-slate-500 italic">No reviewers assigned</span>
              )}
            </div>
          </div>

          {/* RUBRIC & SCIENTIFIC */}
          <div>
            <span className="text-slate-400 text-[10px] uppercase block mb-1">Rubric &amp; Evidence</span>
            <div className="space-y-1">
              <div>
                <span className="text-slate-500">Rubric: </span>
                <span className="font-bold text-slate-800">{item.rubricProgress}</span>
              </div>
              <div>
                <span className="text-slate-500">Scientific: </span>
                <span className="font-bold text-slate-800">{item.scientificComparisonStatus}</span>
              </div>
            </div>
          </div>

          {/* FINANCIAL */}
          <div>
            <span className="text-slate-400 text-[10px] uppercase block mb-1">Financial Scrutiny</span>
            <span
              className={`font-bold ${
                item.financialStatus === "Verified" ? "text-emerald-700" : "text-amber-700"
              }`}
            >
              {item.financialStatus}
            </span>
          </div>

          {/* CONSENSUS & VARIANCE */}
          <div>
            <span className="text-slate-400 text-[10px] uppercase block mb-1">Score Variance</span>
            <span
              className={`font-bold ${
                item.consensusStatus === "Within Range" ? "text-emerald-700" : "text-red-700"
              }`}
            >
              {item.consensusStatus} {item.maxScoreVariance > 0 && `(Diff: ${item.maxScoreVariance.toFixed(1)})`}
            </span>
          </div>
        </div>

        {/* BLOCKING REASON OR PRIMARY ACTION BANNER */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pt-1 gap-2 border-t">
          <div className="text-slate-700 font-sans text-xs">
            {!isReady && item.blockingReasons && item.blockingReasons.length > 0 ? (
              <div className="flex items-center space-x-1.5 text-amber-900 font-medium">
                <AlertCircle className="h-4 w-4 text-amber-600 flex-shrink-0" />
                <span>Blocked: {item.blockingReasons[0]}</span>
              </div>
            ) : (
              <span className="text-emerald-900 font-semibold flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                <span>All prerequisites met. Ready for final committee decision.</span>
              </span>
            )}
          </div>

          <Link href={`/proposals/${item.proposalId}`}>
            <Button size="sm" className="text-xs font-mono">
              <span>Open Proposal Brief</span>
              <ArrowRight className="h-3.5 w-3.5 ml-1" />
            </Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}
