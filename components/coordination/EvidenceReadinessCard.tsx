"use client";

import React, { useEffect, useState } from "react";
import {
  AlertCircle,
  Clock,
  ChevronDown,
  ChevronRight,
  Info,
  Sparkles,
  Award,
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { coordinationService, EvidenceReadinessResponse } from "@/lib/api/coordination";

interface EvidenceReadinessCardProps {
  proposalId: string;
}

export function EvidenceReadinessCard({ proposalId }: EvidenceReadinessCardProps) {
  const [data, setData] = useState<EvidenceReadinessResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  useEffect(() => {
    async function fetchScore() {
      try {
        setLoading(true);
        setError(null);
        const res = await coordinationService.getEvidenceReadiness(proposalId);
        setData(res);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Failed to load evidence readiness score.");
      } finally {
        setLoading(false);
      }
    }
    fetchScore();
  }, [proposalId]);

  if (loading) {
    return (
      <div className="p-6 text-center text-xs text-slate-500 flex items-center justify-center space-x-2 border rounded-lg bg-slate-50">
        <Clock className="h-4 w-4 animate-spin text-blue-600" />
        <span>Calculating Evidence Readiness Score from system verification checks...</span>
      </div>
    );
  }

  if (error || !data) {
    return null;
  }

  const scoreColorClass =
    data.totalScore >= 80
      ? "text-emerald-700 bg-emerald-50 border-emerald-300"
      : data.totalScore >= 60
      ? "text-blue-700 bg-blue-50 border-blue-300"
      : data.totalScore >= 40
      ? "text-amber-700 bg-amber-50 border-amber-300"
      : "text-red-700 bg-red-50 border-red-300";

  return (
    <Card className="border-slate-200 shadow-sm">
      <CardHeader className="py-3.5 bg-slate-50/80 border-b border-slate-200 flex flex-row items-center justify-between">
        <div className="flex items-center space-x-2">
          <Sparkles className="h-4 w-4 text-blue-600" />
          <CardTitle className="text-sm font-bold text-slate-900 uppercase">
            Evidence Readiness Summary
          </CardTitle>
          {data.isDemo && (
            <Badge variant="outline" className="bg-amber-100 text-amber-900 border-amber-300 text-[9px] font-mono uppercase font-bold px-1.5">
              DEMO DATA
            </Badge>
          )}
        </div>

        <Badge variant="outline" className="font-mono text-xs font-bold px-2 py-0.5">
          Readiness Metric: 0–100
        </Badge>
      </CardHeader>

      <CardContent className="p-4 space-y-4 text-xs font-mono">
        {/* SCORE BANNER */}
        <div className={`p-4 rounded-lg border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 ${scoreColorClass}`}>
          <div>
            <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider block">
              EVIDENCE READINESS SCORE
            </span>
            <div className="flex items-baseline space-x-2">
              <span className="text-3xl font-bold font-mono tracking-tight">{data.totalScore}</span>
              <span className="text-sm text-slate-500 font-bold">/ 100</span>
            </div>
            <span className="text-xs font-sans font-semibold mt-0.5 block">{data.interpretationLabel}</span>
          </div>

          <div className="text-[11px] font-sans text-slate-600 max-w-sm p-2.5 bg-white/80 rounded border border-slate-200/60 space-y-1">
            <div className="flex items-center space-x-1 text-slate-900 font-bold text-[10px] uppercase">
              <Info className="h-3.5 w-3.5 text-blue-600" />
              <span>Score Disclaimer</span>
            </div>
            <p className="text-[10px] leading-tight text-slate-700 italic">{data.disclaimer}</p>
          </div>
        </div>

        {/* 6 COMPONENTS BREAKDOWN GRID */}
        <div className="space-y-2">
          <h4 className="font-bold text-slate-800 text-[11px] uppercase tracking-wider flex items-center justify-between border-b pb-1">
            <span>Deterministic Score Components (100 Points Total)</span>
            <span className="text-[10px] text-slate-400 font-normal">Click component to inspect evidence checks</span>
          </h4>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {data.components.map((comp, idx) => (
              <div
                key={idx}
                onClick={() => setExpandedIndex(expandedIndex === idx ? null : idx)}
                className="p-2.5 bg-slate-50 border rounded hover:border-blue-300 transition-all cursor-pointer space-y-1"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-1.5 font-bold text-slate-900 text-[11px]">
                    {expandedIndex === idx ? (
                      <ChevronDown className="h-3 w-3 text-blue-600 flex-shrink-0" />
                    ) : (
                      <ChevronRight className="h-3 w-3 text-slate-400 flex-shrink-0" />
                    )}
                    <span>{comp.name}</span>
                  </div>
                  <span className="font-bold font-mono text-slate-900 text-xs">
                    {comp.score.toFixed(0)} / {comp.maxScore.toFixed(0)}
                  </span>
                </div>

                <p className="text-[10px] font-sans text-slate-600 pl-4">{comp.explanation}</p>

                {expandedIndex === idx && comp.contributingChecks && comp.contributingChecks.length > 0 && (
                  <div className="mt-2 pl-4 pt-2 border-t border-slate-200 space-y-1">
                    <span className="text-[9px] font-bold uppercase text-slate-500 block">
                      Contributing Evidence / System Checks:
                    </span>
                    <ul className="list-disc pl-3 text-[10px] font-sans text-slate-800 space-y-0.5">
                      {comp.contributingChecks.map((chk, cIdx) => (
                        <li key={cIdx}>{chk}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* STRENGTHS & ATTENTION REQUIRED SUMMARY */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2 border-t">
          {/* STRENGTHS */}
          <div className="space-y-2">
            <h4 className="font-bold text-emerald-900 text-[11px] uppercase tracking-wider flex items-center space-x-1.5">
              <Award className="h-3.5 w-3.5 text-emerald-600" />
              <span>Evidence Strengths</span>
            </h4>
            <div className="space-y-1.5 font-sans text-xs">
              {data.strengths && data.strengths.length > 0 ? (
                data.strengths.map((item, idx) => (
                  <div key={idx} className="p-2 bg-emerald-50/50 border border-emerald-200/80 rounded space-y-0.5">
                    <div className="flex items-center justify-between font-bold text-emerald-950 text-[11px]">
                      <span>{item.title}</span>
                      <Badge variant="outline" className="text-[9px] font-mono">
                        {item.evidenceId}
                      </Badge>
                    </div>
                    <p className="text-[10px] text-slate-600">{item.description}</p>
                  </div>
                ))
              ) : (
                <p className="text-[10px] text-slate-500 italic">No specific strengths recorded.</p>
              )}
            </div>
          </div>

          {/* ATTENTION REQUIRED */}
          <div className="space-y-2">
            <h4 className="font-bold text-amber-900 text-[11px] uppercase tracking-wider flex items-center space-x-1.5">
              <AlertCircle className="h-3.5 w-3.5 text-amber-600" />
              <span>Attention Required / Evidence Gaps</span>
            </h4>
            <div className="space-y-1.5 font-sans text-xs">
              {data.attentionRequired && data.attentionRequired.length > 0 ? (
                data.attentionRequired.map((item, idx) => (
                  <div key={idx} className="p-2 bg-amber-50/50 border border-amber-200/80 rounded space-y-0.5">
                    <div className="flex items-center justify-between font-bold text-amber-950 text-[11px]">
                      <span>{item.title}</span>
                      <Badge variant="outline" className="text-[9px] font-mono">
                        {item.evidenceId}
                      </Badge>
                    </div>
                    <p className="text-[10px] text-slate-600">{item.description}</p>
                  </div>
                ))
              ) : (
                <p className="text-[10px] text-slate-500 italic">No attention items recorded.</p>
              )}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
