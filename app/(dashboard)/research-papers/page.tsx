"use client";

import React, { useEffect, useState } from "react";
import { Search, BookOpen, Sparkles, Loader2, Database, Cpu, FlaskConical, AlertTriangle } from "lucide-react";
import {
  researchPaperService,
  ResearchPaper,
  ResearchPaperSearchResult,
  ScientificMetric,
  ScientificDataset,
  ScientificExperiment,
} from "@/lib/api/research-papers";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";

export default function ResearchPapersPage() {
  const [activeTab, setActiveTab] = useState<"directory" | "evidence" | "search">("directory");
  const [papers, setPapers] = useState<ResearchPaper[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPaper, setSelectedPaper] = useState<ResearchPaper | null>(null);

  // Evidence States
  const [metrics, setMetrics] = useState<ScientificMetric[]>([]);
  const [datasets, setDatasets] = useState<ScientificDataset[]>([]);
  const [experiments, setExperiments] = useState<ScientificExperiment[]>([]);

  // Search State
  const [searchQuery, setSearchQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<ResearchPaperSearchResult[]>([]);
  const [searchDisclaimer, setSearchDisclaimer] = useState("");

  const [seeding, setSeeding] = useState(false);

  useEffect(() => {
    researchPaperService
      .getResearchPapers()
      .then((data) => {
        setPapers(data);
        if (data.length > 0) {
          setSelectedPaper(data[0]);
        }
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!selectedPaper) return;
    let isMounted = true;
    researchPaperService.getPaperMetrics(selectedPaper.id).then((m) => {
      if (isMounted) setMetrics(m);
    });
    researchPaperService.getPaperDatasets(selectedPaper.id).then((d) => {
      if (isMounted) setDatasets(d);
    });
    researchPaperService.getPaperExperiments(selectedPaper.id).then((e) => {
      if (isMounted) setExperiments(e);
    });
    return () => {
      isMounted = false;
    };
  }, [selectedPaper]);

  const refreshPapers = async () => {
    setLoading(true);
    try {
      const data = await researchPaperService.getResearchPapers();
      setPapers(data);
      if (data.length > 0 && !selectedPaper) {
        setSelectedPaper(data[0]);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSeedFixture = async () => {
    try {
      setSeeding(true);
      await researchPaperService.seedResearchPaperFixture();
      await refreshPapers();
    } catch {
      // Error handled
    } finally {
      setSeeding(false);
    }
  };

  const handleSearchSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    try {
      setIsSearching(true);
      const res = await researchPaperService.searchResearchPapers(searchQuery, undefined, 5);
      setSearchResults(res.results);
      setSearchDisclaimer(res.disclaimer);
    } catch {
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <div className="flex items-center gap-2">
            <BookOpen className="h-6 w-6 text-primary" />
            <h1 className="text-2xl font-bold tracking-tight text-foreground">
              Scientific Research Paper Knowledge Base
            </h1>
            <Badge variant="outline" className="bg-primary/10 text-primary border-primary/30">
              STEP 3 Scientific Evidence Layer
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            Structured, page-traceable extraction of scientific metrics, datasets, algorithms, baselines, and experimental findings.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            onClick={handleSeedFixture}
            disabled={seeding}
            className="flex items-center gap-1.5"
          >
            {seeding ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4 text-amber-500" />}
            <span>Seed Fixture Paper</span>
          </Button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-border">
        <button
          onClick={() => setActiveTab("directory")}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === "directory"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          Corpus Directory ({papers.length})
        </button>
        <button
          onClick={() => setActiveTab("evidence")}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === "evidence"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          Scientific Evidence & Metrics
        </button>
        <button
          onClick={() => setActiveTab("search")}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === "search"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          Scientific Concept Search
        </button>
      </div>

      {/* Tab 1: Directory */}
      {activeTab === "directory" && (
        <div className="space-y-4">
          {loading ? (
            <div className="flex items-center justify-center py-12 text-muted-foreground">
              <Loader2 className="h-6 w-6 animate-spin mr-2" />
              <span>Loading scientific corpus...</span>
            </div>
          ) : papers.length === 0 ? (
            <Card className="border-dashed p-8 text-center">
              <BookOpen className="h-10 w-10 text-muted-foreground mx-auto mb-3 opacity-50" />
              <h3 className="text-lg font-semibold">No Research Papers Ingested Yet</h3>
              <p className="text-sm text-muted-foreground max-w-md mx-auto mt-1 mb-4">
                Click below to seed the synthetic coal mining predictive maintenance paper fixture.
              </p>
              <Button onClick={handleSeedFixture} disabled={seeding}>
                {seeding && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
                Seed Synthetic Research Paper
              </Button>
            </Card>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left Column: Papers List */}
              <div className="lg:col-span-2 space-y-4">
                <Card>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Title & Authors</TableHead>
                        <TableHead>Domain</TableHead>
                        <TableHead>Year</TableHead>
                        <TableHead>Pages</TableHead>
                        <TableHead>Action</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {papers.map((p) => (
                        <TableRow key={p.id} className="cursor-pointer hover:bg-muted/50">
                          <TableCell className="max-w-md">
                            <div className="font-medium text-sm line-clamp-1">{p.title}</div>
                            <div className="text-xs text-muted-foreground line-clamp-1">
                              {p.authors || "Unknown Authors"}
                            </div>
                          </TableCell>
                          <TableCell>
                            <Badge variant="secondary" className="text-xs">
                              {p.researchDomain}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-xs">{p.publicationYear || "N/A"}</TableCell>
                          <TableCell className="text-xs">{p.pageCount} Pages</TableCell>
                          <TableCell>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => {
                                setSelectedPaper(p);
                                setActiveTab("evidence");
                              }}
                              className="text-xs text-primary hover:text-primary"
                            >
                              View Evidence
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </Card>
              </div>

              {/* Right Column: Selected Paper Quick Summary */}
              <div className="space-y-4">
                {selectedPaper ? (
                  <Card className="p-4 space-y-4">
                    <div>
                      <Badge className="bg-emerald-500/10 text-emerald-600 border-emerald-500/30 mb-2">
                        Traceable Scientific Evidence Source
                      </Badge>
                      <h3 className="font-semibold text-base leading-tight">{selectedPaper.title}</h3>
                      <p className="text-xs text-muted-foreground mt-1">{selectedPaper.authors}</p>
                    </div>

                    <div className="space-y-2 text-xs border-t border-border pt-3">
                      <div>
                        <span className="font-semibold">DOI:</span> {selectedPaper.doi || "N/A"}
                      </div>
                      <div>
                        <span className="font-semibold">File Hash:</span>{" "}
                        <code className="text-[10px] bg-muted px-1 py-0.5 rounded">
                          {selectedPaper.fileHash.slice(0, 16)}...
                        </code>
                      </div>
                      <div>
                        <span className="font-semibold">Source Filename:</span> {selectedPaper.sourceFilename}
                      </div>
                    </div>

                    <Button
                      onClick={() => setActiveTab("evidence")}
                      className="w-full text-xs flex items-center justify-center gap-1.5"
                    >
                      <FlaskConical className="h-4 w-4" />
                      <span>Inspect Extracted Scientific Evidence</span>
                    </Button>
                  </Card>
                ) : (
                  <Card className="p-6 text-center text-muted-foreground text-xs">
                    Select a paper from the list to inspect page-level evidence.
                  </Card>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Scientific Evidence & Metrics */}
      {activeTab === "evidence" && (
        <div className="space-y-6">
          {selectedPaper ? (
            <div className="space-y-6">
              {/* Paper Header Banner */}
              <Card className="p-4 bg-muted/30 border-l-4 border-l-primary">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
                  <div>
                    <h2 className="text-lg font-bold text-foreground leading-tight">{selectedPaper.title}</h2>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      {selectedPaper.authors} • {selectedPaper.publicationYear} • DOI: {selectedPaper.doi || "N/A"}
                    </p>
                  </div>
                  <Badge variant="outline" className="font-mono text-xs self-start md:self-auto">
                    {selectedPaper.pages.length} Pages Extracted
                  </Badge>
                </div>
              </Card>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Left Column: Reported Metrics Table */}
                  <Card className="p-4 space-y-4 lg:col-span-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <FlaskConical className="h-5 w-5 text-primary" />
                        <h3 className="font-semibold text-base">Reported Scientific Metrics</h3>
                      </div>
                      <Badge variant="secondary" className="text-xs">
                        Strict Raw Preservation
                      </Badge>
                    </div>

                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Metric</TableHead>
                          <TableHead>Model / Target</TableHead>
                          <TableHead>Raw Value</TableHead>
                          <TableHead>Normalized</TableHead>
                          <TableHead>Unit</TableHead>
                          <TableHead>Page</TableHead>
                          <TableHead>Evidence ID</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {metrics.length === 0 ? (
                          <TableRow>
                            <TableCell colSpan={7} className="text-center text-xs text-muted-foreground py-4">
                              No explicit numerical metrics reported.
                            </TableCell>
                          </TableRow>
                        ) : (
                          metrics.map((m) => (
                            <TableRow key={m.evidenceId}>
                              <TableCell className="font-medium text-sm">{m.metricName}</TableCell>
                              <TableCell>
                                <Badge variant="outline" className="text-xs bg-slate-100 dark:bg-slate-800">
                                  {m.comparisonTarget || "General Model"}
                                </Badge>
                              </TableCell>
                              <TableCell className="font-mono text-xs font-semibold">{m.rawValue}</TableCell>
                              <TableCell className="font-mono text-xs">
                                {m.normalizedValue !== null ? m.normalizedValue : "N/A"}
                              </TableCell>
                              <TableCell className="text-xs">{m.unit || "N/A"}</TableCell>
                              <TableCell className="text-xs">Page {m.sourcePage}</TableCell>
                              <TableCell>
                                <Badge variant="default" className="font-mono text-[10px]">
                                  [{m.evidenceId}]
                                </Badge>
                              </TableCell>
                            </TableRow>
                          ))
                        )}
                      </TableBody>
                    </Table>
                  </Card>

                  {/* Datasets Card */}
                  <Card className="p-4 space-y-3">
                    <div className="flex items-center gap-2 border-b border-border pb-2">
                      <Database className="h-4 w-4 text-emerald-600" />
                      <h3 className="font-semibold text-sm">Dataset Specifications</h3>
                    </div>
                    {datasets.map((d) => (
                      <div key={d.evidenceId} className="space-y-2 text-xs">
                        <div className="flex items-center justify-between font-medium">
                          <span>{d.datasetName}</span>
                          <Badge variant="outline" className="font-mono text-[10px]">
                            [{d.evidenceId}]
                          </Badge>
                        </div>
                        <div className="grid grid-cols-2 gap-2 p-2 bg-muted/40 rounded border border-border/50">
                          <div>
                            <span className="text-muted-foreground">Observations:</span> {d.sampleCountRaw}
                          </div>
                          <div>
                            <span className="text-muted-foreground">Sensors:</span> {d.sensorCount || "N/A"}
                          </div>
                          <div>
                            <span className="text-muted-foreground">Features:</span> {d.featureCount || "N/A"}
                          </div>
                          <div>
                            <span className="text-muted-foreground">Page:</span> Page {d.sourcePage}
                          </div>
                        </div>
                      </div>
                    ))}
                  </Card>

                  {/* Experimental Setup & Baselines Card */}
                  <Card className="p-4 space-y-3">
                    <div className="flex items-center gap-2 border-b border-border pb-2">
                      <Cpu className="h-4 w-4 text-amber-600" />
                      <h3 className="font-semibold text-sm">Experimental Setup & Baselines</h3>
                    </div>
                    {experiments.map((exp) => (
                      <div key={exp.evidenceId} className="space-y-2 text-xs">
                        <div>
                          <span className="font-semibold">Algorithms / Models:</span>{" "}
                          {exp.algorithms.join(", ") || "NOT_REPORTED"}
                        </div>
                        <div>
                          <span className="font-semibold">Baselines Compared:</span>{" "}
                          {exp.baselines.join(", ") || "NOT_REPORTED"}
                        </div>
                        <div>
                          <span className="font-semibold">Validation Protocol:</span>{" "}
                          {exp.validationStrategy || "NOT_REPORTED"}
                        </div>
                        <div>
                          <span className="font-semibold">Hardware / Telemetry:</span>{" "}
                          {exp.hardwareSensors.join(", ") || "NOT_REPORTED"}
                        </div>
                        <div className="pt-1 text-right">
                          <Badge variant="outline" className="font-mono text-[10px]">
                            [{exp.evidenceId}] • Page {exp.sourcePage}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </Card>
                </div>
            </div>
          ) : (
            <Card className="p-6 text-center text-muted-foreground text-xs">
              Select a paper from the Corpus Directory tab to view extracted evidence.
            </Card>
          )}
        </div>
      )}

      {/* Tab 3: Scientific Concept Search */}
      {activeTab === "search" && (
        <div className="space-y-6">
          <Card className="p-4">
            <form onSubmit={handleSearchSubmit} className="flex gap-3">
              <Input
                placeholder="Search scientific concepts (e.g. vibration telemetry failure prediction)..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="flex-1"
              />
              <Button type="submit" disabled={isSearching || !searchQuery.trim()}>
                {isSearching ? <Loader2 className="h-4 w-4 animate-spin mr-1.5" /> : <Search className="h-4 w-4 mr-1.5" />}
                Search Corpus
              </Button>
            </form>
          </Card>

          {searchResults.length > 0 && (
            <div className="space-y-4">
              {searchDisclaimer && (
                <div className="p-3 bg-amber-500/10 border border-amber-500/30 rounded text-xs text-amber-700 dark:text-amber-400 flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 flex-shrink-0 text-amber-500" />
                  <span>{searchDisclaimer}</span>
                </div>
              )}

              <div className="space-y-3">
                {searchResults.map((res) => (
                  <Card key={`${res.paperId}-${res.evidenceId}`} className="p-4 border-l-4 border-l-primary">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <div className="flex items-center gap-2">
                          <Badge variant="default" className="font-mono text-xs">
                            [{res.evidenceId}]
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            Page {res.pageNumber} • {res.sourceFilename}
                          </span>
                        </div>
                        <h4 className="font-semibold text-sm mt-1">{res.title}</h4>
                        <p className="text-xs text-muted-foreground">{res.authors}</p>
                      </div>

                      <Badge variant="outline" className="bg-primary/10 text-primary border-primary/30">
                        {Math.round(res.relevanceScore * 100)}% Relevance
                      </Badge>
                    </div>

                    <div className="mt-3 p-2 bg-muted/50 rounded text-xs text-foreground font-mono">
                      &quot;{res.snippet}&quot;
                    </div>

                    <div className="flex items-center gap-2 mt-3">
                      {res.matchedDimensions.map((d) => (
                        <Badge key={d} variant="secondary" className="text-[10px] uppercase">
                          {d}
                        </Badge>
                      ))}
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
