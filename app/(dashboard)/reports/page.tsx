import React from "react";
import { Printer, Download, AlertTriangle } from "lucide-react";
import { reportService } from "@/lib/api/reports";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { formatCurrency, formatDate } from "@/lib/utils";

interface ReportsPageProps {
  searchParams?: Promise<{ id?: string }>;
}

export default async function ReportsPage({ searchParams }: ReportsPageProps) {
  const resolvedParams = (await searchParams) || {};
  const proposalId = resolvedParams.id || "PROP-2026-001";
  const report = await reportService.getReportByProposalId(proposalId);
  const { proposal, evaluation } = report;

  return (
    <div className="space-y-6">
      {/* Top Action Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">
            Comprehensive R&amp;D Evaluation Report
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Formal technical assessment synthesis document for NaCCER / CMPDI review committee.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <Button variant="outline" size="sm">
            <Printer className="h-3.5 w-3.5 mr-1.5" />
            Print Report
          </Button>
          <Button size="sm">
            <Download className="h-3.5 w-3.5 mr-1.5" />
            Export Official PDF
          </Button>
        </div>
      </div>

      {/* Main Report Container */}
      <div className="space-y-6 bg-white p-8 rounded-lg border border-slate-200 shadow-xs max-w-5xl mx-auto">
        {/* Report Header */}
        <div className="border-b-2 border-slate-900 pb-6 flex items-start justify-between">
          <div>
            <div className="flex items-center space-x-2">
              <span className="h-3 w-3 bg-emerald-600 rounded-xs" />
              <span className="text-xs font-bold uppercase tracking-wider text-slate-600 font-mono">
                NaCCER R&amp;D TECHNICAL EVALUATION REPORT
              </span>
            </div>
            <h2 className="text-lg font-bold text-slate-900 mt-2">{proposal.title}</h2>
            <p className="text-xs text-slate-500 font-mono mt-1">
              Proposal ID: {proposal.id} • Date Generated: {formatDate(report.generatedAt)}
            </p>
          </div>
          <Badge variant="warning" className="text-xs font-bold py-1 px-3">
            RECOMMENDATION: NEEDS REVISION
          </Badge>
        </div>

        {/* 1. Proposal Information Section */}
        <div className="space-y-3">
          <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider font-mono border-l-2 border-slate-900 pl-2">
            1. Proposal Information
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 bg-slate-50 rounded-md border border-slate-200 text-xs">
            <div>
              <span className="text-slate-500 font-mono text-[10px] uppercase block">Institution</span>
              <span className="font-bold text-slate-900">{proposal.institution.name}</span>
            </div>
            <div>
              <span className="text-slate-500 font-mono text-[10px] uppercase block">Principal Investigator</span>
              <span className="font-bold text-slate-900">{proposal.principalInvestigator}</span>
            </div>
            <div>
              <span className="text-slate-500 font-mono text-[10px] uppercase block">Research Domain</span>
              <span className="font-semibold text-slate-800">{proposal.domain}</span>
            </div>
            <div>
              <span className="text-slate-500 font-mono text-[10px] uppercase block">Proposed Budget</span>
              <span className="font-mono font-bold text-slate-900">{formatCurrency(proposal.proposedBudget)}</span>
            </div>
          </div>
        </div>

        {/* 2. Executive Summary */}
        <div className="space-y-3">
          <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider font-mono border-l-2 border-slate-900 pl-2">
            2. Executive Summary
          </h3>
          <p className="text-xs text-slate-700 leading-relaxed bg-slate-50/50 p-4 rounded-md border border-slate-200">
            {report.executiveSummary}
          </p>
        </div>

        {/* 3. Completeness Findings */}
        <div className="space-y-3">
          <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider font-mono border-l-2 border-slate-900 pl-2">
            3. Completeness &amp; Compliance Findings
          </h3>
          <div className="p-4 bg-slate-50 rounded-md border border-slate-200 text-xs text-slate-600">
            <span className="font-mono text-[10px] text-slate-500 uppercase font-bold block mb-1">
              Automated Completeness Check:
            </span>
            <span>Document completeness engine will evaluate form attachments in Phase P0. Base setup structure validated.</span>
          </div>
        </div>

        {/* 4. Financial Findings */}
        <div className="space-y-3">
          <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider font-mono border-l-2 border-slate-900 pl-2">
            4. Financial &amp; Budget Findings
          </h3>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>COST HEAD</TableHead>
                <TableHead>PROPOSED AMOUNT</TableHead>
                <TableHead>BENCHMARK COST</TableHead>
                <TableHead>COMPLIANCE</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {evaluation.financialChecks.map((fin) => (
                <TableRow key={fin.id}>
                  <TableCell className="font-medium text-slate-900">{fin.costHead}</TableCell>
                  <TableCell className="font-mono font-bold text-slate-900">{formatCurrency(fin.proposedAmount)}</TableCell>
                  <TableCell className="font-mono text-slate-600">{fin.benchmarkAmount ? formatCurrency(fin.benchmarkAmount) : "N/A"}</TableCell>
                  <TableCell>
                    {fin.complianceStatus === "FLAGGED" ? (
                      <Badge variant="danger">Flagged Variance</Badge>
                    ) : (
                      <Badge variant="success">Compliant</Badge>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        {/* 5. Historical Benchmark */}
        <div className="space-y-3">
          <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider font-mono border-l-2 border-slate-900 pl-2">
            5. Historical Benchmark Analysis
          </h3>
          <div className="p-4 bg-slate-50 rounded-md border border-slate-200 text-xs text-slate-600">
            <span>Vector similarity comparison against prior CIL/NaCCER projects will populate upon pgvector integration in Phase P0.</span>
          </div>
        </div>

        {/* 6. Novelty Assessment */}
        <div className="space-y-3">
          <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider font-mono border-l-2 border-slate-900 pl-2">
            6. Novelty &amp; Innovation Assessment
          </h3>
          <div className="p-4 bg-slate-50 rounded-md border border-slate-200 text-xs text-slate-600">
            <span>NLP novelty distance score will be displayed here in Phase P0.</span>
          </div>
        </div>

        {/* 7. Evaluation Scores Breakdown */}
        <div className="space-y-3">
          <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider font-mono border-l-2 border-slate-900 pl-2">
            7. Evaluation Rubric Scores Breakdown
          </h3>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>CRITERION</TableHead>
                <TableHead>CATEGORY</TableHead>
                <TableHead>MAX SCORE</TableHead>
                <TableHead>ASSIGNED SCORE</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {evaluation.criteria.map((crit) => (
                <TableRow key={crit.id}>
                  <TableCell className="font-semibold text-slate-900">{crit.title}</TableCell>
                  <TableCell className="font-mono text-xs">{crit.category}</TableCell>
                  <TableCell className="font-mono text-xs font-bold">{crit.maxScore}</TableCell>
                  <TableCell className="font-mono text-xs font-bold text-slate-900">{crit.assignedScore || 0}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        {/* 8. Risk Flags */}
        <div className="space-y-3">
          <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider font-mono border-l-2 border-slate-900 pl-2">
            8. Identified Risk Flags
          </h3>
          <div className="p-3 bg-red-50 rounded-md border border-red-200 text-xs text-red-900 flex items-start space-x-2">
            <AlertTriangle className="h-4 w-4 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <span className="font-bold">Financial Risk Flag:</span> Equipment cost head for Multi-Gas Sensor Test Rig exceeds benchmark by 15.6%. Requires justification from Principal Investigator.
            </div>
          </div>
        </div>

        {/* 9. Evidence References */}
        <div className="space-y-3">
          <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider font-mono border-l-2 border-slate-900 pl-2">
            9. Evidence &amp; Source Citations
          </h3>
          <div className="space-y-2">
            {evaluation.evidences.map((ev) => (
              <div key={ev.id} className="p-3 bg-slate-50 rounded border border-slate-200 text-xs font-mono">
                <span className="font-bold text-slate-900">[{ev.sourceDocument} • Page {ev.pageNumber}]</span>
                <p className="text-slate-600 font-sans mt-1">&quot;{ev.extractedSnippet}&quot;</p>
              </div>
            ))}
          </div>
        </div>

        {/* 10 & 11. Reviewer Decision & Comments */}
        <div className="space-y-3 pt-4 border-t border-slate-200">
          <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider font-mono border-l-2 border-slate-900 pl-2">
            10. Final Reviewer Recommendation &amp; Comments
          </h3>
          <div className="p-4 bg-slate-100 rounded-md border border-slate-300 text-xs space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-bold text-slate-900">Reviewer: Dr. A. Sharma (Senior Technical Evaluator)</span>
              <Badge variant="warning">NEEDS REVISION</Badge>
            </div>
            <p className="text-slate-700 italic">
              &quot;Proposal shows strong technical potential in spatial CH4 detection. However, financial justification for ATEX Zone 0 enclosure equipment rates and clarification on underground field trial access permissions must be submitted before final approval.&quot;
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
