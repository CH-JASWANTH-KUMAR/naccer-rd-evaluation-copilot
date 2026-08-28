"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Search, Sparkles, AlertCircle, FileText, ExternalLink, ArrowRight, Loader2 } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { projectService, SimilarityResultItem } from "@/lib/api/projects";
import { RESEARCH_DOMAINS } from "@/lib/constants";
import { formatCurrency } from "@/lib/utils";

export function SimilaritySearchWorkspace() {
  const [title, setTitle] = useState("");
  const [objectives, setObjectives] = useState("");
  const [technology, setTechnology] = useState("");
  const [domain, setDomain] = useState("");

  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<SimilarityResultItem[] | null>(null);
  const [disclaimer, setDisclaimer] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title && !objectives && !technology && !domain) return;

    setLoading(true);
    try {
      const res = await projectService.searchSimilarProjects({
        title,
        objectives,
        technology,
        domain,
        topK: 10,
      });
      setResults(res.results);
      setDisclaimer(res.disclaimer);
    } catch {
      // Handle error
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Search Input Card */}
      <Card className="border-blue-200 bg-gradient-to-r from-blue-50/40 via-white to-slate-50">
        <CardHeader className="pb-3">
          <CardTitle className="text-base text-slate-900 flex items-center space-x-2">
            <Sparkles className="h-5 w-5 text-blue-600" />
            <span>Find Similar Historical R&amp;D Benchmark Projects</span>
          </CardTitle>
          <CardDescription className="text-xs">
            Query the CIL/CMPDI historical knowledge base to identify evidence of prior art, related objectives, or technical overlap.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSearch} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-semibold text-slate-700 block mb-1">
                  Proposal Title / Concept
                </label>
                <Input
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Real-Time Methane Detection System in Underground Mines"
                  className="text-xs"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-700 block mb-1">
                  Research Domain
                </label>
                <Select value={domain} onChange={(e) => setDomain(e.target.value)} className="text-xs">
                  <option value="">Select Domain...</option>
                  {RESEARCH_DOMAINS.map((d) => (
                    <option key={d} value={d}>
                      {d}
                    </option>
                  ))}
                </Select>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-semibold text-slate-700 block mb-1">
                  Technical Objectives / Problem Statement
                </label>
                <Textarea
                  value={objectives}
                  onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setObjectives(e.target.value)}
                  placeholder="Describe technical objectives, sensor network deployment, or experimental goals..."
                  rows={3}
                  className="text-xs"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-700 block mb-1">
                  Proposed Technology / Tools
                </label>
                <Textarea
                  value={technology}
                  onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setTechnology(e.target.value)}
                  placeholder="e.g. ZigBee Mesh, Intrinsic Safety Enclosures, Edge Machine Learning"
                  rows={3}
                  className="text-xs"
                />
              </div>
            </div>

            <div className="flex items-center justify-end space-x-2 pt-2">
              <Button type="submit" disabled={loading} size="sm" className="bg-blue-600 hover:bg-blue-700 text-white">
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin mr-1.5" />
                    <span>Searching Knowledge Base...</span>
                  </>
                ) : (
                  <>
                    <Search className="h-4 w-4 mr-1.5" />
                    <span>Find Similar Projects &amp; Evidence</span>
                  </>
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Reviewer Safety Disclaimer Banner */}
      {disclaimer && (
        <div className="p-3 bg-amber-50 border border-amber-200 rounded-md flex items-start space-x-2.5 text-xs text-amber-900">
          <AlertCircle className="h-4 w-4 text-amber-600 flex-shrink-0 mt-0.5" />
          <div>
            <span className="font-bold">Reviewer Safety Notice:</span> {disclaimer}
          </div>
        </div>
      )}

      {/* Results Display */}
      {results !== null && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-900">
              Similarity Search Results ({results.length} related projects found)
            </h3>
          </div>

          {results.length > 0 ? (
            <div className="space-y-4">
              {results.map((item) => (
                <Card key={item.projectId} className="border border-slate-200 hover:border-blue-300 transition-colors">
                  <CardContent className="p-5 space-y-3">
                    <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
                      <div className="space-y-1 max-w-2xl">
                        <div className="flex flex-wrap items-center gap-2">
                          <Badge variant="outline" className="font-mono text-[10px]">
                            {item.projectCode}
                          </Badge>
                          <Badge
                            variant={
                              item.similarityPercentage >= 65
                                ? "success"
                                : item.similarityPercentage >= 35
                                ? "warning"
                                : "secondary"
                            }
                            className="text-xs font-bold"
                          >
                            {item.similarityPercentage}% Similarity
                          </Badge>
                          <Badge variant="outline" className="text-[10px]">
                            {item.relationship.replace("_", " ")}
                          </Badge>
                          <Badge
                            variant={item.provenance.sourceType === "OFFICIAL" ? "info" : "secondary"}
                            className="text-[10px]"
                          >
                            {item.provenance.sourceType === "OFFICIAL" ? "OFFICIAL" : "DEMO"}
                          </Badge>
                        </div>
                        <h4 className="text-sm font-bold text-slate-900 leading-snug">{item.projectTitle}</h4>
                        <p className="text-xs text-slate-600">
                          Agency: <span className="font-semibold text-slate-800">{item.institution}</span> • Domain: {item.domain}
                        </p>
                      </div>

                      <div className="text-left sm:text-right flex-shrink-0">
                        <span className="text-[10px] font-mono uppercase text-slate-400 block">Approved Cost</span>
                        <span className="text-sm font-bold font-mono text-slate-900">
                          {item.approvedCostRaw ? item.approvedCostRaw : formatCurrency(item.approvedCost)}
                        </span>
                      </div>
                    </div>

                    {/* Matched Fields Tags */}
                    {item.matchedFields.length > 0 && (
                      <div className="flex items-center space-x-2 pt-1">
                        <span className="text-[10px] font-mono text-slate-400 uppercase">Matched Concepts:</span>
                        <div className="flex flex-wrap gap-1">
                          {item.matchedFields.map((f) => (
                            <Badge key={f} variant="outline" className="text-[9px] bg-slate-50 uppercase">
                              {f}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Evidence List */}
                    {item.evidence.length > 0 && (
                      <div className="space-y-2 pt-2 border-t border-slate-100">
                        <h5 className="text-[11px] font-semibold text-slate-700 uppercase tracking-wider">
                          Extracted Evidence &amp; Reason
                        </h5>
                        <div className="space-y-1.5">
                          {item.evidence.map((ev, idx) => (
                            <div key={idx} className="p-2.5 bg-slate-50 rounded border border-slate-200 text-xs space-y-1">
                              <p className="text-slate-800 font-medium">{ev.reason}</p>
                              <p className="text-slate-600 font-mono text-[11px] bg-white p-1.5 rounded border border-slate-200">
                                &quot;{ev.snippet}&quot;
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Source Provenance Footer */}
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 pt-3 border-t border-slate-100 text-xs text-slate-500">
                      <div className="flex items-center space-x-3">
                        <span className="flex items-center">
                          <FileText className="h-3.5 w-3.5 text-slate-400 mr-1" />
                          Source: <strong className="ml-1 text-slate-700">{item.provenance.source}</strong>
                        </span>
                        <span>
                          Pages: <strong className="text-slate-700">Pp. {item.provenance.sourcePageStart}-{item.provenance.sourcePageEnd || item.provenance.sourcePageStart}</strong>
                        </span>
                        <Badge
                          variant={
                            item.provenance.verificationStatus === "VERIFIED"
                              ? "info"
                              : item.provenance.verificationStatus === "REJECTED"
                              ? "danger"
                              : "warning"
                          }
                          className="text-[9px]"
                        >
                          {item.provenance.verificationStatus.replace("_", " ")}
                        </Badge>
                      </div>

                      <div className="flex items-center space-x-2">
                        {item.provenance.sourceUrl && (
                          <a
                            href={item.provenance.sourceUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:underline flex items-center text-xs font-mono"
                          >
                            <ExternalLink className="h-3 w-3 mr-1" />
                            Official PDF
                          </a>
                        )}
                        <Link href={`/projects/${item.projectId}`}>
                          <Button variant="outline" size="sm" className="h-7 text-xs">
                            View Full Project <ArrowRight className="h-3 w-3 ml-1" />
                          </Button>
                        </Link>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <div className="p-8 text-center text-xs text-slate-500 bg-white border border-slate-200 rounded-md">
              No historical CIL/CMPDI R&amp;D projects match the specified proposal concepts.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
