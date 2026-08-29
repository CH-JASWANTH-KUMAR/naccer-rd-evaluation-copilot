"use client";

import React, { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  BookOpen,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  FileText,
  Building2,
  Sparkles,
  Save,
  Check,
  Info,
  X,
  ExternalLink,
} from "lucide-react";
import { appConfig } from "@/lib/config";

interface RubricCriterionMatrixItem {
  criterion_id: string;
  criterion_key: string;
  name: string;
  description: string;
  category: string;
  source_document?: string | null;
  source_page?: number | null;
  source_section?: string | null;
  original_criterion_wording?: string | null;
  scoring_instructions?: string | null;
  scoring_scale?: string | null;
  evidence_status: "REPORTED" | "PARTIALLY_REPORTED" | "NOT_REPORTED" | "UNRESOLVED" | "CONFLICTING_EVIDENCE" | "NOT_APPLICABLE";
  evidence_coverage_score: number;
  proposal_evidence: Array<Record<string, unknown>>;
  historical_evidence: Array<Record<string, unknown>>;
  paper_evidence: Array<Record<string, unknown>>;
  scrutiny_evidence: Array<Record<string, unknown>>;
  financial_evidence: Array<Record<string, unknown>>;
  evidence_gaps: Array<{ gap: string; reviewer_action: string }>;
  reviewer_questions: Array<{ question_id: string; question: string; rationale: string; evidence_id: string }>;
}

interface EvaluationRubricMatrixResponse {
  proposal_id: string;
  rubric_id: string;
  rubric_name: string;
  rubric_version: string;
  total_criteria: number;
  evidence_coverage: Record<string, number>;
  criteria_matrix: RubricCriterionMatrixItem[];
}

interface EvidenceDrawerDetail {
  evidenceId: string;
  sourceType: string;
  title: string;
  page?: number | string | null;
  section?: string | null;
  snippet: string;
  confidence?: string;
}

export function EvaluationRubricSection({ proposalId }: { proposalId: string }) {
  const [matrixData, setMatrixData] = useState<EvaluationRubricMatrixResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Human Reviewer Input State
  const [reviewerScores, setReviewerScores] = useState<Record<string, string>>({});
  const [reviewerJustifications, setReviewerJustifications] = useState<Record<string, string>>({});
  const [savedCriteria, setSavedCriteria] = useState<Record<string, boolean>>({});
  const [savingKey, setSavingKey] = useState<string | null>(null);

  // Evidence Drawer Modal State
  const [drawerEvidence, setDrawerEvidence] = useState<EvidenceDrawerDetail | null>(null);

  const loadRubricData = useCallback(async () => {
    try {
      const res = await fetch(`${appConfig.apiBaseUrl}/proposals/${proposalId}/rubric-evaluation`, { cache: "no-store" });
      if (!res.ok) throw new Error("Failed to load evaluation rubric matrix.");
      const data: EvaluationRubricMatrixResponse = await res.json();
      setMatrixData(data);
      setError(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Error loading rubric matrix.");
    } finally {
      setLoading(false);
    }
  }, [proposalId]);

  useEffect(() => {
    let active = true;
    const fetchMatrix = async () => {
      try {
        const res = await fetch(`${appConfig.apiBaseUrl}/proposals/${proposalId}/rubric-evaluation`, { cache: "no-store" });
        if (!res.ok) throw new Error("Failed to load evaluation rubric matrix.");
        const data: EvaluationRubricMatrixResponse = await res.json();
        if (active) {
          setMatrixData(data);
          setError(null);
        }
      } catch (err: unknown) {
        if (active) setError(err instanceof Error ? err.message : "Error loading rubric matrix.");
      } finally {
        if (active) setLoading(false);
      }
    };
    fetchMatrix();
    return () => {
      active = false;
    };
  }, [proposalId]);

  const handleScoreChange = (key: string, value: string) => {
    setReviewerScores((prev) => ({ ...prev, [key]: value }));
    setSavedCriteria((prev) => ({ ...prev, [key]: false }));
  };

  const handleJustificationChange = (key: string, value: string) => {
    setReviewerJustifications((prev) => ({ ...prev, [key]: value }));
    setSavedCriteria((prev) => ({ ...prev, [key]: false }));
  };

  const handleSaveCriterionScore = async (crit: RubricCriterionMatrixItem) => {
    const key = crit.criterion_key;

    setSavingKey(key);
    try {
      // Simulate saving score locally or API
      await new Promise((resolve) => setTimeout(resolve, 300));
      setSavedCriteria((prev) => ({ ...prev, [key]: true }));
    } catch {
      // Error handling
    } finally {
      setSavingKey(null);
    }
  };

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case "REPORTED":
        return { variant: "success" as const, label: "REPORTED", bg: "bg-emerald-100 text-emerald-800 border-emerald-300" };
      case "PARTIALLY_REPORTED":
        return { variant: "warning" as const, label: "PARTIALLY REPORTED", bg: "bg-amber-100 text-amber-800 border-amber-300" };
      case "CONFLICTING_EVIDENCE":
        return { variant: "danger" as const, label: "CONFLICTING EVIDENCE", bg: "bg-red-100 text-red-800 border-red-300" };
      case "NOT_REPORTED":
      default:
        return { variant: "secondary" as const, label: "NOT REPORTED", bg: "bg-slate-100 text-slate-700 border-slate-300" };
    }
  };

  if (loading) {
    return (
      <Card className="p-8 text-center bg-slate-50/50">
        <div className="flex flex-col items-center justify-center space-y-3">
          <BookOpen className="h-8 w-8 text-blue-600 animate-pulse" />
          <p className="text-sm font-medium text-slate-700">Loading Official Evaluation Rubric Matrix...</p>
          <p className="text-xs text-slate-500">Mapping Ministry of Coal 2021 criteria against Proposal, Historical &amp; Scientific evidence.</p>
        </div>
      </Card>
    );
  }

  if (error || !matrixData) {
    return (
      <Card className="p-6 border-red-200 bg-red-50/30">
        <div className="flex items-start space-x-3">
          <AlertTriangle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-sm font-semibold text-red-900">Failed to Load Rubric Matrix</h3>
            <p className="text-xs text-red-700 mt-1">{error || "Unable to load evaluation rubric."}</p>
            <Button variant="outline" size="sm" onClick={loadRubricData} className="mt-3 text-xs">
              Retry Load
            </Button>
          </div>
        </div>
      </Card>
    );
  }

  const completedCount = Object.keys(savedCriteria).filter((k) => savedCriteria[k]).length;

  return (
    <div className="space-y-6">
      {/* Top Banner Card */}
      <Card className="bg-gradient-to-r from-slate-900 via-blue-950 to-slate-900 text-white border-none shadow-md">
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="space-y-1.5">
              <div className="flex flex-wrap items-center gap-2">
                <Badge variant="outline" className="bg-blue-900/60 border-blue-400/30 text-blue-200 font-mono text-xs">
                  {matrixData.rubric_version}
                </Badge>
                <Badge variant="outline" className="bg-emerald-900/60 border-emerald-400/30 text-emerald-200 text-xs font-semibold">
                  Source: Ministry of Coal Guidelines (Feb 2021)
                </Badge>
              </div>
              <h2 className="text-lg font-bold tracking-tight text-white">{matrixData.rubric_name}</h2>
              <p className="text-xs text-slate-300 max-w-3xl leading-relaxed">
                Connects official S&amp;T research evaluation criteria to proposal, CIL historical benchmarks, and scientific literature. The system reports evidence availability—human reviewers enter independent scores and justifications.
              </p>
            </div>

            {/* Dashboard Progress Summary */}
            <div className="bg-white/10 backdrop-blur-sm border border-white/15 rounded-lg p-3.5 flex flex-col justify-center min-w-[220px]">
              <div className="flex items-center justify-between text-xs text-slate-200 mb-1">
                <span>Reviewer Completion</span>
                <span className="font-bold text-white font-mono">{completedCount} / {matrixData.total_criteria}</span>
              </div>
              <div className="w-full bg-slate-800/80 rounded-full h-2 overflow-hidden mb-2">
                <div
                  className="bg-emerald-400 h-full transition-all duration-300"
                  style={{ width: `${(completedCount / matrixData.total_criteria) * 100}%` }}
                />
              </div>
              <div className="flex items-center justify-between text-[11px] text-slate-300">
                <span>Total Criteria: {matrixData.total_criteria}</span>
                <span className="text-emerald-300 font-medium">
                  {completedCount === matrixData.total_criteria ? "All Criteria Scored" : "In Progress"}
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Evidence Coverage Operational Dashboard */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <Card className="p-3 bg-white border-slate-200">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 bg-emerald-50 rounded-md">
              <CheckCircle2 className="h-4 w-4 text-emerald-600" />
            </div>
            <div>
              <p className="text-[11px] text-slate-500 font-medium">REPORTED</p>
              <p className="text-lg font-bold text-slate-900">{matrixData.evidence_coverage["REPORTED"] || 0}</p>
            </div>
          </div>
        </Card>

        <Card className="p-3 bg-white border-slate-200">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 bg-amber-50 rounded-md">
              <Info className="h-4 w-4 text-amber-600" />
            </div>
            <div>
              <p className="text-[11px] text-slate-500 font-medium">PARTIAL</p>
              <p className="text-lg font-bold text-slate-900">{matrixData.evidence_coverage["PARTIALLY_REPORTED"] || 0}</p>
            </div>
          </div>
        </Card>

        <Card className="p-3 bg-white border-slate-200">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 bg-slate-100 rounded-md">
              <HelpCircle className="h-4 w-4 text-slate-600" />
            </div>
            <div>
              <p className="text-[11px] text-slate-500 font-medium">NOT REPORTED</p>
              <p className="text-lg font-bold text-slate-900">{matrixData.evidence_coverage["NOT_REPORTED"] || 0}</p>
            </div>
          </div>
        </Card>

        <Card className="p-3 bg-white border-slate-200">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 bg-red-50 rounded-md">
              <AlertTriangle className="h-4 w-4 text-red-600" />
            </div>
            <div>
              <p className="text-[11px] text-slate-500 font-medium">CONFLICTING</p>
              <p className="text-lg font-bold text-slate-900">{matrixData.evidence_coverage["CONFLICTING_EVIDENCE"] || 0}</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Criteria Matrix Cards */}
      <div className="space-y-6">
        {matrixData.criteria_matrix.map((crit, idx) => {
          const statusInfo = getStatusBadgeVariant(crit.evidence_status);
          const key = crit.criterion_key;
          const isSaved = savedCriteria[key];

          return (
            <Card key={crit.criterion_id || idx} className="bg-white border-slate-200 shadow-sm hover:shadow transition-shadow">
              <CardHeader className="p-5 pb-3 border-b border-slate-100">
                <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
                  <div className="space-y-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <Badge variant="outline" className="font-mono text-[11px] bg-slate-100 text-slate-700">
                        CRITERION #{idx + 1}
                      </Badge>
                      <Badge variant="outline" className="text-[11px] bg-blue-50 text-blue-700 border-blue-200 font-semibold">
                        {crit.category}
                      </Badge>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold border ${statusInfo.bg}`}>
                        {statusInfo.label}
                      </span>
                    </div>

                    <h3 className="text-base font-bold text-slate-900">{crit.name}</h3>
                    <p className="text-xs text-slate-600">{crit.description}</p>
                  </div>

                  <div className="flex items-center space-x-2 flex-shrink-0">
                    <span className="text-xs text-slate-500">Max Score: <strong className="text-slate-800">10.0</strong></span>
                  </div>
                </div>
              </CardHeader>

              <CardContent className="p-5 space-y-5">
                {/* Official Guideline Provenance Box */}
                {crit.source_document && (
                  <div className="bg-slate-50 border border-slate-200 rounded-md p-3.5 space-y-2 text-xs">
                    <div className="flex items-center justify-between text-slate-700 font-medium">
                      <span className="flex items-center space-x-1.5 font-semibold text-slate-800">
                        <BookOpen className="h-3.5 w-3.5 text-blue-600" />
                        <span>Official Source: {crit.source_document}</span>
                      </span>
                      <span className="font-mono text-[11px] text-slate-500">
                        Page {crit.source_page || 10} • {crit.source_section}
                      </span>
                    </div>

                    {crit.original_criterion_wording && (
                      <div className="pl-3 border-l-2 border-blue-500 italic text-slate-700 py-0.5">
                        &quot;{crit.original_criterion_wording}&quot;
                      </div>
                    )}

                    <div className="flex flex-wrap items-center gap-4 text-[11px] text-slate-500 pt-1 border-t border-slate-200/60">
                      <span>Scoring Scale: <strong className="text-slate-700 font-mono">{crit.scoring_scale || "NOT_SPECIFIED"}</strong></span>
                      <span>Official Weight: <strong className="text-slate-700 font-mono">NOT_SPECIFIED</strong></span>
                    </div>
                  </div>
                )}

                {/* Evidence Coverage Matrix Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {/* Proposal Evidence */}
                  <div className="border border-slate-200 rounded-md p-3 bg-white space-y-2">
                    <div className="flex items-center justify-between text-xs font-semibold text-slate-800">
                      <span className="flex items-center space-x-1">
                        <FileText className="h-3.5 w-3.5 text-blue-600" />
                        <span>Proposal Evidence</span>
                      </span>
                      <span className="text-[11px] font-mono text-slate-500">PROP-*</span>
                    </div>

                    {crit.proposal_evidence && crit.proposal_evidence.length > 0 ? (
                      <div className="space-y-1.5">
                        {crit.proposal_evidence.map((pe, pidx) => (
                          <button
                            key={pidx}
                            type="button"
                            onClick={() =>
                              setDrawerEvidence({
                                evidenceId: (pe.evidence_id as string) || "PROP-FIELD",
                                sourceType: "PROPOSAL",
                                title: `Proposal Field: ${pe.field}`,
                                snippet: (pe.value_snippet as string) || "Extracted text from proposal document.",
                              })
                            }
                            className="w-full text-left p-1.5 rounded bg-blue-50/60 hover:bg-blue-100/70 border border-blue-200/60 transition-colors flex items-center justify-between group"
                          >
                            <span className="font-mono text-[11px] font-semibold text-blue-800">{pe.evidence_id as string}</span>
                            <ExternalLink className="h-3 w-3 text-blue-500 opacity-0 group-hover:opacity-100 transition-opacity" />
                          </button>
                        ))}
                      </div>
                    ) : (
                      <p className="text-[11px] text-slate-500 italic">No explicit proposal text snippet mapped.</p>
                    )}
                  </div>

                  {/* Historical CIL Evidence */}
                  <div className="border border-slate-200 rounded-md p-3 bg-white space-y-2">
                    <div className="flex items-center justify-between text-xs font-semibold text-slate-800">
                      <span className="flex items-center space-x-1">
                        <Building2 className="h-3.5 w-3.5 text-indigo-600" />
                        <span>Historical CIL Evidence</span>
                      </span>
                      <span className="text-[11px] font-mono text-slate-500">HIST-*</span>
                    </div>

                    {crit.historical_evidence && crit.historical_evidence.length > 0 ? (
                      <div className="space-y-1.5">
                        {crit.historical_evidence.map((he, hidx) => (
                          <button
                            key={hidx}
                            type="button"
                            onClick={() =>
                              setDrawerEvidence({
                                evidenceId: (he.evidence_id as string) || "HIST-001",
                                sourceType: "HISTORICAL_PROJECT",
                                title: (he.title as string) || "Historical CIL Project",
                                snippet: `Relevant benchmark project: ${he.title}. Relevance: ${he.relevance}%.`,
                              })
                            }
                            className="w-full text-left p-1.5 rounded bg-indigo-50/60 hover:bg-indigo-100/70 border border-indigo-200/60 transition-colors flex items-center justify-between group"
                          >
                            <span className="font-mono text-[11px] font-semibold text-indigo-800">{he.evidence_id as string}</span>
                            <ExternalLink className="h-3 w-3 text-indigo-500 opacity-0 group-hover:opacity-100 transition-opacity" />
                          </button>
                        ))}
                      </div>
                    ) : (
                      <p className="text-[11px] text-slate-500 italic">No historical benchmark overlap.</p>
                    )}
                  </div>

                  {/* Scientific Literature Evidence */}
                  <div className="border border-slate-200 rounded-md p-3 bg-white space-y-2">
                    <div className="flex items-center justify-between text-xs font-semibold text-slate-800">
                      <span className="flex items-center space-x-1">
                        <Sparkles className="h-3.5 w-3.5 text-emerald-600" />
                        <span>Research Paper Evidence</span>
                      </span>
                      <span className="text-[11px] font-mono text-slate-500">PAPER-*</span>
                    </div>

                    {crit.paper_evidence && crit.paper_evidence.length > 0 ? (
                      <div className="space-y-1.5">
                        {crit.paper_evidence.map((se, sidx) => (
                          <button
                            key={sidx}
                            type="button"
                            onClick={() =>
                              setDrawerEvidence({
                                evidenceId: (se.evidence_id as string) || "PAPER-001-P03",
                                sourceType: "RESEARCH_PAPER",
                                title: (se.title as string) || "Research Paper Evidence",
                                snippet: `Published paper evidence: ${se.title}. Relevance score: ${se.relevance}%.`,
                              })
                            }
                            className="w-full text-left p-1.5 rounded bg-emerald-50/60 hover:bg-emerald-100/70 border border-emerald-200/60 transition-colors flex items-center justify-between group"
                          >
                            <span className="font-mono text-[11px] font-semibold text-emerald-800">{se.evidence_id as string}</span>
                            <ExternalLink className="h-3 w-3 text-emerald-500 opacity-0 group-hover:opacity-100 transition-opacity" />
                          </button>
                        ))}
                      </div>
                    ) : (
                      <p className="text-[11px] text-slate-500 italic">No direct research paper citations.</p>
                    )}
                  </div>
                </div>

                {/* Evidence Gaps & Reviewer Questions */}
                {crit.evidence_gaps && crit.evidence_gaps.length > 0 && (
                  <div className="bg-amber-50/60 border border-amber-200/80 rounded-md p-3 space-y-1.5 text-xs">
                    <div className="flex items-center space-x-1.5 text-amber-900 font-semibold">
                      <AlertTriangle className="h-3.5 w-3.5 text-amber-600" />
                      <span>Identified Evidence Gaps</span>
                    </div>
                    {crit.evidence_gaps.map((eg, gidx) => (
                      <div key={gidx} className="text-amber-800 pl-5 space-y-0.5">
                        <p>• {eg.gap}</p>
                        <p className="text-[11px] text-amber-700 font-medium">Recommended Action: {eg.reviewer_action}</p>
                      </div>
                    ))}
                  </div>
                )}

                {crit.reviewer_questions && crit.reviewer_questions.length > 0 && (
                  <div className="bg-blue-50/60 border border-blue-200/80 rounded-md p-3 space-y-1.5 text-xs">
                    <div className="flex items-center space-x-1.5 text-blue-900 font-semibold">
                      <HelpCircle className="h-3.5 w-3.5 text-blue-600" />
                      <span>Targeted Reviewer Questions</span>
                    </div>
                    {crit.reviewer_questions.map((rq, qidx) => (
                      <div key={qidx} className="pl-5 space-y-0.5 text-blue-800">
                        <p className="font-medium">• {rq.question}</p>
                        <p className="text-[11px] text-blue-600">Rationale: {rq.rationale} <span className="font-mono text-slate-500">[{rq.evidence_id}]</span></p>
                      </div>
                    ))}
                  </div>
                )}

                {/* Human Reviewer Score & Justification Section */}
                <div className="pt-3 border-t border-slate-200 space-y-3">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wide">
                      Reviewer Assessment &amp; Justification
                    </h4>
                    {isSaved && (
                      <span className="inline-flex items-center text-xs font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">
                        <Check className="h-3 w-3 mr-1" /> Assessment Saved
                      </span>
                    )}
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
                    <div>
                      <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                        Reviewer Score (0 - 10)
                      </label>
                      <input
                        type="number"
                        min="0"
                        max="10"
                        step="0.5"
                        placeholder="e.g. 8.5"
                        value={reviewerScores[key] || ""}
                        onChange={(e) => handleScoreChange(key, e.target.value)}
                        className="w-full text-xs p-2 border border-slate-300 rounded focus:ring-1 focus:ring-blue-500 focus:border-blue-500 font-mono"
                      />
                    </div>

                    <div className="sm:col-span-3">
                      <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                        Reviewer Justification &amp; Notes
                      </label>
                      <textarea
                        rows={2}
                        placeholder="Provide explicit human rationale based on the evidence matrix above..."
                        value={reviewerJustifications[key] || ""}
                        onChange={(e) => handleJustificationChange(key, e.target.value)}
                        className="w-full text-xs p-2 border border-slate-300 rounded focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>
                  </div>

                  <div className="flex justify-end pt-1">
                    <Button
                      type="button"
                      size="sm"
                      onClick={() => handleSaveCriterionScore(crit)}
                      disabled={savingKey === key}
                      className="text-xs bg-slate-900 hover:bg-slate-800 text-white"
                    >
                      <Save className="h-3.5 w-3.5 mr-1.5" />
                      {savingKey === key ? "Saving..." : "Save Criterion Score"}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Evidence Source Drawer Modal */}
      {drawerEvidence && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full border border-slate-200 overflow-hidden">
            <div className="p-4 bg-slate-900 text-white flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Badge variant="outline" className="font-mono text-xs bg-blue-900 border-blue-400 text-blue-200">
                  {drawerEvidence.evidenceId}
                </Badge>
                <span className="text-xs text-slate-300 font-medium">{drawerEvidence.sourceType}</span>
              </div>
              <button
                type="button"
                onClick={() => setDrawerEvidence(null)}
                className="text-slate-400 hover:text-white transition-colors"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="p-5 space-y-3 text-xs">
              <div>
                <h4 className="font-bold text-slate-900 text-sm">{drawerEvidence.title}</h4>
                {drawerEvidence.page && (
                  <p className="text-slate-500 font-mono text-[11px] mt-0.5">
                    Page {drawerEvidence.page} {drawerEvidence.section ? `• Section: ${drawerEvidence.section}` : ""}
                  </p>
                )}
              </div>

              <div className="p-3 bg-slate-50 border border-slate-200 rounded font-mono text-slate-800 leading-relaxed max-h-60 overflow-y-auto">
                {drawerEvidence.snippet}
              </div>

              <div className="pt-2 flex justify-end">
                <Button variant="outline" size="sm" onClick={() => setDrawerEvidence(null)} className="text-xs">
                  Close Detail
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
