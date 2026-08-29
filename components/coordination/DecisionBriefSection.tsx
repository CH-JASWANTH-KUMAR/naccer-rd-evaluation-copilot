"use client";

import React, { useEffect, useState } from "react";
import {
  FileText,
  CheckCircle2,
  AlertTriangle,
  AlertCircle,
  Clock,
  UserCheck,
  ShieldAlert,
  Scale,
  ExternalLink,
  BookOpen,
  HelpCircle,
  Layers,
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { coordinationService, DecisionBriefResponse } from "@/lib/api/coordination";
import { formatCurrency } from "@/lib/utils";

interface DecisionBriefSectionProps {
  proposalId: string;
  reviewerId?: string;
  userRole?: string;
}

export function DecisionBriefSection({ proposalId, reviewerId, userRole = "ADMIN" }: DecisionBriefSectionProps) {
  const [brief, setBrief] = useState<DecisionBriefResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchBrief() {
      try {
        setLoading(true);
        setError(null);
        const data = await coordinationService.getDecisionBrief(proposalId, reviewerId, userRole);
        setBrief(data);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Failed to load decision brief");
      } finally {
        setLoading(false);
      }
    }
    fetchBrief();
  }, [proposalId, reviewerId, userRole]);

  if (loading) {
    return (
      <div className="p-8 text-center text-xs text-slate-500 flex flex-col items-center gap-2">
        <Clock className="h-6 w-6 animate-spin text-blue-600" />
        <span>Compiling decision-ready brief from system evidence and reviewer findings...</span>
      </div>
    );
  }

  if (error || !brief) {
    return (
      <div className="p-6 bg-red-50 border border-red-200 rounded-md text-xs text-red-900 flex items-start gap-2">
        <AlertTriangle className="h-4 w-4 text-red-600 flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-bold">Error Loading Decision Brief:</span>
          <p className="mt-1 text-slate-700">{error || "No decision brief available."}</p>
        </div>
      </div>
    );
  }

  const isReady = brief.decisionReadiness === "READY_FOR_HUMAN_DECISION";

  return (
    <div className="space-y-6">
      {/* HEADER BANNER */}
      <div
        className={`p-4 rounded-lg border text-xs space-y-2 ${
          isReady
            ? "bg-emerald-50/80 border-emerald-300 text-emerald-950"
            : "bg-amber-50/80 border-amber-300 text-amber-950"
        }`}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {isReady ? (
              <CheckCircle2 className="h-5 w-5 text-emerald-600 flex-shrink-0" />
            ) : (
              <AlertCircle className="h-5 w-5 text-amber-600 flex-shrink-0" />
            )}
            <h3 className="font-bold text-sm uppercase tracking-wide">
              {isReady ? "READY FOR HUMAN DECISION" : "WORKFLOW INCOMPLETE — NOT READY FOR FINAL DECISION"}
            </h3>
          </div>
          <Badge variant={isReady ? "success" : "warning"} className="font-mono text-xs px-2.5 py-0.5 font-bold">
            {brief.decisionReadiness}
          </Badge>
        </div>

        {brief.blockingReasons && brief.blockingReasons.length > 0 && (
          <div className="pl-7 space-y-1">
            <span className="font-semibold text-[11px] uppercase tracking-wider block text-amber-900">
              Active Workflow Blockers ({brief.blockingReasons.length}):
            </span>
            <ul className="list-disc pl-4 space-y-0.5 text-[11px] text-slate-800 font-medium">
              {brief.blockingReasons.map((b: string, idx: number) => (
                <li key={idx}>{b}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* 1. PROPOSAL & REVIEW READINESS GRID */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* PROPOSAL INFORMATION */}
        <Card className="border-slate-200">
          <CardHeader className="py-3 bg-slate-50 border-b border-slate-200">
            <CardTitle className="text-xs font-bold text-slate-800 uppercase flex items-center gap-1.5">
              <FileText className="h-3.5 w-3.5 text-blue-600" />
              <span>Proposal Profile</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-3 text-xs space-y-2 font-mono">
            <div className="flex justify-between border-b pb-1">
              <span className="text-slate-500">Title:</span>
              <span className="font-bold text-slate-900 text-right max-w-[65%] truncate">{brief.title}</span>
            </div>
            <div className="flex justify-between border-b pb-1">
              <span className="text-slate-500">Institution:</span>
              <span className="font-semibold text-slate-800">{brief.institution}</span>
            </div>
            <div className="flex justify-between border-b pb-1">
              <span className="text-slate-500">Principal Investigator:</span>
              <span className="font-semibold text-slate-800">{brief.principalInvestigator}</span>
            </div>
            <div className="flex justify-between border-b pb-1">
              <span className="text-slate-500">Domain:</span>
              <span className="font-semibold text-slate-800">{brief.domain}</span>
            </div>
            {brief.declaredTotalBudget && (
              <div className="flex justify-between">
                <span className="text-slate-500">Declared Budget:</span>
                <span className="font-bold text-slate-900">{formatCurrency(brief.declaredTotalBudget)}</span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* REVIEW READINESS STATUS */}
        <Card className="border-slate-200">
          <CardHeader className="py-3 bg-slate-50 border-b border-slate-200">
            <CardTitle className="text-xs font-bold text-slate-800 uppercase flex items-center gap-1.5">
              <UserCheck className="h-3.5 w-3.5 text-emerald-600" />
              <span>Review Readiness Summary</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-3 text-xs space-y-2 font-mono">
            <div className="flex justify-between border-b pb-1">
              <span className="text-slate-500">Reviewer Completion:</span>
              <Badge variant="outline" className="font-bold text-[10px]">
                {brief.reviewerCompletion}
              </Badge>
            </div>
            <div className="flex justify-between border-b pb-1">
              <span className="text-slate-500">Rubric Progress:</span>
              <Badge variant="outline" className="font-bold text-[10px]">
                {brief.rubricCompletion}
              </Badge>
            </div>
            <div className="flex justify-between border-b pb-1">
              <span className="text-slate-500">Scientific Comparison:</span>
              <Badge variant={brief.scientificComparisonStatus === "READY" ? "success" : "warning"} className="text-[10px]">
                {brief.scientificComparisonStatus}
              </Badge>
            </div>
            <div className="flex justify-between border-b pb-1">
              <span className="text-slate-500">Financial Verification:</span>
              <Badge variant={brief.financialVerificationStatus === "COMPLIANT" ? "success" : "warning"} className="text-[10px]">
                {brief.financialVerificationStatus}
              </Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Completeness Scrutiny:</span>
              <Badge variant={brief.completenessStatus === "COMPLETE" ? "success" : "warning"} className="text-[10px]">
                {brief.completenessStatus}
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 2. SCIENTIFIC EVIDENCE GROUNDING */}
      <Card className="border-slate-200">
        <CardHeader className="py-3 bg-slate-50 border-b border-slate-200">
          <CardTitle className="text-xs font-bold text-slate-800 uppercase flex items-center gap-1.5">
            <BookOpen className="h-3.5 w-3.5 text-indigo-600" />
            <span>Scientific Evidence Base &amp; Provenance</span>
          </CardTitle>
          <CardDescription className="text-[11px]">
            Surfaced prior art from historical CIL projects and scientific literature.
          </CardDescription>
        </CardHeader>
        <CardContent className="p-4 space-y-4 text-xs">
          {/* Historical Projects */}
          <div className="space-y-2">
            <h4 className="font-semibold text-slate-800 text-[11px] uppercase tracking-wider">Relevant Historical CIL Projects</h4>
            {brief.relevantHistoricalProjects && brief.relevantHistoricalProjects.length > 0 ? (
              <div className="space-y-1.5 font-mono">
                {brief.relevantHistoricalProjects.map((item, idx) => (
                  <div key={idx} className="p-2 bg-slate-50 border rounded text-[11px] space-y-0.5">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-900">{item.title}</span>
                      <Badge variant="outline" className="text-[9px]">
                        {item.evidenceId}
                      </Badge>
                    </div>
                    <p className="text-slate-600 text-[10px] font-sans">{item.snippet}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-slate-500 text-[11px] italic">No direct historical project matches surfaced.</p>
            )}
          </div>

          {/* Research Papers */}
          <div className="space-y-2">
            <h4 className="font-semibold text-slate-800 text-[11px] uppercase tracking-wider">Relevant Research Papers</h4>
            {brief.relevantResearchPapers && brief.relevantResearchPapers.length > 0 ? (
              <div className="space-y-1.5 font-mono">
                {brief.relevantResearchPapers.map((item, idx) => (
                  <div key={idx} className="p-2 bg-slate-50 border rounded text-[11px] space-y-0.5">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-900">{item.title}</span>
                      <Badge variant="outline" className="text-[9px]">
                        {item.evidenceId}
                      </Badge>
                    </div>
                    <p className="text-slate-600 text-[10px] font-sans">{item.snippet}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-slate-500 text-[11px] italic">No research paper matches surfaced.</p>
            )}
          </div>

          {/* Evidence Gaps & Questions */}
          {brief.evidenceGaps && brief.evidenceGaps.length > 0 && (
            <div className="p-3 bg-amber-50/50 border border-amber-200 rounded space-y-1">
              <span className="font-bold text-amber-900 text-[10px] uppercase block">Surfaced Technical Gaps:</span>
              <ul className="list-disc pl-4 text-[11px] text-slate-700 space-y-0.5">
                {brief.evidenceGaps.map((g, idx) => (
                  <li key={idx}>{g}</li>
                ))}
              </ul>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 3. REVIEWER CONSENSUS & SCORE VARIANCE */}
      <Card className="border-slate-200">
        <CardHeader className="py-3 bg-slate-50 border-b border-slate-200">
          <CardTitle className="text-xs font-bold text-slate-800 uppercase flex items-center justify-between">
            <div className="flex items-center gap-1.5">
              <Scale className="h-3.5 w-3.5 text-blue-600" />
              <span>Reviewer Consensus &amp; Disagreement Matrix</span>
            </div>
            <Badge variant={brief.consensusStatus === "WITHIN_RANGE" ? "success" : "danger"} className="text-[10px]">
              {brief.consensusStatus}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="p-4 space-y-3 text-xs">
          {/* Explicit Non-Interference Disclaimer */}
          <div className="p-2.5 bg-blue-50 border border-blue-200 rounded text-[11px] text-slate-700 flex items-start gap-2">
            <ShieldAlert className="h-4 w-4 text-blue-600 flex-shrink-0 mt-0.5" />
            <span>{brief.consensusDisclaimer}</span>
          </div>

          {brief.disagreementFlags && brief.disagreementFlags.length > 0 ? (
            <div className="space-y-2">
              <h4 className="font-bold text-red-900 text-[10px] uppercase">
                Significant Score Differences (Variance &gt;= 2.0):
              </h4>
              {brief.disagreementFlags.map((flag, idx) => (
                <div key={idx} className="p-3 bg-red-50/50 border border-red-200 rounded space-y-1.5 font-mono">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-900">{flag.criterionName}</span>
                    <Badge variant="danger" className="text-[9px]">
                      Diff: {flag.difference.toFixed(1)}
                    </Badge>
                  </div>
                  <div className="flex items-center space-x-4 text-[11px] text-slate-700">
                    {Object.entries(flag.scoresByReviewer).map(([rev, score], sIdx) => (
                      <span key={sIdx}>
                        <span className="font-semibold text-slate-900">Reviewer {rev}:</span> {score.toFixed(1)}
                      </span>
                    ))}
                  </div>
                  {flag.permittedComments && flag.permittedComments.length > 0 && (
                    <p className="text-[10px] font-sans text-slate-600 italic">
                      Reviewer Note: &quot;{flag.permittedComments[0]}&quot;
                    </p>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-slate-600 text-[11px] italic">No significant reviewer score disagreements detected.</p>
          )}
        </CardContent>
      </Card>

      {/* 4. OUTSTANDING ACTIONS & DECISION ACTIONS */}
      <Card className="border-slate-200">
        <CardHeader className="py-3 bg-slate-50 border-b border-slate-200">
          <CardTitle className="text-xs font-bold text-slate-800 uppercase flex items-center gap-1.5">
            <Layers className="h-3.5 w-3.5 text-purple-600" />
            <span>Outstanding Actions &amp; Governance Step</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="p-4 space-y-4 text-xs">
          <div className="space-y-1.5 font-mono">
            {brief.outstandingActions.map((act, idx) => (
              <div key={idx} className="p-2 bg-slate-50 border rounded flex items-center space-x-2 text-[11px]">
                <HelpCircle className="h-3.5 w-3.5 text-slate-500" />
                <span>{act}</span>
              </div>
            ))}
          </div>

          <div className="pt-2 flex items-center justify-end space-x-3 border-t">
            <Button variant="outline" size="sm" className="text-xs font-mono">
              <ExternalLink className="h-3.5 w-3.5 mr-1" />
              Open Decision Pack
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
