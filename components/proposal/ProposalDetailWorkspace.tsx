"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { FileText, CheckCircle2, AlertTriangle, AlertCircle, Sparkles, RefreshCw, ArrowRight, DollarSign } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Proposal } from "@/lib/types";
import { proposalService, ProposalCompletenessReport, FinancialComplianceReport, ProposalSourceProvenance } from "@/lib/api/proposals";
import { SimilarityResultItem } from "@/lib/api/projects";
import { formatCurrency } from "@/lib/utils";

interface ProposalDetailWorkspaceProps {
  initialProposal: Proposal;
}

export function ProposalDetailWorkspace({ initialProposal }: ProposalDetailWorkspaceProps) {
  const [proposal, setProposal] = useState<Proposal>(initialProposal);
  const [activeTab, setActiveTab] = useState<"structured" | "completeness" | "financial" | "similar">("structured");

  const [completenessReport, setCompletenessReport] = useState<ProposalCompletenessReport | null>(null);
  const [complianceReport, setComplianceReport] = useState<FinancialComplianceReport | null>(null);
  const [sourceProvenance, setSourceProvenance] = useState<ProposalSourceProvenance | null>(null);
  const [similarProjects, setSimilarProjects] = useState<SimilarityResultItem[] | null>(null);

  const [loading, setLoading] = useState(false);
  const [reprocessing, setReprocessing] = useState(false);

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
      </div>

      {/* TAB 1: Structured Proposal & Source Provenance */}
      {activeTab === "structured" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle className="text-sm">Structured Proposal Fields &amp; Sections</CardTitle>
              <CardDescription className="text-xs">
                Parsed section fields extracted from PDF proposal document.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4 text-xs">
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
                  Technology &amp; Infrastructure
                </span>
                <p className="text-slate-700 bg-slate-50 p-3 rounded border border-slate-200 whitespace-pre-wrap">
                  {proposal.technology || "Section text not extracted."}
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

              <div>
                <span className="font-mono text-[10px] uppercase font-semibold text-slate-400 block mb-1">
                  Expected Outcomes &amp; Deliverables
                </span>
                <p className="text-slate-700 bg-slate-50 p-3 rounded border border-slate-200 whitespace-pre-wrap">
                  {proposal.expectedOutcomes || "Section text not extracted."}
                </p>
              </div>
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
            <CardTitle className="text-sm">Rule-Based Financial Arithmetic &amp; Compliance Report</CardTitle>
            <CardDescription className="text-xs">
              Deterministic verification of proposed budget totals and component head arithmetic.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {complianceReport ? (
              <div className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div className="p-3 bg-slate-50 rounded border border-slate-200">
                    <span className="text-[10px] font-mono text-slate-400 uppercase block">Declared Total Budget</span>
                    <span className="text-sm font-bold font-mono text-slate-900">{formatCurrency(complianceReport.declaredTotal)}</span>
                  </div>
                  <div className="p-3 bg-slate-50 rounded border border-slate-200">
                    <span className="text-[10px] font-mono text-slate-400 uppercase block">Calculated Component Sum</span>
                    <span className="text-sm font-bold font-mono text-slate-900">{formatCurrency(complianceReport.calculatedTotal)}</span>
                  </div>
                  <div className="p-3 bg-slate-50 rounded border border-slate-200">
                    <span className="text-[10px] font-mono text-slate-400 uppercase block">Arithmetic Mismatch</span>
                    <Badge variant={complianceReport.arithmeticMismatch ? "danger" : "success"} className="text-xs font-bold mt-1">
                      {complianceReport.arithmeticMismatch ? `MISMATCH (Diff: ${formatCurrency(complianceReport.differenceAmount)})` : "MATCH"}
                    </Badge>
                  </div>
                </div>

                <div className="space-y-2">
                  <h4 className="text-xs font-semibold text-slate-800 uppercase">Cost Head Findings &amp; Itemized Breakdown</h4>
                  {complianceReport.findings.map((f, idx) => (
                    <div key={idx} className="p-3 bg-white border border-slate-200 rounded text-xs space-y-1">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <span className="font-bold text-slate-900">{f.costHead}</span>
                          {f.sourcePage && (
                            <Badge variant="outline" className="font-mono text-[10px]">
                              Page {f.sourcePage}
                            </Badge>
                          )}
                        </div>
                        <div className="text-right">
                          <span className="font-mono font-bold text-slate-800 block">{formatCurrency(f.proposedAmount)}</span>
                          {f.rawAmountString && (
                            <span className="text-[10px] font-mono text-slate-500 block">{f.rawAmountString}</span>
                          )}
                        </div>
                      </div>
                      {f.notes && <p className="text-slate-600 text-[11px]">{f.notes}</p>}
                    </div>
                  ))}
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
    </div>
  );
}
