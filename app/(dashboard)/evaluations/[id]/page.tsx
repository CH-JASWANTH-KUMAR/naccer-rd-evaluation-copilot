import React from "react";
import Link from "next/link";
import { notFound } from "next/navigation";
import { CheckCircle2, Edit3, XCircle, MessageSquare, Cpu } from "lucide-react";
import { proposalService } from "@/lib/api/proposals";
import { evaluationService } from "@/lib/api/evaluations";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { formatCurrency } from "@/lib/utils";

interface EvaluationWorkspacePageProps {
  params: Promise<{ id: string }>;
}

export default async function EvaluationWorkspacePage({ params }: EvaluationWorkspacePageProps) {
  const { id } = await params;
  const proposal = await proposalService.getProposalById(id);
  const evaluation = await evaluationService.getEvaluationByProposalId(id);

  if (!proposal || !evaluation) {
    notFound();
  }

  return (
    <div className="space-y-6">
      {/* Workspace Top Bar */}
      <Card className="bg-slate-900 text-white border-slate-800">
        <CardContent className="p-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            <div>
              <div className="flex items-center space-x-2">
                <Badge variant="outline" className="text-slate-300 border-slate-700 bg-slate-800 font-mono text-[10px]">
                  EVALUATION WORKSPACE
                </Badge>
                <Badge variant="info" className="text-[10px]">
                  {proposal.id}
                </Badge>
              </div>
              <h1 className="text-lg font-bold text-white mt-1 leading-snug">{proposal.title}</h1>
              <p className="text-xs text-slate-400 mt-0.5">
                Reviewer: <span className="text-slate-200 font-semibold">{evaluation.evaluatorName}</span> • Host: {proposal.institution.name}
              </p>
            </div>
            <div className="flex items-center space-x-3 flex-shrink-0">
              <Link href={`/reports?id=${proposal.id}`}>
                <Button variant="outline" size="sm" className="bg-slate-800 text-white border-slate-700 hover:bg-slate-700">
                  Generate Draft Report
                </Button>
              </Link>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Grid: Proposal Summary & Evaluation Criteria Rubric */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Proposal Summary & Key Findings */}
        <div className="lg:col-span-1 space-y-6">
          {/* Proposal Summary Card */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-xs uppercase tracking-wider font-mono text-slate-600">
                Proposal Summary
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-xs text-slate-700">
              <p className="bg-slate-50 p-3 rounded-md border border-slate-200 leading-relaxed">
                {proposal.summary}
              </p>
              <div className="space-y-1.5 font-mono text-[11px]">
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Proposed Budget:</span>
                  <span className="font-bold text-slate-900">{formatCurrency(proposal.proposedBudget)}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Duration:</span>
                  <span className="font-semibold text-slate-900">{proposal.durationMonths} Months</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-slate-500">Principal Investigator:</span>
                  <span className="font-semibold text-slate-900">{proposal.principalInvestigator}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* AI Finding Placeholder Panel */}
          <Card className="border-amber-200 bg-amber-50/30">
            <CardHeader className="pb-2">
              <div className="flex items-center space-x-2">
                <Cpu className="h-4 w-4 text-amber-700" />
                <CardTitle className="text-xs font-bold text-amber-900">
                  AI Copilot Findings Placeholder
                </CardTitle>
              </div>
            </CardHeader>
            <CardContent className="text-xs text-amber-900 space-y-2">
              <div className="p-2.5 bg-amber-100/60 rounded border border-amber-200 leading-relaxed text-[11px]">
                <span className="font-semibold">Base Setup Disclosure:</span> AI scoring models, RAG vector distance metrics, and automated compliance risk scores will be connected in Phase P0. No fake AI scores are generated in this phase.
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Evaluation Criteria Rubric Cards */}
        <div className="lg:col-span-2 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-slate-900">Evaluation Criteria &amp; Rubric</h2>
              <p className="text-xs text-slate-500">
                Score each criterion based on technical merit, novelty, methodology, and financial alignment.
              </p>
            </div>
            <div className="text-right">
              <span className="text-[10px] font-mono uppercase text-slate-500 block">Assigned Total</span>
              <span className="text-base font-bold text-slate-900 font-mono">
                {evaluation.criteria.reduce((acc, c) => acc + (c.assignedScore || 0), 0)} / 100
              </span>
            </div>
          </div>

          {/* Criteria Cards */}
          <div className="space-y-4">
            {evaluation.criteria.map((criterion, index) => (
              <Card key={criterion.id} className="border-slate-200 bg-white">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div>
                      <span className="text-[10px] font-mono uppercase text-slate-500 font-semibold">
                        Criterion {index + 1} • {criterion.category}
                      </span>
                      <CardTitle className="text-sm font-bold text-slate-900 mt-0.5">
                        {criterion.title}
                      </CardTitle>
                    </div>
                    <Badge variant="outline" className="font-mono text-xs bg-slate-50">
                      Max {criterion.maxScore} Pts
                    </Badge>
                  </div>
                  <CardDescription className="text-xs text-slate-600 mt-1">
                    {criterion.description}
                  </CardDescription>
                </CardHeader>

                <CardContent className="space-y-4">
                  {/* AI Finding Placeholder inside criterion */}
                  <div className="p-3 bg-slate-50 rounded-md border border-slate-200 text-xs text-slate-600">
                    <span className="font-mono text-[10px] uppercase font-bold text-slate-500 block mb-0.5">
                      AI Engine Finding Placeholder:
                    </span>
                    <span className="italic text-slate-500">{criterion.findingsPlaceholder}</span>
                  </div>

                  {/* Reviewer Score Input & Progress */}
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 items-center pt-1">
                    <div className="sm:col-span-2 space-y-1">
                      <div className="flex justify-between text-xs font-semibold text-slate-700">
                        <span>Score Progress</span>
                        <span>{criterion.assignedScore || 0} / {criterion.maxScore}</span>
                      </div>
                      <Progress value={criterion.assignedScore || 0} max={criterion.maxScore} />
                    </div>
                    <div className="sm:col-span-1">
                      <label className="text-[10px] font-mono uppercase text-slate-500 block mb-1">
                        Criterion Score
                      </label>
                      <Input
                        type="number"
                        defaultValue={criterion.assignedScore || 0}
                        max={criterion.maxScore}
                        min={0}
                        className="h-8 text-xs font-mono font-bold"
                      />
                    </div>
                  </div>

                  {/* Reviewer Notes */}
                  <div>
                    <label className="text-[10px] font-mono uppercase text-slate-500 block mb-1">
                      Reviewer Technical Comment
                    </label>
                    <textarea
                      defaultValue={criterion.reviewerNotes}
                      rows={2}
                      className="w-full rounded-md border border-slate-300 bg-white p-2 text-xs text-slate-900 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-slate-950"
                      placeholder="Add reviewer technical justification..."
                    />
                  </div>

                  {/* Reviewer Action Buttons */}
                  <div className="pt-2 border-t border-slate-100 flex flex-wrap items-center justify-between gap-2">
                    <span className="text-[10px] font-mono uppercase text-slate-400 font-semibold">
                      Reviewer Action:
                    </span>
                    <div className="flex items-center space-x-2">
                      <Button variant="outline" size="sm" className="h-7 text-xs text-emerald-800 bg-emerald-50 hover:bg-emerald-100 border-emerald-200">
                        <CheckCircle2 className="h-3 w-3 mr-1 text-emerald-600" />
                        Confirm Finding
                      </Button>
                      <Button variant="outline" size="sm" className="h-7 text-xs text-amber-800 bg-amber-50 hover:bg-amber-100 border-amber-200">
                        <Edit3 className="h-3 w-3 mr-1 text-amber-600" />
                        Modify Score
                      </Button>
                      <Button variant="outline" size="sm" className="h-7 text-xs text-red-800 bg-red-50 hover:bg-red-100 border-red-200">
                        <XCircle className="h-3 w-3 mr-1 text-red-600" />
                        Reject Criterion
                      </Button>
                      <Button variant="ghost" size="sm" className="h-7 text-xs text-slate-700">
                        <MessageSquare className="h-3 w-3 mr-1 text-slate-500" />
                        Add Comment
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
