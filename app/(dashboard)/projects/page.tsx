"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { Search, Database, Loader2 } from "lucide-react";
import { projectService } from "@/lib/api/projects";
import { HistoricalProject } from "@/lib/types";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { Card, CardContent } from "@/components/ui/card";
import { RESEARCH_DOMAINS } from "@/lib/constants";
import { formatCurrency } from "@/lib/utils";

export default function HistoricalProjectsPage() {
  const [projects, setProjects] = useState<HistoricalProject[]>([]);
  const [loading, setLoading] = useState(true);

  // Filter States
  const [search, setSearch] = useState("");
  const [domain, setDomain] = useState("");
  const [status, setStatus] = useState("");
  const [sourceType, setSourceType] = useState("");
  const [verificationStatus, setVerificationStatus] = useState("");

  const fetchProjects = () => {
    setLoading(true);
    projectService
      .getHistoricalProjects({
        search: search || undefined,
        domain: domain || undefined,
        status: status || undefined,
        sourceType: sourceType || undefined,
        verificationStatus: verificationStatus || undefined,
      })
      .then((data) => {
        setProjects(data);
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    let isMounted = true;
    projectService
      .getHistoricalProjects({
        search: search || undefined,
        domain: domain || undefined,
        status: status || undefined,
        sourceType: sourceType || undefined,
        verificationStatus: verificationStatus || undefined,
      })
      .then((data) => {
        if (isMounted) {
          setProjects(data);
          setLoading(false);
        }
      })
      .catch(() => {
        if (isMounted) {
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [search, domain, status, sourceType, verificationStatus]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchProjects();
  };

  return (
    <div className="space-y-6">
      {/* Page Title */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight flex items-center space-x-2">
            <Database className="h-5 w-5 text-blue-600" />
            <span>Historical R&amp;D Project Knowledge Base</span>
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Official CIL / CMPDI historical catalogue records &amp; benchmark evidence repository.
          </p>
        </div>
      </div>

      {/* Filter Bar */}
      <form onSubmit={handleSearchSubmit} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-3 bg-white p-4 rounded-lg border border-slate-200 shadow-xs">
        <div className="relative lg:col-span-1">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-400" />
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search code, title..."
            className="pl-9 text-xs"
          />
        </div>

        <div>
          <Select value={domain} onChange={(e) => setDomain(e.target.value)} className="text-xs">
            <option value="">All Research Domains</option>
            {RESEARCH_DOMAINS.map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </Select>
        </div>

        <div>
          <Select value={status} onChange={(e) => setStatus(e.target.value)} className="text-xs">
            <option value="">All Statuses</option>
            <option value="ONGOING">Ongoing</option>
            <option value="COMPLETED">Completed</option>
            <option value="TERMINATED">Terminated</option>
          </Select>
        </div>

        <div>
          <Select value={sourceType} onChange={(e) => setSourceType(e.target.value)} className="text-xs">
            <option value="">All Sources</option>
            <option value="OFFICIAL">Official CIL/CMPDI</option>
            <option value="SYNTHETIC">Synthetic Demo</option>
          </Select>
        </div>

        <div>
          <Select value={verificationStatus} onChange={(e) => setVerificationStatus(e.target.value)} className="text-xs">
            <option value="">All Verification</option>
            <option value="NEEDS_REVIEW">Needs Review</option>
            <option value="VERIFIED">Verified</option>
            <option value="REJECTED">Rejected</option>
          </Select>
        </div>

        <div>
          <Button type="submit" size="sm" className="w-full h-9">
            Search
          </Button>
        </div>
      </form>

      {/* Projects Directory Table */}
      <Card>
        <CardContent className="p-0">
          {loading ? (
            <div className="p-8 flex items-center justify-center space-x-2 text-xs text-slate-500">
              <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
              <span>Querying historical project records...</span>
            </div>
          ) : projects.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>PROJECT CODE &amp; TITLE</TableHead>
                  <TableHead>INSTITUTION</TableHead>
                  <TableHead>SOURCE</TableHead>
                  <TableHead>COST</TableHead>
                  <TableHead>STATUS</TableHead>
                  <TableHead>VERIFICATION</TableHead>
                  <TableHead className="text-right">ACTION</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {projects.map((proj) => (
                  <TableRow key={proj.id}>
                    <TableCell className="font-medium text-slate-900">
                      <div className="max-w-md space-y-1">
                        <div className="flex items-center space-x-2">
                          <Badge variant="outline" className="font-mono text-[10px]">
                            {proj.projectCode || proj.id}
                          </Badge>
                          <span className="text-[10px] text-slate-500 font-mono">{proj.domain}</span>
                        </div>
                        <Link
                          href={`/projects/${proj.id}`}
                          className="font-semibold text-slate-900 hover:underline line-clamp-2 text-xs"
                        >
                          {proj.title}
                        </Link>
                      </div>
                    </TableCell>
                    <TableCell>
                      <span className="font-semibold text-slate-800 text-xs">{proj.institution.name}</span>
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={proj.sourceType === "OFFICIAL" ? "success" : "secondary"}
                        className="text-[10px]"
                      >
                        {proj.sourceType === "OFFICIAL" ? "OFFICIAL (CIL/CMPDI)" : "DEMO / SYNTHETIC"}
                      </Badge>
                    </TableCell>
                    <TableCell className="font-mono text-xs font-semibold text-slate-800">
                      {proj.approvedCostRaw ? proj.approvedCostRaw : formatCurrency(proj.totalCost)}
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className="text-[10px]">
                        {proj.status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          proj.verificationStatus === "VERIFIED"
                            ? "info"
                            : proj.verificationStatus === "REJECTED"
                            ? "danger"
                            : "warning"
                        }
                        className="text-[10px]"
                      >
                        {proj.verificationStatus.replace("_", " ")}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <Link href={`/projects/${proj.id}`}>
                        <Button variant="outline" size="sm" className="h-7 text-xs">
                          View Details &amp; Provenance
                        </Button>
                      </Link>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="p-8 text-center text-xs text-slate-500">
              No historical project records match the current search or filter criteria.
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
