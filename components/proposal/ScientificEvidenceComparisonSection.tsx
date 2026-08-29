"use client";

import React, { useEffect, useState } from "react";
import { Sparkles, AlertTriangle, HelpCircle, FileText, Loader2, Database, BookOpen } from "lucide-react";
import {
  proposalService,
  ProposalScientificComparisonResponse,
  ScientificComparisonRecord,
  EvidenceGapRecord,
  ReviewerQuestionRecord,
} from "@/lib/api/proposals";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";

interface Props {
  proposalId: string;
}

export function ScientificEvidenceComparisonSection({ proposalId }: Props) {
  const [comparison, setComparison] = useState<ProposalScientificComparisonResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    proposalService
      .getScientificComparison(proposalId)
      .then((data) => {
        if (isMounted) {
          setComparison(data);
          setLoading(false);
        }
      })
      .catch(() => {
        if (isMounted) {
          setError("Failed to load scientific evidence comparison.");
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [proposalId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12 text-muted-foreground">
        <Loader2 className="h-6 w-6 animate-spin mr-2" />
        <span>Generating multi-source scientific comparison...</span>
      </div>
    );
  }

  if (error || !comparison) {
    return (
      <Card className="p-6 text-center text-muted-foreground text-xs border-dashed">
        <AlertTriangle className="h-8 w-8 text-amber-500 mx-auto mb-2 opacity-60" />
        <p>{error || "No scientific comparison data available."}</p>
      </Card>
    );
  }

  const renderStatusBadge = (status: string) => {
    switch (status) {
      case "MATCHING":
        return <Badge className="bg-emerald-500/10 text-emerald-600 border-emerald-500/30 text-[10px]">MATCHING</Badge>;
      case "PARTIALLY_MATCHING":
        return <Badge className="bg-amber-500/10 text-amber-600 border-amber-500/30 text-[10px]">PARTIALLY MATCHING</Badge>;
      case "DIFFERENT":
        return <Badge className="bg-blue-500/10 text-blue-600 border-blue-500/30 text-[10px]">DIFFERENT</Badge>;
      case "NOT_REPORTED":
        return <Badge variant="secondary" className="text-[10px]">NOT REPORTED</Badge>;
      default:
        return <Badge variant="outline" className="text-[10px]">{status}</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner & Summary */}
      <Card className="p-4 bg-muted/30 border-l-4 border-l-primary">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              <h2 className="text-base font-bold text-foreground">Scientific Evidence Comparison</h2>
              <Badge variant="outline" className="bg-primary/10 text-primary text-xs">
                Human Decision-Support
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Multi-source comparison of proposal methodology, algorithms, datasets, metrics, and validation against historical CIL projects & scientific literature.
            </p>
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            <Badge variant="outline" className="bg-emerald-500/10 text-emerald-600 text-[11px]">
              {comparison.comparisonSummary.matching || 0} Matching
            </Badge>
            <Badge variant="outline" className="bg-amber-500/10 text-amber-600 text-[11px]">
              {comparison.comparisonSummary.partially_matching || 0} Partially Matching
            </Badge>
            <Badge variant="outline" className="bg-blue-500/10 text-blue-600 text-[11px]">
              {comparison.comparisonSummary.different || 0} Different
            </Badge>
            <Badge variant="outline" className="bg-slate-100 text-slate-600 text-[11px]">
              {comparison.comparisonSummary.not_reported || 0} Not Reported
            </Badge>
          </div>
        </div>
      </Card>

      {/* 10 Scientific Dimensions Table */}
      <Card className="p-4 space-y-3">
        <div className="flex items-center gap-2 border-b border-border pb-2">
          <FileText className="h-4 w-4 text-primary" />
          <h3 className="font-semibold text-sm">Scientific Dimensions Comparison</h3>
        </div>

        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-48">Dimension</TableHead>
              <TableHead>Proposal Value</TableHead>
              <TableHead>Literature / Evidence Value</TableHead>
              <TableHead className="w-36">Status</TableHead>
              <TableHead className="w-36">Evidence ID</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {comparison.comparisons.map((c: ScientificComparisonRecord) => (
              <TableRow key={c.comparisonId}>
                <TableCell className="font-medium text-xs">
                  {c.dimension.replace("_", " ")}
                </TableCell>
                <TableCell className="text-xs font-mono max-w-xs truncate" title={c.proposalValue}>
                  {c.proposalValue}
                </TableCell>
                <TableCell className="text-xs font-mono max-w-xs truncate" title={c.evidenceValue}>
                  {c.evidenceValue}
                </TableCell>
                <TableCell>{renderStatusBadge(c.comparisonStatus)}</TableCell>
                <TableCell>
                  <Badge variant="default" className="font-mono text-[10px]">
                    [{c.evidenceId}]
                  </Badge>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Evidence Gaps Card */}
        <Card className="p-4 space-y-3">
          <div className="flex items-center gap-2 border-b border-border pb-2">
            <AlertTriangle className="h-4 w-4 text-amber-500" />
            <h3 className="font-semibold text-sm">Identified Evidence Gaps</h3>
          </div>

          <div className="space-y-3">
            {comparison.evidenceGaps.map((g: EvidenceGapRecord, idx: number) => (
              <div key={idx} className="p-3 bg-amber-500/10 border border-amber-500/20 rounded text-xs space-y-1.5">
                <div className="flex items-center justify-between font-semibold text-amber-800 dark:text-amber-300">
                  <span>⚠ {g.gap}</span>
                  <Badge variant="outline" className="font-mono text-[10px]">
                    [{g.evidenceSupportingGap}]
                  </Badge>
                </div>
                <p className="text-[11px] text-muted-foreground leading-relaxed">
                  <strong className="text-foreground">Suggested Reviewer Action:</strong> {g.reviewerAction}
                </p>
              </div>
            ))}
          </div>
        </Card>

        {/* Targeted Reviewer Questions Card */}
        <Card className="p-4 space-y-3">
          <div className="flex items-center gap-2 border-b border-border pb-2">
            <HelpCircle className="h-4 w-4 text-primary" />
            <h3 className="font-semibold text-sm">Targeted Reviewer Questions</h3>
          </div>

          <div className="space-y-3">
            {comparison.reviewerQuestions.map((q: ReviewerQuestionRecord) => (
              <div key={q.questionId} className="p-3 bg-muted/40 border border-border/50 rounded text-xs space-y-1.5">
                <div className="flex items-center justify-between font-medium text-foreground">
                  <span>{q.questionId}: {q.question}</span>
                  <Badge variant="outline" className="font-mono text-[10px]">
                    [{q.evidenceId}]
                  </Badge>
                </div>
                <p className="text-[11px] text-muted-foreground">
                  <strong>Evidence Grounding Rationale:</strong> {q.rationale}
                </p>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Evidence Sources Card */}
      <Card className="p-4 space-y-3">
        <div className="flex items-center gap-2 border-b border-border pb-2">
          <Database className="h-4 w-4 text-emerald-600" />
          <h3 className="font-semibold text-sm">Retrieved Evidence Sources</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {comparison.evidenceSources.map((s) => (
            <div key={s.evidenceId} className="p-3 rounded border border-border/50 bg-muted/20 text-xs space-y-1">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {s.sourceType === "HISTORICAL_PROJECT" ? (
                    <Database className="h-3.5 w-3.5 text-blue-500" />
                  ) : (
                    <BookOpen className="h-3.5 w-3.5 text-emerald-500" />
                  )}
                  <Badge variant="default" className="font-mono text-[10px]">
                    [{s.evidenceId}]
                  </Badge>
                </div>
                <Badge variant="outline" className="text-[10px]">
                  {Math.round(s.relevanceScore * 100)}% Relevance
                </Badge>
              </div>
              <div className="font-medium line-clamp-1">{s.title}</div>
              <div className="text-[10px] text-muted-foreground flex gap-1 flex-wrap">
                {s.matchedDimensions.map((m) => (
                  <span key={m} className="bg-muted px-1 rounded">
                    {m}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
