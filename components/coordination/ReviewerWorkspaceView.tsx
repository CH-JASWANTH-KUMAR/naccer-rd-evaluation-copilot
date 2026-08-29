"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  Clock,
  AlertTriangle,
  UserCheck,
  ArrowRight,
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { coordinationService, ReviewerWorkspaceQueue, ReviewerAssignedProposalCard } from "@/lib/api/coordination";

interface ReviewerWorkspaceViewProps {
  reviewerId: string;
}

export function ReviewerWorkspaceView({ reviewerId: initialReviewerId }: ReviewerWorkspaceViewProps) {
  const [reviewerId, setReviewerId] = useState(initialReviewerId || "Reviewer A (Technical)");
  const [queue, setQueue] = useState<ReviewerWorkspaceQueue | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"pending" | "completed" | "coi">("pending");

  useEffect(() => {
    async function fetchQueue() {
      try {
        setLoading(true);
        setError(null);
        const data = await coordinationService.getReviewerWorkspace(reviewerId);
        setQueue(data);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Failed to load reviewer workspace queue.");
      } finally {
        setLoading(false);
      }
    }
    fetchQueue();
  }, [reviewerId]);

  if (loading) {
    return (
      <div className="p-12 text-center text-xs text-slate-500 flex flex-col items-center gap-2">
        <Clock className="h-8 w-8 animate-spin text-blue-600" />
        <span>Loading reviewer workspace queue...</span>
      </div>
    );
  }

  if (error || !queue) {
    return (
      <div className="p-6 bg-red-50 border border-red-200 rounded-md text-xs text-red-900 flex items-start gap-2">
        <AlertTriangle className="h-4 w-4 text-red-600 flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-bold">Workspace Error:</span>
          <p className="mt-1 text-slate-700">{error || "Unable to load reviewer workspace."}</p>
        </div>
      </div>
    );
  }

  const currentCards =
    activeTab === "pending"
      ? queue.pendingReviews
      : activeTab === "completed"
      ? queue.completedReviews
      : queue.coiReviews;

  return (
    <div className="space-y-6">
      {/* HEADER BAR */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <UserCheck className="h-5 w-5 text-blue-600" />
            <span>Reviewer Workspace Queue</span>
          </h1>
          <div className="flex items-center space-x-2 mt-1">
            <span className="text-xs text-slate-500 font-mono">Active Reviewer Persona:</span>
            <select
              value={reviewerId}
              onChange={(e) => setReviewerId(e.target.value)}
              className="text-xs font-mono font-bold bg-slate-100 border border-slate-300 rounded px-2 py-1 text-slate-900"
            >
              <option value="Reviewer A (Technical)">Reviewer A — Technical Evaluation</option>
              <option value="Reviewer B (Scientific)">Reviewer B — Scientific/Research Evaluation</option>
              <option value="Reviewer C (Financial)">Reviewer C — Financial & Implementation Evaluation</option>
            </select>
          </div>
        </div>

        {/* TABS SELECTOR */}
        <div className="flex items-center space-x-1 bg-slate-100 p-1 rounded-lg text-xs font-medium">
          <button
            onClick={() => setActiveTab("pending")}
            className={`px-3 py-1.5 rounded-md transition-all ${
              activeTab === "pending" ? "bg-white shadow text-slate-900 font-bold" : "text-slate-600 hover:text-slate-900"
            }`}
          >
            Pending Tasks ({queue.pendingReviews.length})
          </button>
          <button
            onClick={() => setActiveTab("completed")}
            className={`px-3 py-1.5 rounded-md transition-all ${
              activeTab === "completed" ? "bg-white shadow text-slate-900 font-bold" : "text-slate-600 hover:text-slate-900"
            }`}
          >
            Completed ({queue.completedReviews.length})
          </button>
          {queue.coiReviews.length > 0 && (
            <button
              onClick={() => setActiveTab("coi")}
              className={`px-3 py-1.5 rounded-md transition-all ${
                activeTab === "coi" ? "bg-white shadow text-amber-900 font-bold" : "text-slate-600 hover:text-slate-900"
              }`}
            >
              COI Declarations ({queue.coiReviews.length})
            </button>
          )}
        </div>
      </div>

      {/* CARDS LIST */}
      {currentCards.length === 0 ? (
        <div className="p-12 text-center text-xs text-slate-500 border border-dashed rounded-lg bg-slate-50">
          No review tasks found in {activeTab} queue.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {currentCards.map((card) => (
            <ReviewerProposalCard key={card.evaluationId} card={card} />
          ))}
        </div>
      )}
    </div>
  );
}

function ReviewerProposalCard({ card }: { card: ReviewerAssignedProposalCard }) {
  return (
    <Card className="border-slate-200 hover:border-blue-300 transition-all shadow-sm">
      <CardHeader className="py-3 bg-slate-50/70 border-b border-slate-200 flex flex-row items-start justify-between space-y-0">
        <div>
          <div className="flex items-center space-x-1.5 mb-1">
            <Badge variant="outline" className="font-mono text-[10px] uppercase">
              {card.proposalReference}
            </Badge>
            {card.isDemo && (
              <Badge variant="outline" className="bg-amber-100 text-amber-900 border-amber-300 text-[9px] font-mono uppercase font-bold">
                DEMO DATA
              </Badge>
            )}
            <Badge
              variant={card.priority === "HIGH" ? "danger" : "warning"}
              className="text-[9px] font-mono uppercase px-1.5"
            >
              Priority: {card.priority || "MEDIUM"}
            </Badge>
          </div>
          <CardTitle className="text-sm font-bold text-slate-900 line-clamp-1">{card.proposalTitle}</CardTitle>
          <CardDescription className="text-xs text-slate-700 font-mono font-semibold mt-0.5">
            Task: {card.taskTitle || "Review Proposal"}
          </CardDescription>
        </div>
        <Badge
          variant={
            card.reviewStatus === "COMPLETED" || card.reviewStatus === "SUBMITTED"
              ? "success"
              : card.reviewStatus === "RECUSAL_PENDING"
              ? "warning"
              : "outline"
          }
          className="text-[10px] font-mono"
        >
          {card.reviewStatus}
        </Badge>
      </CardHeader>

      <CardContent className="p-4 space-y-3 text-xs font-mono">
        <div className="grid grid-cols-2 gap-2 text-[11px] bg-slate-50 p-2.5 rounded border border-slate-200/80">
          <div>
            <span className="text-slate-400 text-[10px] block">RUBRIC PROGRESS</span>
            <span className="font-bold text-slate-800">
              {card.rubricCompletedCount}/{card.rubricTotalCount} criteria
            </span>
          </div>

          <div>
            <span className="text-slate-400 text-[10px] block">EVIDENCE SOURCES</span>
            <span className="font-semibold text-slate-800">
              {card.evidenceSourcesCount || 6} sources ({card.evidenceGapsCount} gaps)
            </span>
          </div>

          <div>
            <span className="text-slate-400 text-[10px] block">ASSIGNED DATE</span>
            <span className="text-slate-700">{card.assignmentDate.split("T")[0]}</span>
          </div>

          <div>
            <span className="text-slate-400 text-[10px] block">CONSENSUS STATUS</span>
            <span className="font-semibold text-slate-800">{card.consensusStatus}</span>
          </div>
        </div>

        <div className="flex items-center justify-between pt-1">
          <span className="text-slate-500 font-sans text-[11px] italic">{card.actionRequired}</span>

          <Link href={`/proposals/${card.proposalId}`}>
            <Button size="sm" className="text-xs font-mono">
              <span>{card.actionRequired.includes("View") ? "View Assessment" : "Open Workspace"}</span>
              <ArrowRight className="h-3.5 w-3.5 ml-1" />
            </Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}
