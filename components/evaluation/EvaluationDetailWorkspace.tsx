"use client";

import React, { useState } from "react";
import { CheckCircle2, AlertCircle, Sparkles, Save, Send, RefreshCw, AlertTriangle, Table, Layers, Brain } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { evaluationService, EvaluationDetail } from "@/lib/api/evaluations";
import { AIEvidenceAnalysisTab } from "./AIEvidenceAnalysisTab";
import { ConsensusComparisonTab } from "./ConsensusComparisonTab";
import { DecisionPackTab } from "./DecisionPackTab";

interface EvaluationDetailWorkspaceProps {
  initialEvaluation: EvaluationDetail;
}

export function EvaluationDetailWorkspace({ initialEvaluation }: EvaluationDetailWorkspaceProps) {
  const [evaluation, setEvaluation] = useState<EvaluationDetail>(initialEvaluation);
  const [activeTab, setActiveTab] = useState<"rubric" | "ai_analysis" | "consensus" | "decision_pack">("rubric");

  // Draft Form States
  const [criteriaScores, setCriteriaScores] = useState<Record<string, { score: number; comments: string; justification: string }>>(
    () => {
      const map: Record<string, { score: number; comments: string; justification: string }> = {};
      (initialEvaluation.criteria || []).forEach((c) => {
        map[c.id] = {
          score: c.score ?? 7.5,
          comments: c.comments || "",
          justification: c.justificationNotes || "",
        };
      });
      return map;
    }
  );

  const [reviewerSummary, setReviewerSummary] = useState(initialEvaluation.reviewerSummary || "");
  const [recommendation, setRecommendation] = useState<"FAVORABLE" | "FAVORABLE_WITH_CONDITIONS" | "REQUIRES_REVISION" | "NOT_RECOMMENDED">(
    initialEvaluation.reviewerRecommendation || "FAVORABLE_WITH_CONDITIONS"
  );

  const [saving, setSaving] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleScoreChange = (criterionId: string, scoreVal: number) => {
    setCriteriaScores((prev) => ({
      ...prev,
      [criterionId]: {
        ...prev[criterionId],
        score: Math.min(Math.max(scoreVal, 0), 10),
      },
    }));
  };

  const handleCommentChange = (criterionId: string, text: string) => {
    setCriteriaScores((prev) => ({
      ...prev,
      [criterionId]: {
        ...prev[criterionId],
        comments: text,
      },
    }));
  };

  const handleJustificationChange = (criterionId: string, text: string) => {
    setCriteriaScores((prev) => ({
      ...prev,
      [criterionId]: {
        ...prev[criterionId],
        justification: text,
      },
    }));
  };

  const handleSaveDraft = async () => {
    setSaving(true);
    setErrorMessage(null);
    setSuccessMessage(null);
    try {
      const payloadCriteria = Object.entries(criteriaScores).map(([id, val]) => ({
        id,
        score: val.score,
        comments: val.comments,
        justificationNotes: val.justification,
      }));

      const updated = await evaluationService.updateEvaluationDraft(evaluation.id, {
        reviewerSummary,
        reviewerRecommendation: recommendation,
        criteria: payloadCriteria,
      });
      setEvaluation(updated);
      setSuccessMessage("Evaluation draft saved successfully.");
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : "Failed to save evaluation draft.");
    } finally {
      setSaving(false);
    }
  };

  const handleGenerateSummary = async () => {
    setGenerating(true);
    try {
      const summaryText = await evaluationService.generateDraftSummary(evaluation.id);
      setReviewerSummary(summaryText);
    } catch {
      // Ignore
    } finally {
      setGenerating(false);
    }
  };

  const handleSubmitEvaluation = async () => {
    setSubmitting(true);
    setErrorMessage(null);
    setSuccessMessage(null);
    try {
      // First save draft
      await handleSaveDraft();
      const submitted = await evaluationService.submitEvaluation(evaluation.id);
      setEvaluation(submitted);
      setSuccessMessage("Evaluation submitted successfully. Status updated to SUBMITTED.");
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : "Submission failed.");
    } finally {
      setSubmitting(false);
    }
  };

  const isReadOnly = evaluation.status === "SUBMITTED";

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <Card className="bg-white border-slate-200">
        <CardContent className="p-6">
          <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
            <div className="space-y-2 max-w-3xl">
              <div className="flex flex-wrap items-center gap-2">
                <Badge variant="outline" className="font-mono text-xs bg-slate-100">
                  {evaluation.proposal?.proposalReference || `PR-2026-${evaluation.proposalId.slice(0, 6)}`}
                </Badge>
                <Badge variant="outline" className="text-xs">
                  Rubric {evaluation.rubricVersion}
                </Badge>
                <Badge
                  variant={evaluation.status === "SUBMITTED" ? "success" : "warning"}
                  className="text-xs font-bold"
                >
                  STATUS: {evaluation.status}
                </Badge>
              </div>

              <h1 className="text-lg font-bold text-slate-900 leading-snug">
                {evaluation.proposal?.title || "R&D Proposal Evaluation Workspace"}
              </h1>
              <p className="text-xs text-slate-600">
                Reviewer: <span className="font-semibold text-slate-800">{evaluation.reviewerId}</span> • Submitting Institution: <span className="font-semibold text-slate-800">{evaluation.proposal?.institution?.name || "CMPDI Submitting Institute"}</span>
              </p>
            </div>

            <div className="flex flex-col items-start lg:items-end space-y-2 flex-shrink-0">
              <span className="text-[10px] font-mono uppercase text-slate-500 block">Weighted Overall Score</span>
              <div className="flex items-baseline space-x-1">
                <span className="text-2xl font-bold font-mono text-blue-600">
                  {evaluation.overallScore !== null && evaluation.overallScore !== undefined
                    ? evaluation.overallScore.toFixed(1)
                    : "—"}
                </span>
                <span className="text-xs text-slate-400 font-mono">/ 10.0</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Messages */}
      {errorMessage && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-md flex items-start space-x-2 text-xs text-red-700">
          <AlertCircle className="h-4 w-4 text-red-500 flex-shrink-0 mt-0.5" />
          <div>
            <strong>Error: </strong>
            {errorMessage}
          </div>
        </div>
      )}

      {successMessage && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-md flex items-start space-x-2 text-xs text-emerald-800">
          <CheckCircle2 className="h-4 w-4 text-emerald-600 flex-shrink-0 mt-0.5" />
          <div>
            <strong>Success: </strong>
            {successMessage}
          </div>
        </div>
      )}

      {/* Reviewer Safety Disclaimer Banner */}
      <div className="p-3 bg-amber-50 border border-amber-200 rounded-md flex items-start space-x-2.5 text-xs text-amber-900">
        <AlertCircle className="h-4 w-4 text-amber-600 flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-bold">Human Reviewer Safety Notice:</span> AI-assisted evidence, historical similarity scores, and preliminary scrutiny findings are decision-support inputs. Final technical, novelty, funding, approval, and rejection decisions remain with authorized human reviewers.
        </div>
      </div>

      {/* Tab Switcher */}
      <div className="flex border-b border-slate-200 space-x-4">
        <button
          type="button"
          onClick={() => setActiveTab("rubric")}
          className={`pb-2.5 text-xs font-bold border-b-2 flex items-center space-x-2 transition-colors ${
            activeTab === "rubric"
              ? "border-blue-600 text-blue-600"
              : "border-transparent text-slate-500 hover:text-slate-700"
          }`}
        >
          <Layers className="h-4 w-4" />
          <span>Configurable Rubric &amp; Reviewer Scoring</span>
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("ai_analysis")}
          className={`pb-2.5 text-xs font-bold border-b-2 flex items-center space-x-2 transition-colors ${
            activeTab === "ai_analysis"
              ? "border-blue-600 text-blue-600"
              : "border-transparent text-slate-500 hover:text-slate-700"
          }`}
        >
          <Brain className="h-4 w-4 text-blue-600" />
          <span>AI Evidence Analysis Assistant</span>
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("consensus")}
          className={`pb-2.5 text-xs font-bold border-b-2 flex items-center space-x-2 transition-colors ${
            activeTab === "consensus"
              ? "border-blue-600 text-blue-600"
              : "border-transparent text-slate-500 hover:text-slate-700"
          }`}
        >
          <Layers className="h-4 w-4 text-indigo-600" />
          <span>Multi-Reviewer Consensus</span>
          <Badge variant="secondary" className="text-[9px] px-1.5 py-0 bg-indigo-50 text-indigo-700">
            P1.1
          </Badge>
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("decision_pack")}
          className={`pb-2.5 text-xs font-bold border-b-2 flex items-center space-x-2 transition-colors ${
            activeTab === "decision_pack"
              ? "border-blue-600 text-blue-600"
              : "border-transparent text-slate-500 hover:text-slate-700"
          }`}
        >
          <Sparkles className="h-4 w-4 text-blue-600" />
          <span>Decision Pack &amp; PDF Export</span>
          <Badge variant="secondary" className="text-[9px] px-1.5 py-0 bg-blue-50 text-blue-700">
            P0.9
          </Badge>
        </button>
      </div>

      {activeTab === "ai_analysis" ? (
        <AIEvidenceAnalysisTab
          evaluationId={evaluation.id}
          onAcceptNote={(questionText) => {
            setActiveTab("rubric");
            setReviewerSummary((prev) => (prev ? `${prev}\n\nReviewer Question: ${questionText}` : `Reviewer Question: ${questionText}`));
          }}
        />
      ) : activeTab === "consensus" ? (
        <ConsensusComparisonTab evaluationId={evaluation.id} />
      ) : activeTab === "decision_pack" ? (
        <DecisionPackTab evaluationId={evaluation.id} />
      ) : (
        <>
      <Card>
        <CardHeader className="pb-3 border-b border-slate-200">
          <CardTitle className="text-sm flex items-center space-x-2">
            <Table className="h-4 w-4 text-blue-600" />
            <span>Criterion Evidence Matrix</span>
          </CardTitle>
          <CardDescription className="text-xs">
            Multi-source evidence mapping for proposal criteria scrutiny.
          </CardDescription>
        </CardHeader>
        <CardContent className="p-4 space-y-3">
          <div className="space-y-2">
            {evaluation.evidences.map((ev) => (
              <div key={ev.id} className="p-2.5 bg-slate-50 border border-slate-200 rounded text-xs space-y-1">
                <div className="flex items-center justify-between">
                  <Badge variant="outline" className="text-[9px] font-mono uppercase bg-white">
                    {ev.evidenceType}
                  </Badge>
                  <span className="text-[10px] text-slate-500 font-mono">Source: {ev.sourceReference || ev.sourceType}</span>
                </div>
                <p className="text-slate-800 font-medium">{ev.evidenceText}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Section 2: Configurable Evaluation Rubric Grid */}
      <div className="space-y-4">
        <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
          <Layers className="h-4 w-4 text-blue-600" />
          <span>Configurable Evaluation Rubric Criteria ({evaluation.criteria.length} Criteria)</span>
        </h3>

        <div className="grid grid-cols-1 gap-4">
          {evaluation.criteria.map((c) => {
            const currentData = criteriaScores[c.id] || { score: c.score ?? 7.5, comments: c.comments || "", justification: c.justificationNotes || "" };
            const isLowScore = currentData.score <= 5.0;

            return (
              <Card key={c.id} className={`border ${isLowScore ? "border-amber-300 bg-amber-50/20" : "border-slate-200"}`}>
                <CardContent className="p-5 space-y-4">
                  <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
                    <div className="space-y-1 max-w-xl">
                      <div className="flex items-center space-x-2">
                        <Badge variant="outline" className="font-mono text-[10px]">
                          {c.criterionKey || c.name}
                        </Badge>
                        <Badge variant="secondary" className="text-[10px]">
                          Weight: {(c.weight * 100).toFixed(0)}%
                        </Badge>
                      </div>
                      <h4 className="text-sm font-bold text-slate-900">{c.name}</h4>
                      <p className="text-xs text-slate-600">{c.description}</p>
                    </div>

                    {/* Score Input */}
                    <div className="flex items-center space-x-2 bg-slate-50 p-2.5 rounded-md border border-slate-200 flex-shrink-0">
                      <span className="text-xs font-semibold text-slate-700">Reviewer Score:</span>
                      <Input
                        type="number"
                        min={0}
                        max={10}
                        step={0.5}
                        value={currentData.score}
                        disabled={isReadOnly}
                        onChange={(e) => handleScoreChange(c.id, parseFloat(e.target.value) || 0)}
                        className="w-16 h-8 text-xs font-mono font-bold text-center"
                      />
                      <span className="text-xs text-slate-400 font-mono">/ 10</span>
                    </div>
                  </div>

                  {/* Novelty Safety Disclaimer */}
                  {c.criterionKey === "NOVELTY" && (
                    <div className="p-2.5 bg-blue-50 border border-blue-200 rounded text-[11px] text-blue-900 flex items-start space-x-2">
                      <Sparkles className="h-3.5 w-3.5 text-blue-600 flex-shrink-0 mt-0.5" />
                      <div>
                        <strong>Novelty Safety Note:</strong> P0.4 historical similarity scores indicate prior art evidence. Historical similarity does <strong>not</strong> constitute autonomous duplicate classification. The reviewer assigns the actual novelty score.
                      </div>
                    </div>
                  )}

                  {/* Reviewer Comment Textarea */}
                  <div>
                    <label className="text-xs font-semibold text-slate-700 block mb-1">
                      Reviewer Scrutiny Comment / Observations
                    </label>
                    <Textarea
                      value={currentData.comments}
                      disabled={isReadOnly}
                      onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => handleCommentChange(c.id, e.target.value)}
                      placeholder="Enter technical observations, methodology strengths, or concerns..."
                      rows={2}
                      className="text-xs"
                    />
                  </div>

                  {/* Low Score Justification (Required if score <= 5.0) */}
                  {isLowScore && (
                    <div className="p-3 bg-amber-50 border border-amber-200 rounded-md space-y-1.5">
                      <label className="text-xs font-bold text-amber-900 flex items-center space-x-1.5">
                        <AlertTriangle className="h-3.5 w-3.5 text-amber-600" />
                        <span>Low Score Justification Required (Score &le; 5.0)</span>
                      </label>
                      <Textarea
                        value={currentData.justification}
                        disabled={isReadOnly}
                        onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => handleJustificationChange(c.id, e.target.value)}
                        placeholder="Provide specific technical justification for why this criterion received a low score..."
                        rows={2}
                        className="text-xs bg-white"
                      />
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Section 3: Reviewer Summary & Recommendation */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Reviewer Executive Summary &amp; Recommendation</CardTitle>
          <CardDescription className="text-xs">
            Reviewer-entered assessment summary and final technical recommendation.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4 text-xs">
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="font-semibold text-slate-700">Executive Summary Statement</label>
              {!isReadOnly && (
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="h-6 text-[11px] text-blue-600 hover:text-blue-700 p-0"
                  disabled={generating}
                  onClick={handleGenerateSummary}
                >
                  <RefreshCw className={`h-3 w-3 mr-1 ${generating ? "animate-spin" : ""}`} />
                  Generate Draft Summary Text
                </Button>
              )}
            </div>
            <Textarea
              value={reviewerSummary}
              disabled={isReadOnly}
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setReviewerSummary(e.target.value)}
              placeholder="Synthesize overall technical evaluation, key strengths, and conditions for recommendation..."
              rows={4}
            />
          </div>

          <div>
            <label className="font-semibold text-slate-700 block mb-1">
              Reviewer Final Technical Recommendation *
            </label>
            <Select
              value={recommendation}
              disabled={isReadOnly}
              onChange={(e) => setRecommendation(e.target.value as EvaluationDetail["reviewerRecommendation"])}
              className="text-xs"
            >
              <option value="FAVORABLE">Favorable (Recommended for Funding)</option>
              <option value="FAVORABLE_WITH_CONDITIONS">Favorable with Conditions (Minor Revisions Required)</option>
              <option value="REQUIRES_REVISION">Requires Major Revision &amp; Resubmission</option>
              <option value="NOT_RECOMMENDED">Not Recommended</option>
            </Select>
          </div>

          {/* Action Bar */}
          {!isReadOnly && (
            <div className="pt-3 flex items-center justify-end space-x-3 border-t border-slate-200">
              <Button
                type="button"
                variant="outline"
                size="sm"
                disabled={saving || submitting}
                onClick={handleSaveDraft}
              >
                <Save className="h-4 w-4 mr-1.5" />
                {saving ? "Saving Draft..." : "Save Draft"}
              </Button>
              <Button
                type="button"
                size="sm"
                className="bg-blue-600 hover:bg-blue-700 text-white"
                disabled={saving || submitting}
                onClick={handleSubmitEvaluation}
              >
                <Send className="h-4 w-4 mr-1.5" />
                {submitting ? "Submitting Evaluation..." : "Submit Evaluation"}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
      </>
      )}
    </div>
  );
}
