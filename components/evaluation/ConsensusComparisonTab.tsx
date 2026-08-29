"use client";

import React, { useState, useEffect } from "react";
import { Users, CheckCircle2, ShieldAlert, FileText, Send, Lock } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { evaluationService } from "@/lib/api/evaluations";

interface ComparisonCriterion {
  criterion_key: string;
  criterion_name: string;
  max_score: number;
  scores_by_reviewer: Record<string, number>;
  score_difference: number;
  disagreement_status: string;
  comments: string | null;
}

interface ConsensusComparisonTabProps {
  evaluationId: string;
}

export function ConsensusComparisonTab({ evaluationId }: ConsensusComparisonTabProps) {
  const [comparison, setComparison] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Governance Finalization State
  const [finalizing, setFinalizing] = useState(false);
  const [recommendation, setRecommendation] = useState("FAVORABLE_WITH_CONDITIONS");
  const [governanceNote, setGovernanceNote] = useState("");
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // COI State
  const [coiReason, setCoiReason] = useState("");
  const [coiDeclared, setCoiDeclared] = useState(false);

  const reloadComparison = async () => {
    try {
      const data = await evaluationService.getReviewerComparison(evaluationId);
      setComparison(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load reviewer comparison.");
    }
  };

  useEffect(() => {
    let isMounted = true;
    evaluationService
      .getReviewerComparison(evaluationId)
      .then((data) => {
        if (isMounted) setComparison(data);
      })
      .catch((err: unknown) => {
        if (isMounted) setError(err instanceof Error ? err.message : "Failed to load reviewer comparison.");
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });
    return () => {
      isMounted = false;
    };
  }, [evaluationId]);

  const handleDeclareCOI = async () => {
    if (!coiReason || coiReason.length < 5) return;
    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1"}/evaluations/${evaluationId}/conflicts`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reviewer_id: "Reviewer", reason: coiReason }),
      });
      setCoiDeclared(true);
    } catch {
      setError("Failed to declare conflict of interest.");
    }
  };

  const handleFinalizeGovernance = async () => {
    if (governanceNote.length < 20) return;
    setFinalizing(true);
    setError(null);
    try {
      await evaluationService.finalizeGovernance(evaluationId, recommendation, governanceNote);
      setSuccessMsg("Institutional governance evaluation record finalized successfully.");
      reloadComparison();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to finalize governance record.");
    } finally {
      setFinalizing(false);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="p-8 flex flex-col items-center justify-center space-y-3 text-xs text-slate-500">
          <Users className="h-6 w-6 animate-spin text-blue-600" />
          <span>Aggregating multi-reviewer score comparison &amp; consensus...</span>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="border-amber-200 bg-amber-50/30">
        <CardContent className="p-6 space-y-3 text-xs">
          <div className="flex items-center space-x-2 text-amber-800 font-bold">
            <Lock className="h-5 w-5" />
            <span>Reviewer Independence Policy Active</span>
          </div>
          <p className="text-slate-600">{error}</p>
        </CardContent>
      </Card>
    );
  }

  if (!comparison) return null;

  const criteria = (comparison.comparison_criteria as ComparisonCriterion[]) || [];
  const stats = (comparison.statistics as Record<string, unknown>) || {};

  return (
    <div className="space-y-6">
      {/* Overview Banner */}
      <Card>
        <CardHeader className="pb-3 border-b border-slate-200">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div>
              <div className="flex items-center space-x-2">
                <Badge variant="outline" className="font-mono text-[10px] bg-blue-50 text-blue-700">
                  Consensus Status: {comparison.consensus_status as string}
                </Badge>
                <Badge
                  variant={comparison.disagreement_status === "SIGNIFICANT_DIFFERENCE" ? "warning" : "secondary"}
                  className="font-mono text-[10px]"
                >
                  Score Variation: {comparison.disagreement_status as string}
                </Badge>
              </div>
              <CardTitle className="text-base font-bold text-slate-900 mt-2 flex items-center space-x-2">
                <Users className="h-5 w-5 text-blue-600" />
                <span>Multi-Reviewer Consensus &amp; Comparison Workspace</span>
              </CardTitle>
            </div>

            <div className="flex items-center space-x-2">
              <span className="text-xs text-slate-500 font-medium">
                Participation: {comparison.completed_reviewers as number} / {comparison.total_assigned_reviewers as number} Reviewers
              </span>
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-4 text-xs text-slate-700 space-y-2">
          <div className="flex items-center justify-between bg-slate-50 p-3 rounded border border-slate-200">
            <span className="font-bold text-slate-900">{(stats.label as string) || "Reviewer Score Statistics"}:</span>
            <span className="text-lg font-bold font-mono text-blue-600">
              {stats.overall_score !== null && stats.overall_score !== undefined ? Number(stats.overall_score).toFixed(1) : "—"} / 10.0
            </span>
          </div>
        </CardContent>
      </Card>

      {/* Conflict of Interest Declaration Card */}
      <Card className="border-amber-200 bg-amber-50/20">
        <CardHeader className="pb-2">
          <CardTitle className="text-xs font-bold text-amber-900 flex items-center space-x-1.5">
            <ShieldAlert className="h-4 w-4 text-amber-600" />
            <span>Reviewer Conflict of Interest (COI) Recusal</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-xs">
          {coiDeclared ? (
            <div className="p-3 bg-emerald-50 border border-emerald-200 rounded text-emerald-800 font-medium">
              Conflict of interest declared. Recusal submitted for administrative review.
            </div>
          ) : (
            <div className="space-y-2">
              <Textarea
                placeholder="Specify potential conflict of interest reason (e.g. co-authorship, institutional affiliation)..."
                value={coiReason}
                onChange={(e) => setCoiReason(e.target.value)}
                className="text-xs min-h-[60px]"
              />
              <Button
                size="sm"
                variant="outline"
                className="text-xs border-amber-300 text-amber-900 hover:bg-amber-100"
                disabled={coiReason.length < 5}
                onClick={handleDeclareCOI}
              >
                Declare Conflict of Interest &amp; Request Recusal
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Criterion Score Comparison Table */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-bold text-slate-900">Criterion Score Comparison &amp; Disagreement Matrix</CardTitle>
          <CardDescription className="text-xs">
            Differences between independent reviewer scores flagged against institutional disagreement threshold (&ge; 2.0 pts).
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left border-collapse">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 font-bold">
                  <th className="p-2.5">Criterion</th>
                  <th className="p-2.5">Scores by Reviewer</th>
                  <th className="p-2.5">Score Difference</th>
                  <th className="p-2.5">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {criteria.map((c: ComparisonCriterion) => (
                  <tr key={c.criterion_key} className="hover:bg-slate-50/80">
                    <td className="p-2.5 font-bold text-slate-900">{c.criterion_name}</td>
                    <td className="p-2.5 font-mono">
                      {Object.entries(c.scores_by_reviewer || {}).map(([r, s]) => (
                        <span key={r} className="mr-3">
                          {r}: <strong>{String(s)}</strong>
                        </span>
                      ))}
                    </td>
                    <td className="p-2.5 font-mono font-bold text-slate-700">{c.score_difference.toFixed(1)} pts</td>
                    <td className="p-2.5">
                      <Badge
                        variant={c.disagreement_status === "SIGNIFICANT_DIFFERENCE" ? "warning" : "secondary"}
                        className="text-[10px]"
                      >
                        {c.disagreement_status}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Human Governance Finalization */}
      <Card className="border-blue-200">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-bold text-slate-900 flex items-center space-x-2">
            <FileText className="h-4 w-4 text-blue-600" />
            <span>Human Institutional Governance Finalization</span>
          </CardTitle>
          <CardDescription className="text-xs">
            Authorized governance personnel record final consensus recommendation and explanation note.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4 text-xs">
          {successMsg && (
            <div className="p-3 bg-emerald-50 border border-emerald-200 rounded text-emerald-800 font-medium flex items-center space-x-2">
              <CheckCircle2 className="h-4 w-4 text-emerald-600" />
              <span>{successMsg}</span>
            </div>
          )}

          <div className="space-y-1">
            <label className="font-bold text-slate-800">Final Governance Recommendation:</label>
            <Select
              value={recommendation}
              onChange={(e) => setRecommendation(e.target.value)}
              className="text-xs"
            >
              <option value="FAVORABLE">FAVORABLE — Recommended for Funding</option>
              <option value="FAVORABLE_WITH_CONDITIONS">FAVORABLE WITH CONDITIONS — Subject to Modifications</option>
              <option value="REQUIRES_REVISION">REQUIRES REVISION — Return for Resubmission</option>
              <option value="NOT_RECOMMENDED">NOT RECOMMENDED — Rejected</option>
            </Select>
          </div>

          <div className="space-y-1">
            <label className="font-bold text-slate-800">Governance Explanation &amp; Resolution Note (min 20 chars):</label>
            <Textarea
              placeholder="Record final committee consensus reasoning, condition requirements, or resolution of score differences..."
              value={governanceNote}
              onChange={(e) => setGovernanceNote(e.target.value)}
              className="min-h-[90px] text-xs"
            />
          </div>

          <Button
            size="sm"
            className="bg-blue-600 hover:bg-blue-700 text-white"
            disabled={finalizing || governanceNote.length < 20}
            onClick={handleFinalizeGovernance}
          >
            <Send className="h-3.5 w-3.5 mr-1.5" />
            {finalizing ? "Finalizing Governance..." : "Finalize Institutional Governance Record"}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
