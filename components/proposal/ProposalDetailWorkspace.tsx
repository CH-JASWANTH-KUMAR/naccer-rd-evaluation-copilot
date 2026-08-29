"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { FileText, CheckCircle2, AlertTriangle, AlertCircle, Sparkles, RefreshCw, ArrowRight, DollarSign, BookOpen, Info } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Proposal } from "@/lib/types";
import { proposalService, ProposalCompletenessReport, FinancialComplianceReport, ProposalSourceProvenance } from "@/lib/api/proposals";
import { SimilarityResultItem } from "@/lib/api/projects";
import { formatCurrency } from "@/lib/utils";
import { ScientificEvidenceComparisonSection } from "@/components/proposal/ScientificEvidenceComparisonSection";
import { EvaluationRubricSection } from "@/components/proposal/EvaluationRubricSection";

interface ProposalDetailWorkspaceProps {
  initialProposal: Proposal;
}

export function ProposalDetailWorkspace({ initialProposal }: ProposalDetailWorkspaceProps) {
  const [proposal, setProposal] = useState<Proposal>(initialProposal);
  const [activeTab, setActiveTab] = useState<"structured" | "completeness" | "financial" | "similar" | "scientific" | "rubric">("structured");

  const [completenessReport, setCompletenessReport] = useState<ProposalCompletenessReport | null>(null);
  const [complianceReport, setComplianceReport] = useState<FinancialComplianceReport | null>(null);
  const [sourceProvenance, setSourceProvenance] = useState<ProposalSourceProvenance | null>(null);
  const [similarProjects, setSimilarProjects] = useState<SimilarityResultItem[] | null>(null);

  const [loading, setLoading] = useState(false);
  const [reprocessing, setReprocessing] = useState(false);
  const [evidenceDrawerContent, setEvidenceDrawerContent] = useState<{ title: string; text: string; pages: string; evidenceId: string } | null>(null);

  useEffect(() => {
    let isMounted = true;
    Promise.all([
      proposalService.getProposalCompleteness(proposal.id),
      proposalService.getProposalCompliance(proposal.id),
      proposalService.getProposalSource(proposal.id),
    ]).then(([comp, fin, src]) => {
      if (isMounted) {
        if (comp) setCompletenessReport(comp);
        if (fin) setComplianceReport(fin);
        if (src) setSourceProvenance(src);
      }
    });

    return () => {
      isMounted = false;
    };
  }, [proposal.id]);

  const handleReprocess = async () => {
    setReprocessing(true);
    try {
      const updated = await proposalService.reprocessProposal(proposal.id);
      setProposal(updated);
      const [comp, fin] = await Promise.all([
        proposalService.getProposalCompleteness(proposal.id),
        proposalService.getProposalCompliance(proposal.id),
      ]);
      if (comp) setCompletenessReport(comp);
      if (fin) setComplianceReport(fin);
    } catch {
      // Handle error
    } finally {
      setReprocessing(false);
    }
  };

  const handleLoadSimilarProjects = async () => {
    setLoading(true);
    try {
      const res = await proposalService.findSimilarProjectsForProposal(proposal.id, 5);
      setSimilarProjects(res.results);
    } catch {
      // Handle error
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Proposal Header Card */}
      <Card className="bg-white border-slate-200">
        <CardContent className="p-6">
          <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
            <div className="space-y-2 max-w-3xl">
              <div className="flex flex-wrap items-center gap-2">
                <Badge variant="outline" className="font-mono text-xs bg-slate-100">
                  {proposal.proposalReference || proposal.id}
                </Badge>
                <Badge variant="outline" className="text-xs">
                  {proposal.domain}
                </Badge>
                <Badge
                  variant={proposal.documentType === "RESEARCH_PAPER" ? "secondary" : "info"}
                  className="text-xs font-bold font-mono"
                  title={proposal.documentTypeReasons?.join(" | ")}
                >
                  DOC TYPE: {proposal.documentType || "R&D_PROPOSAL"} ({proposal.documentTypeConfidence || "HIGH"})
                </Badge>
                <Badge
                  variant={proposal.completenessStatus === "COMPLETE" ? "success" : "warning"}
                  className="text-xs font-bold"
                >
                  {proposal.completenessStatus === "COMPLETE" ? "COMPLETENESS: PASS" : "COMPLETENESS: INCOMPLETE"}
                </Badge>
                <Badge
                  variant={
                    proposal.complianceStatus === "COMPLIANT"
                      ? "info"
                      : proposal.complianceStatus === "FLAGGED"
                      ? "danger"
                      : "warning"
                  }
                  className="text-xs font-bold"
                >
                  {proposal.complianceStatus === "COMPLIANT" ? "FINANCIAL: COMPLIANT" : `FINANCIAL: ${proposal.complianceStatus}`}
                </Badge>
              </div>

              <h1 className="text-lg font-bold text-slate-900 leading-snug">{proposal.title}</h1>
              <p className="text-xs text-slate-600">
                Submitting Institution: <span className="font-semibold text-slate-800">{proposal.institution.name}</span> • Principal Investigator: <span className="font-semibold text-slate-800">{proposal.principalInvestigator}</span>
              </p>
            </div>

            <div className="flex flex-col items-start lg:items-end space-y-2 flex-shrink-0">
              <span className="text-[10px] font-mono uppercase text-slate-500 block">Requested R&amp;D Budget</span>
              <span className="text-xl font-bold font-mono text-slate-900">
                {formatCurrency(proposal.budgetTotal || proposal.proposedBudget || 0)}
              </span>

              <Button
                variant="outline"
                size="sm"
                className="h-8 text-xs border-slate-300"
                disabled={reprocessing}
                onClick={handleReprocess}
              >
                <RefreshCw className={`h-3.5 w-3.5 mr-1 ${reprocessing ? "animate-spin" : ""}`} />
                Re-Run Scrutiny Engines
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Reviewer Safety Disclaimer */}
      <div className="p-3 bg-amber-50 border border-amber-200 rounded-md flex items-start space-x-2.5 text-xs text-amber-900">
        <AlertCircle className="h-4 w-4 text-amber-600 flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-bold">Reviewer Safety &amp; Scrutiny Directive:</span> Preliminary scrutiny checks perform deterministic document structuring, completeness checking, and financial arithmetic validation. They do <strong>not</strong> constitute an automated approval, rejection, or novelty decision.
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex items-center space-x-1 border-b border-slate-200 pb-2">
        <button
          type="button"
          onClick={() => setActiveTab("structured")}
          className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-colors flex items-center space-x-1.5 ${
            activeTab === "structured" ? "bg-blue-50 text-blue-700 border border-blue-200" : "text-slate-600 hover:text-slate-900"
          }`}
        >
          <FileText className="h-3.5 w-3.5" />
          <span>Structured Proposal &amp; Source</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("completeness")}
          className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-colors flex items-center space-x-1.5 ${
            activeTab === "completeness" ? "bg-blue-50 text-blue-700 border border-blue-200" : "text-slate-600 hover:text-slate-900"
          }`}
        >
          <CheckCircle2 className="h-3.5 w-3.5" />
          <span>Completeness Report ({completenessReport?.missingFields.length || 0} Missing)</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("financial")}
          className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-colors flex items-center space-x-1.5 ${
            activeTab === "financial" ? "bg-blue-50 text-blue-700 border border-blue-200" : "text-slate-600 hover:text-slate-900"
          }`}
        >
          <DollarSign className="h-3.5 w-3.5" />
          <span>Financial Compliance</span>
        </button>

        <button
          type="button"
          onClick={() => {
            setActiveTab("similar");
            if (!similarProjects) handleLoadSimilarProjects();
          }}
          className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-colors flex items-center space-x-1.5 ${
            activeTab === "similar" ? "bg-blue-50 text-blue-700 border border-blue-200" : "text-slate-600 hover:text-slate-900"
          }`}
        >
          <Sparkles className="h-3.5 w-3.5 text-blue-600" />
          <span>P0.4 Historical Benchmark Search</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("rubric")}
          className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-colors flex items-center space-x-1.5 ${
            activeTab === "rubric" ? "bg-blue-50 text-blue-700 border border-blue-200" : "text-slate-600 hover:text-slate-900"
          }`}
        >
          <BookOpen className="h-3.5 w-3.5 text-indigo-600" />
          <span>Evaluation Rubric (MoC v1.0)</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("scientific")}
          className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-colors flex items-center space-x-1.5 ${
            activeTab === "scientific" ? "bg-blue-50 text-blue-700 border border-blue-200" : "text-slate-600 hover:text-slate-900"
          }`}
        >
          <Sparkles className="h-3.5 w-3.5 text-emerald-600" />
          <span>Scientific Evidence Comparison</span>
        </button>
      </div>

      {/* TAB 1: Structured Proposal & Source Provenance */}
      {activeTab === "structured" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="lg:col-span-2">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <div>
                <CardTitle className="text-sm">
                  {proposal.documentType === "RESEARCH_PAPER"
                    ? "Native Research Paper Structure & Sections"
                    : "Structured Proposal Fields & Sections"}
                </CardTitle>
                <CardDescription className="text-xs">
                  {proposal.documentType === "RESEARCH_PAPER"
                    ? "Extracted native research paper sections with concise summaries and full source provenance."
                    : "Parsed section fields extracted from PDF proposal document."}
                </CardDescription>
              </div>
              <Badge variant="outline" className="font-mono text-xs uppercase bg-slate-100">
                {proposal.documentType || "R&D_PROPOSAL"}
              </Badge>
            </CardHeader>
            <CardContent className="space-y-4 text-xs">
              {proposal.structuredSections && proposal.structuredSections.length > 0 ? (
                proposal.structuredSections
                  .filter((sec) => sec.status === "REPORTED" && sec.summary !== "NOT_REPORTED")
                  .map((sec) => (
                    <div key={sec.key} className="p-3 bg-slate-50 rounded-lg border border-slate-200 space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-slate-800 text-xs flex items-center gap-2">
                          {sec.displayTitle}
                          <Badge variant="outline" className="text-[10px] font-mono bg-white text-slate-600">
                            {sec.evidenceId} • Pages {sec.sourcePageStart}-{sec.sourcePageEnd}
                          </Badge>
                        </span>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-6 text-[10px] text-blue-600 hover:text-blue-800 hover:bg-blue-50 px-2"
                          onClick={() =>
                            setEvidenceDrawerContent({
                              title: sec.displayTitle,
                              text: sec.content,
                              pages: `Pages ${sec.sourcePageStart}-${sec.sourcePageEnd}`,
                              evidenceId: sec.evidenceId,
                            })
                          }
                        >
                          <BookOpen className="h-3 w-3 mr-1" />
                          View Source Evidence
                        </Button>
                      </div>
                      <p className="text-slate-700 bg-white p-2.5 rounded border border-slate-100 whitespace-pre-line leading-relaxed">
                        {sec.summary}
                      </p>
                    </div>
                  ))
              ) : (
                <>
                  <div>
                    <span className="font-mono text-[10px] uppercase font-semibold text-slate-400 block mb-1">
                      Problem Statement &amp; Research Gap
                    </span>
                    <p className="text-slate-700 bg-slate-50 p-3 rounded border border-slate-200 whitespace-pre-wrap">
                      {proposal.problemStatement || "Section text not extracted."}
                    </p>
                  </div>

                  <div>
                    <span className="font-mono text-[10px] uppercase font-semibold text-slate-400 block mb-1">
                      Project Objectives
                    </span>
                    <p className="text-slate-700 bg-slate-50 p-3 rounded border border-slate-200 whitespace-pre-wrap">
                      {proposal.objectives || "Section text not extracted."}
                    </p>
                  </div>

                  <div>
                    <span className="font-mono text-[10px] uppercase font-semibold text-slate-400 block mb-1">
                      Proposed Methodology
                    </span>
                    <p className="text-slate-700 bg-slate-50 p-3 rounded border border-slate-200 whitespace-pre-wrap">
                      {proposal.methodology || "Section text not extracted."}
                    </p>
                  </div>
                </>
              )}
            </CardContent>
          </Card>

          {/* Page Provenance Panel */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Document Page Provenance</CardTitle>
              <CardDescription className="text-xs">
                Page-by-page audit trace of source proposal PDF.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 text-xs">
              {sourceProvenance && sourceProvenance.documents.length > 0 ? (
                sourceProvenance.documents.map((doc) => (
                  <div key={doc.documentId} className="space-y-2">
                    <div className="p-2.5 bg-slate-50 rounded border border-slate-200 space-y-1">
                      <span className="font-semibold text-slate-800 block truncate">{doc.filename}</span>
                      <span className="text-[10px] font-mono text-slate-500 block">
                        {doc.pageCount} Pages • {(doc.fileSize / 1024).toFixed(1)} KB
                      </span>
                      {doc.documentHash && (
                        <p className="text-[9px] font-mono text-slate-400 truncate">
                          SHA-256: {doc.documentHash}
                        </p>
                      )}
                    </div>

                    <h5 className="font-semibold text-slate-700 text-[11px] uppercase">Extracted Source Pages</h5>
                    <div className="space-y-1.5 max-h-60 overflow-y-auto pr-1">
                      {doc.pages.map((p) => (
                        <div key={p.pageNumber} className="p-2 bg-white rounded border border-slate-200 text-[11px]">
                          <span className="font-mono font-bold text-blue-600 block mb-0.5">Page {p.pageNumber}</span>
                          <p className="text-slate-600 line-clamp-3 whitespace-pre-wrap">{p.extractedText}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                ))
              ) : (
                <div className="p-4 text-center text-slate-500">No document provenance records found.</div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* TAB 2: Completeness Scrutiny Report */}
      {activeTab === "completeness" && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Preliminary Scrutiny Checklist Findings</CardTitle>
            <CardDescription className="text-xs">
              Mandatory proposal field completeness report generated by rule engine.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {completenessReport ? (
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-slate-50 rounded border border-slate-200">
                  <span className="text-xs font-semibold text-slate-700">Completeness Status:</span>
                  <Badge variant={completenessReport.status === "COMPLETE" ? "success" : "warning"}>
                    {completenessReport.status}
                  </Badge>
                </div>

                <div className="space-y-2">
                  <h4 className="text-xs font-semibold text-slate-800 uppercase">Checklist Items</h4>
                  {completenessReport.findings.map((f, idx) => (
                    <div
                      key={idx}
                      className={`p-3 rounded border text-xs flex items-start space-x-2.5 ${
                        f.severity === "ERROR"
                          ? "bg-red-50 border-red-200 text-red-900"
                          : f.severity === "WARNING"
                          ? "bg-amber-50 border-amber-200 text-amber-900"
                          : "bg-blue-50 border-blue-200 text-blue-900"
                      }`}
                    >
                      {f.severity === "ERROR" ? (
                        <AlertTriangle className="h-4 w-4 text-red-600 flex-shrink-0 mt-0.5" />
                      ) : f.severity === "WARNING" ? (
                        <AlertCircle className="h-4 w-4 text-amber-600 flex-shrink-0 mt-0.5" />
                      ) : (
                        <CheckCircle2 className="h-4 w-4 text-blue-600 flex-shrink-0 mt-0.5" />
                      )}
                      <div>
                        <span className="font-bold uppercase tracking-wider text-[10px] block">{f.field} [{f.severity}]</span>
                        <p className="font-medium">{f.message}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="p-4 text-center text-xs text-slate-500">Loading completeness report...</div>
            )}
          </CardContent>
        </Card>
      )}

      {/* TAB 3: Financial Compliance Report */}
      {activeTab === "financial" && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Rule-Based Financial Arithmetic &amp; Compliance Scrutiny</CardTitle>
            <CardDescription className="text-xs">
              Deterministic verification of proposed budget totals and itemized cost component arithmetic.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Reviewer Guidance Line */}
            <div className="p-3 bg-blue-50/60 rounded-md border border-blue-200/80 flex items-start space-x-2.5 text-xs text-slate-700">
              <Info className="h-4 w-4 text-blue-600 flex-shrink-0 mt-0.5" />
              <span>
                Arithmetic verification checks whether reliably extracted itemized costs reconcile with the declared total.
                Missing or incomplete cost heads are not assumed to be zero.
              </span>
            </div>

            {complianceReport ? (
              <div className="space-y-4">
                {/* Metric Cards Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
                  <div className="p-3 bg-slate-50 rounded border border-slate-200">
                    <span className="text-[10px] font-mono text-slate-400 uppercase block">Declared Total</span>
                    <span className="text-sm font-bold font-mono text-slate-900">{formatCurrency(complianceReport.declaredTotal)}</span>
                  </div>

                  <div className="p-3 bg-slate-50 rounded border border-slate-200">
                    <span className="text-[10px] font-mono text-slate-400 uppercase block">Calculated Component Sum</span>
                    <span className="text-sm font-bold font-mono text-slate-900">
                      {complianceReport.calculatedTotal !== null ? formatCurrency(complianceReport.calculatedTotal) : "Not Verifiable"}
                    </span>
                  </div>

                  <div className="p-3 bg-slate-50 rounded border border-slate-200">
                    <span className="text-[10px] font-mono text-slate-400 uppercase block">Variance</span>
                    <span className="text-sm font-bold font-mono text-slate-900">
                      {complianceReport.varianceAmount !== null ? formatCurrency(complianceReport.varianceAmount) : "N/A"}
                    </span>
                  </div>

                  <div className="p-3 bg-slate-50 rounded border border-slate-200">
                    <span className="text-[10px] font-mono text-slate-400 uppercase block">Arithmetic Status</span>
                    <Badge
                      variant={
                        complianceReport.arithmeticStatus === "MATCH"
                          ? "success"
                          : complianceReport.arithmeticStatus === "MISMATCH"
                          ? "danger"
                          : "warning"
                      }
                      className="text-xs font-bold mt-1"
                    >
                      {complianceReport.arithmeticStatus === "NOT_VERIFIABLE" ? "NOT VERIFIABLE" : complianceReport.arithmeticStatus}
                    </Badge>
                  </div>
                </div>

                {/* Status Explanation Banner */}
                <div
                  className={`p-3.5 rounded-md border text-xs space-y-1 ${
                    complianceReport.arithmeticStatus === "MATCH"
                      ? "bg-emerald-50 border-emerald-200 text-emerald-900"
                      : complianceReport.arithmeticStatus === "MISMATCH"
                      ? "bg-red-50 border-red-200 text-red-900"
                      : "bg-amber-50 border-amber-200 text-amber-900"
                  }`}
                >
                  <div className="flex items-center space-x-2 font-bold uppercase tracking-wider text-[10px]">
                    {complianceReport.arithmeticStatus === "MATCH" ? (
                      <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                    ) : complianceReport.arithmeticStatus === "MISMATCH" ? (
                      <AlertTriangle className="h-4 w-4 text-red-600" />
                    ) : (
                      <AlertCircle className="h-4 w-4 text-amber-600" />
                    )}
                    <span>
                      {complianceReport.extractionSummaryStatus === "MISSING_BREAKDOWN" || complianceReport.arithmeticStatus === "NOT_VERIFIABLE"
                        ? "Itemized budget breakdown not found"
                        : complianceReport.extractionSummaryStatus === "PARTIAL_BREAKDOWN"
                        ? "Partial budget breakdown extracted"
                        : complianceReport.arithmeticStatus === "MISMATCH"
                        ? "Budget Arithmetic Mismatch Detected"
                        : "Budget Component Arithmetic Verified"}
                    </span>
                  </div>
                  <p className="font-medium text-slate-700 leading-relaxed pl-6">{complianceReport.explanation}</p>
                </div>

                {/* Extracted Budget Components Table */}
                <div className="space-y-2">
                  <h4 className="text-xs font-semibold text-slate-800 uppercase">Extracted Budget Components</h4>
                  {complianceReport.findings && complianceReport.findings.length > 0 ? (
                    <div className="overflow-x-auto border border-slate-200 rounded-md">
                      <table className="w-full text-xs text-left">
                        <thead className="bg-slate-50 text-slate-500 font-mono text-[10px] uppercase border-b border-slate-200">
                          <tr>
                            <th className="p-2.5">Cost Head</th>
                            <th className="p-2.5 text-right">Extracted Amount</th>
                            <th className="p-2.5">Source Evidence</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-200 bg-white font-mono">
                          {complianceReport.findings.map((f, idx) => (
                            <tr key={idx} className="hover:bg-slate-50/50">
                              <td className="p-2.5 font-bold text-slate-900">{f.costHead}</td>
                              <td className="p-2.5 text-right font-bold text-slate-800">
                                {formatCurrency(f.proposedAmount)}
                                {f.rawAmountString && (
                                  <span className="text-[10px] text-slate-400 block font-normal">{f.rawAmountString}</span>
                                )}
                              </td>
                              <td className="p-2.5">
                                {f.sourcePage ? (
                                  <Badge
                                    variant="outline"
                                    className="text-[10px] font-mono cursor-pointer hover:bg-slate-100"
                                    onClick={() =>
                                      setEvidenceDrawerContent({
                                        title: `Budget Item: ${f.costHead}`,
                                        text: `Cost Head: ${f.costHead}\nProposed Amount: ${formatCurrency(f.proposedAmount)}\nRaw String: ${f.rawAmountString || 'N/A'}\nSource Page: Page ${f.sourcePage}\nNotes: ${f.notes || ''}`,
                                        pages: `Page ${f.sourcePage}`,
                                        evidenceId: `FIN-PROP-${idx + 1}`,
                                      })
                                    }
                                  >
                                    Page {f.sourcePage}
                                  </Badge>
                                ) : (
                                  <span className="text-slate-400 text-[10px]">Document Metadata</span>
                                )}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <div className="p-4 bg-slate-50 rounded border border-slate-200 text-center text-xs text-slate-500 italic">
                      No itemized budget components were reliably extracted from the proposal document.
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="p-4 text-center text-xs text-slate-500">Loading financial compliance report...</div>
            )}
          </CardContent>
        </Card>
      )}

      {/* TAB 4: P0.4 Historical Benchmark Search Integration */}
      {activeTab === "similar" && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm flex items-center space-x-2">
              <Sparkles className="h-4 w-4 text-blue-600" />
              <span>Evidence-Backed Historical Project Benchmarking (P0.4 Engine)</span>
            </CardTitle>
            <CardDescription className="text-xs">
              Surfaces relevant historical CIL/CMPDI R&amp;D projects to assist reviewer with prior art and evidence comparison.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {loading ? (
              <div className="p-8 text-center text-xs text-slate-500">Querying historical knowledge base for proposal concepts...</div>
            ) : similarProjects && similarProjects.length > 0 ? (
              <div className="space-y-4">
                {similarProjects.map((item) => (
                  <Card key={item.projectId} className="border border-slate-200 hover:border-blue-300">
                    <CardContent className="p-4 space-y-2 text-xs">
                      <div className="flex items-start justify-between">
                        <div>
                          <Badge variant="outline" className="font-mono text-[10px] mr-2">
                            {item.projectCode}
                          </Badge>
                          <Badge variant="success" className="text-xs font-bold">
                            {item.similarityPercentage}% Similarity
                          </Badge>
                          <h4 className="font-bold text-slate-900 mt-1">{item.projectTitle}</h4>
                        </div>
                        <span className="font-mono font-bold text-slate-900">{item.approvedCostRaw || formatCurrency(item.approvedCost)}</span>
                      </div>

                      {item.evidence.length > 0 && (
                        <p className="text-slate-700 bg-slate-50 p-2 rounded border border-slate-200 font-mono text-[11px]">
                          Evidence: {item.evidence[0].reason}
                        </p>
                      )}

                      <div className="flex items-center justify-between pt-1 text-[11px] text-slate-500">
                        <span>Source: {item.provenance.source} (Page {item.provenance.sourcePageStart})</span>
                        <Link href={`/projects/${item.projectId}`}>
                          <Button variant="outline" size="sm" className="h-7 text-xs">
                            Inspect Benchmark <ArrowRight className="h-3 w-3 ml-1" />
                          </Button>
                        </Link>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <div className="p-4 text-center text-xs text-slate-500">No historical projects found matching proposal concepts.</div>
            )}
          </CardContent>
        </Card>
      )}

      {/* TAB 5: Scientific Evidence Comparison */}
      {activeTab === "scientific" && (
        <ScientificEvidenceComparisonSection proposalId={proposal.id} />
      )}

      {/* TAB 6: Evaluation Rubric (MoC Guidelines v1.0) */}
      {activeTab === "rubric" && (
        <EvaluationRubricSection proposalId={proposal.id} />
      )}

      {/* Evidence Source Modal Drawer */}
      {evidenceDrawerContent && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[85vh] flex flex-col overflow-hidden border border-slate-200">
            <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
              <div>
                <h3 className="font-bold text-slate-900 text-sm">{evidenceDrawerContent.title}</h3>
                <span className="text-xs font-mono text-slate-500">
                  {evidenceDrawerContent.evidenceId} • {evidenceDrawerContent.pages}
                </span>
              </div>
              <Button
                variant="ghost"
                size="sm"
                className="h-8 text-xs text-slate-500 hover:text-slate-900"
                onClick={() => setEvidenceDrawerContent(null)}
              >
                Close
              </Button>
            </div>
            <div className="p-4 overflow-y-auto max-h-[70vh] text-xs text-slate-700 font-mono whitespace-pre-wrap leading-relaxed bg-slate-50/50">
              {evidenceDrawerContent.text}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
