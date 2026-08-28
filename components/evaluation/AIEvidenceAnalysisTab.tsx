"use client";

import React, { useState } from "react";
import { Sparkles, RefreshCw, AlertTriangle, CheckCircle2, HelpCircle, FileText, ShieldAlert, ArrowUpRight } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { evaluationService, AIAnalysisRead } from "@/lib/api/evaluations";

interface AIEvidenceAnalysisTabProps {
  evaluationId: string;
  onAcceptNote?: (questionText: string) => void;
}

export function AIEvidenceAnalysisTab({ evaluationId, onAcceptNote }: AIEvidenceAnalysisTabProps) {
  const [analysis, setAnalysis] = useState<AIAnalysisRead | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchOrGenerate = async (forceRefresh = false) => {
    setLoading(true);
    setError(null);
    try {
      const data = forceRefresh
        ? await evaluationService.refreshAIAnalysis(evaluationId)
        : await evaluationService.generateAIAnalysis(evaluationId);
      setAnalysis(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load AI evidence analysis.");
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    let isMounted = true;
    evaluationService
      .generateAIAnalysis(evaluationId)
      .then((data) => {
        if (isMounted) {
          setAnalysis(data);
        }
      })
      .catch((err: unknown) => {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "Failed to load AI evidence analysis.");
        }
      });

    return () => {
      isMounted = false;
    };
  }, [evaluationId]);

  if (loading) {
    return (
      <Card>
        <CardContent className="p-8 flex flex-col items-center justify-center space-y-3 text-xs text-slate-500">
          <RefreshCw className="h-6 w-6 animate-spin text-blue-600" />
          <span>Generating evidence-grounded AI analysis snapshot...</span>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="border-red-200 bg-red-50/20">
        <CardContent className="p-6 space-y-3">
          <div className="flex items-center space-x-2 text-red-700">
            <AlertTriangle className="h-5 w-5 flex-shrink-0" />
            <span className="font-bold text-sm">AI Analysis Unavailable</span>
          </div>
          <p className="text-xs text-slate-600">
            {error}. You can continue manual evaluation using proposal text, historical benchmark search, and financial checks.
          </p>
          <Button size="sm" variant="outline" onClick={() => fetchOrGenerate(true)}>
            Retry AI Analysis
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (!analysis) return null;

  const { analysisResult } = analysis;

  return (
    <div className="space-y-6">
      {/* Metadata Bar & Refresh */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 bg-white p-4 rounded-lg border border-slate-200">
        <div className="flex flex-wrap items-center gap-2">
          <Badge
            variant={analysis.provider.includes("llm") ? "success" : "secondary"}
            className="font-mono text-[10px]"
          >
            {analysis.provider.includes("llm") ? "Configured LLM Provider" : "Deterministic Fallback RAG Engine"}
          </Badge>
          <Badge variant="outline" className="font-mono text-[10px] bg-slate-50">
            Model: {analysis.model}
          </Badge>
          <Badge variant="outline" className="font-mono text-[10px] bg-slate-50">
            Prompt: {analysis.promptVersion}
          </Badge>
          <Badge variant="outline" className="font-mono text-[10px] bg-slate-50">
            Hash: {analysis.inputHash.slice(0, 8)}...
          </Badge>
        </div>

        <Button
          size="sm"
          variant="outline"
          onClick={() => fetchOrGenerate(true)}
          className="h-8 text-xs font-medium"
        >
          <RefreshCw className="h-3.5 w-3.5 mr-1.5" />
          Refresh AI Analysis
        </Button>
      </div>

      {/* Safety Disclaimer */}
      <div className="p-3 bg-blue-50 border border-blue-200 rounded-md text-xs text-blue-900 flex items-start space-x-2.5">
        <Sparkles className="h-4 w-4 text-blue-600 flex-shrink-0 mt-0.5" />
        <div>
          <strong>AI Assistance Safety Notice:</strong> {analysisResult.disclaimer}
        </div>
      </div>

      {/* Executive Observation */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-bold text-slate-900 flex items-center space-x-2">
            <FileText className="h-4 w-4 text-blue-600" />
            <span>Executive Evidence Observation</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="text-xs text-slate-700 leading-relaxed font-medium">
          {analysisResult.overallObservation}
        </CardContent>
      </Card>

      {/* Strengths & Concerns Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Strengths */}
        <Card className="border-emerald-200 bg-emerald-50/10">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-bold text-emerald-900 flex items-center space-x-1.5">
              <CheckCircle2 className="h-4 w-4 text-emerald-600" />
              <span>Grounded Proposal Strengths ({analysisResult.strengths.length})</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-xs">
            {analysisResult.strengths.map((s, idx) => (
              <div key={idx} className="p-3 bg-white border border-emerald-100 rounded space-y-1">
                <span className="font-bold text-slate-900 block">{s.title}</span>
                <p className="text-slate-600">{s.description}</p>
                {s.supportingEvidence.map((ev, eidx) => (
                  <span key={eidx} className="text-[10px] text-emerald-700 font-mono block">
                    Source: {ev.sourceReference}
                  </span>
                ))}
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Concerns */}
        <Card className="border-amber-200 bg-amber-50/10">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-bold text-amber-900 flex items-center space-x-1.5">
              <AlertTriangle className="h-4 w-4 text-amber-600" />
              <span>Identified Concerns &amp; Risks ({analysisResult.concerns.length})</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-xs">
            {analysisResult.concerns.map((c, idx) => (
              <div key={idx} className="p-3 bg-white border border-amber-100 rounded space-y-1">
                <span className="font-bold text-slate-900 block">{c.title}</span>
                <p className="text-slate-600">{c.description}</p>
                {c.supportingEvidence.map((ev, eidx) => (
                  <span key={eidx} className="text-[10px] text-amber-700 font-mono block">
                    Source: {ev.sourceReference}
                  </span>
                ))}
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Criterion-Specific AI Observations */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Criterion-Specific Evidence Analysis</CardTitle>
          <CardDescription className="text-xs">
            Evidence citations and preliminary observations per evaluation criterion.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {analysisResult.criterionAnalysis.map((ca) => (
            <div key={ca.criterionKey} className="p-4 bg-slate-50 border border-slate-200 rounded-lg space-y-2 text-xs">
              <div className="flex items-center justify-between">
                <Badge variant="outline" className="font-mono text-[10px] bg-white">
                  {ca.criterionKey}
                </Badge>
                <span className="font-bold text-slate-900">{ca.criterionName}</span>
              </div>

              <p className="text-slate-700 font-medium">{ca.observation}</p>

              {/* Supporting Evidence Citations */}
              {ca.supportingEvidence.length > 0 && (
                <div className="space-y-1 pt-1">
                  <span className="text-[10px] font-bold text-slate-500 uppercase block">Supporting Citations:</span>
                  {ca.supportingEvidence.map((ev, eidx) => (
                    <div key={eidx} className="p-2 bg-white border border-slate-200 rounded text-[11px] text-slate-600">
                      <span className="font-mono text-[10px] font-semibold text-blue-600 block">
                        [{ev.sourceType}] {ev.sourceReference} {ev.pageStart ? `(Pages ${ev.pageStart}-${ev.pageEnd})` : ""}
                      </span>
                      <span>&quot;{ev.evidenceText}&quot;</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Evidence Gaps & Reviewer Questions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Evidence Gaps */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-bold text-slate-900 flex items-center space-x-1.5">
              <ShieldAlert className="h-4 w-4 text-amber-600" />
              <span>Evidence Gap Analysis ({analysisResult.evidenceGaps.length})</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-xs">
            {analysisResult.evidenceGaps.map((eg, idx) => (
              <div key={idx} className="p-3 bg-amber-50/50 border border-amber-200 rounded space-y-1">
                <Badge variant="outline" className="text-[9px] font-mono bg-white">
                  {eg.criterionKey}
                </Badge>
                <p className="font-semibold text-amber-900">{eg.gapDescription}</p>
                <p className="text-slate-600 text-[11px] font-medium">Impact: {eg.impact}</p>
                <span className="text-blue-700 font-semibold block text-[11px]">
                  Action: {eg.reviewerAction}
                </span>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Reviewer Questions */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-bold text-slate-900 flex items-center space-x-1.5">
              <HelpCircle className="h-4 w-4 text-blue-600" />
              <span>Targeted Reviewer Scrutiny Questions ({analysisResult.reviewerQuestions.length})</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-xs">
            {analysisResult.reviewerQuestions.map((rq, idx) => (
              <div key={idx} className="p-3 bg-white border border-slate-200 rounded space-y-1.5">
                <div className="flex items-center justify-between">
                  <Badge variant="outline" className="text-[9px] font-mono">
                    {rq.criterionKey}
                  </Badge>
                  {onAcceptNote && (
                    <Button
                      size="sm"
                      variant="ghost"
                      className="h-6 text-[10px] text-blue-600 hover:text-blue-700 p-0"
                      onClick={() => onAcceptNote(rq.question)}
                    >
                      Accept as Note <ArrowUpRight className="h-3 w-3 ml-1" />
                    </Button>
                  )}
                </div>
                <p className="font-bold text-slate-900">{rq.question}</p>
                <p className="text-slate-500 text-[11px]">{rq.rationale}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Non-Financial Internal Contradictions */}
      {analysisResult.contradictions.length > 0 && (
        <Card className="border-amber-300 bg-amber-50/20">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-bold text-amber-900 flex items-center space-x-1.5">
              <AlertTriangle className="h-4 w-4 text-amber-600" />
              <span>Internal Non-Financial Consistency Warnings</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-xs">
            {analysisResult.contradictions.map((cd, idx) => (
              <div key={idx} className="p-2.5 bg-white border border-amber-200 rounded text-slate-800">
                <span className="font-bold text-amber-900 block font-mono text-[11px]">
                  Inconsistency: {cd.fieldA} vs {cd.fieldB}
                </span>
                <p className="text-slate-700 mt-0.5">{cd.observation}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
