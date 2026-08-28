"use client";

import React, { useState } from "react";
import { ExternalLink, CheckCircle2, ShieldAlert, FileText, ChevronDown, ChevronUp, Loader2 } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { HistoricalProject } from "@/lib/types";
import { projectService } from "@/lib/api/projects";
import { formatCurrency } from "@/lib/utils";

interface HistoricalProjectDetailViewerProps {
  initialProject: HistoricalProject;
}

export function HistoricalProjectDetailViewer({ initialProject }: HistoricalProjectDetailViewerProps) {
  const [project, setProject] = useState<HistoricalProject>(initialProject);
  const [updating, setUpdating] = useState(false);
  const [showRawText, setShowRawText] = useState(false);

  const handleVerification = async (newStatus: "VERIFIED" | "REJECTED" | "NEEDS_REVIEW") => {
    setUpdating(true);
    try {
      const updated = await projectService.updateVerificationStatus(project.id, newStatus);
      setProject(updated);
    } catch {
      // Handle error
    } finally {
      setUpdating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header Card */}
      <Card className="bg-white border-slate-200">
        <CardContent className="p-6">
          <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
            <div className="space-y-2 max-w-3xl">
              <div className="flex flex-wrap items-center gap-2">
                <Badge variant="outline" className="font-mono text-xs bg-slate-100">
                  {project.projectCode || project.id}
                </Badge>
                <Badge
                  variant={project.sourceType === "OFFICIAL" ? "success" : "secondary"}
                  className="text-xs"
                >
                  {project.sourceType === "OFFICIAL" ? "OFFICIAL DATA (CIL/CMPDI)" : "DEMO / SYNTHETIC DATA"}
                </Badge>
                <Badge
                  variant={
                    project.verificationStatus === "VERIFIED"
                      ? "info"
                      : project.verificationStatus === "REJECTED"
                      ? "danger"
                      : "warning"
                  }
                  className="text-xs"
                >
                  {project.verificationStatus.replace("_", " ")}
                </Badge>
              </div>

              <h1 className="text-lg font-bold text-slate-900 leading-snug">{project.title}</h1>
              <p className="text-xs text-slate-600">
                Implementing Agency / Institution: <span className="font-semibold text-slate-800">{project.institution.name}</span>
              </p>
            </div>

            <div className="flex flex-col items-start lg:items-end space-y-2 flex-shrink-0">
              <span className="text-[10px] font-mono uppercase text-slate-500 block">Total Approved Cost</span>
              <span className="text-xl font-bold font-mono text-slate-900">
                {project.approvedCostRaw ? project.approvedCostRaw : formatCurrency(project.totalCost)}
              </span>

              {/* Reviewer Manual Verification Action Bar */}
              <div className="pt-2 flex items-center space-x-2">
                {project.verificationStatus !== "VERIFIED" && (
                  <Button
                    size="sm"
                    variant="outline"
                    className="h-8 text-xs border-emerald-600 text-emerald-700 hover:bg-emerald-50"
                    disabled={updating}
                    onClick={() => handleVerification("VERIFIED")}
                  >
                    {updating ? <Loader2 className="h-3 w-3 animate-spin mr-1" /> : <CheckCircle2 className="h-3.5 w-3.5 mr-1" />}
                    Mark as Verified
                  </Button>
                )}
                {project.verificationStatus !== "REJECTED" && (
                  <Button
                    size="sm"
                    variant="outline"
                    className="h-8 text-xs border-red-600 text-red-700 hover:bg-red-50"
                    disabled={updating}
                    onClick={() => handleVerification("REJECTED")}
                  >
                    <ShieldAlert className="h-3.5 w-3.5 mr-1" />
                    Mark as Rejected
                  </Button>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Content Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Project Overview */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-sm">Historical Project Parameters &amp; Objectives</CardTitle>
            <CardDescription>Structured details extracted from official catalogue.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 text-xs">
            <div className="p-4 bg-slate-50 rounded-md border border-slate-200 space-y-2">
              <h4 className="font-semibold text-slate-900">Extracted Objectives / Summary</h4>
              <p className="text-slate-700 leading-relaxed whitespace-pre-wrap">{project.summary}</p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="p-3 bg-white border border-slate-200 rounded-md">
                <span className="text-[10px] font-mono text-slate-400 uppercase block">Start Date</span>
                <span className="font-semibold text-slate-800">{project.completionYear ? `01/04/${project.completionYear - 2}` : "Not Specified"}</span>
              </div>
              <div className="p-3 bg-white border border-slate-200 rounded-md">
                <span className="text-[10px] font-mono text-slate-400 uppercase block">Scheduled Completion Date</span>
                <span className="font-semibold text-slate-800">{project.completionYear ? `31/03/${project.completionYear}` : "Not Specified"}</span>
              </div>
            </div>

            <div>
              <h4 className="text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
                Technology Keywords
              </h4>
              <div className="flex flex-wrap gap-1.5">
                {project.technologyStack.map((tech) => (
                  <Badge key={tech} variant="outline" className="bg-white text-xs">
                    {tech}
                  </Badge>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Right Column: Source & Provenance Panel */}
        <Card className="lg:col-span-1">
          <CardHeader className="pb-3 border-b border-slate-200">
            <CardTitle className="text-sm flex items-center space-x-2">
              <FileText className="h-4 w-4 text-blue-600" />
              <span>Source &amp; Provenance Details</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 space-y-3 text-xs">
            <div>
              <span className="text-[10px] font-mono text-slate-400 uppercase block">Source Catalog</span>
              <span className="font-bold text-slate-900">{project.source}</span>
            </div>

            <div>
              <span className="text-[10px] font-mono text-slate-400 uppercase block">Source Document</span>
              <span className="font-mono text-slate-800 break-all">{project.sourceDocumentName || "31_03_2026_RD ongoing projects.pdf"}</span>
            </div>

            <div className="grid grid-cols-2 gap-2 bg-slate-50 p-2.5 rounded border border-slate-200">
              <div>
                <span className="text-[10px] font-mono text-slate-400 uppercase block">Page Range</span>
                <span className="font-bold text-slate-900">
                  {project.sourcePageStart ? `Pp. ${project.sourcePageStart}-${project.sourcePageEnd || project.sourcePageStart}` : "Page 1"}
                </span>
              </div>
              <div>
                <span className="text-[10px] font-mono text-slate-400 uppercase block">Data Integrity</span>
                <Badge variant={project.sourceType === "OFFICIAL" ? "success" : "secondary"} className="text-[9px]">
                  {project.sourceType}
                </Badge>
              </div>
            </div>

            {project.sourceUrl && (
              <div>
                <span className="text-[10px] font-mono text-slate-400 uppercase block mb-1">Official Document URL</span>
                <a
                  href={project.sourceUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline flex items-center text-xs break-all font-mono"
                >
                  <ExternalLink className="h-3 w-3 mr-1 flex-shrink-0" />
                  View Official CMPDI Source PDF
                </a>
              </div>
            )}

            {/* Expandable Raw Record Text */}
            {project.rawRecordText && (
              <div className="pt-2 border-t border-slate-200">
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="w-full text-xs flex items-center justify-between px-0 text-slate-700 hover:bg-transparent"
                  onClick={() => setShowRawText(!showRawText)}
                >
                  <span className="font-semibold">Raw Extracted Source Text</span>
                  {showRawText ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                </Button>
                {showRawText && (
                  <pre className="mt-2 p-3 bg-slate-900 text-slate-100 font-mono text-[11px] rounded-md whitespace-pre-wrap overflow-x-auto max-h-60 leading-relaxed">
                    {project.rawRecordText}
                  </pre>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
