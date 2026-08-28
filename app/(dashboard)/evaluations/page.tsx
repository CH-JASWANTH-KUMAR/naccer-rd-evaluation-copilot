"use client";

import React, { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { CheckSquare, Search, Plus, Loader2, ArrowRight } from "lucide-react";
import { evaluationService, EvaluationDetail } from "@/lib/api/evaluations";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { Card, CardContent } from "@/components/ui/card";

export default function EvaluationsPage() {
  const [evaluations, setEvaluations] = useState<EvaluationDetail[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");

  const fetchEvaluations = useCallback(() => {
    setLoading(true);
    evaluationService
      .getEvaluations({
        status: status || undefined,
      })
      .then((data) => {
        let filtered = data;
        if (search) {
          const q = search.toLowerCase();
          filtered = filtered.filter(
            (e) =>
              e.id.toLowerCase().includes(q) ||
              e.proposalId.toLowerCase().includes(q) ||
              e.proposal?.title?.toLowerCase().includes(q) ||
              e.proposal?.proposalReference?.toLowerCase().includes(q)
          );
        }
        setEvaluations(filtered);
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  }, [search, status]);

  useEffect(() => {
    let isMounted = true;
    evaluationService
      .getEvaluations({
        status: status || undefined,
      })
      .then((data) => {
        if (isMounted) {
          let filtered = data;
          if (search) {
            const q = search.toLowerCase();
            filtered = filtered.filter(
              (e) =>
                e.id.toLowerCase().includes(q) ||
                e.proposalId.toLowerCase().includes(q) ||
                e.proposal?.title?.toLowerCase().includes(q) ||
                e.proposal?.proposalReference?.toLowerCase().includes(q)
            );
          }
          setEvaluations(filtered);
          setLoading(false);
        }
      })
      .catch(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [search, status]);

  return (
    <div className="space-y-6">
      {/* Page Title */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight flex items-center space-x-2">
            <CheckSquare className="h-5 w-5 text-blue-600" />
            <span>Human Reviewer Evaluation Workspace</span>
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Configurable decision-support rubric evaluations, transparent score calculations, and evidence matrices.
          </p>
        </div>

        <Link href="/proposals">
          <Button size="sm" className="bg-blue-600 hover:bg-blue-700 text-white">
            <Plus className="h-4 w-4 mr-1.5" />
            Start Proposal Evaluation
          </Button>
        </Link>
      </div>

      {/* Filter Bar */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          fetchEvaluations();
        }}
        className="grid grid-cols-1 sm:grid-cols-3 gap-3 bg-white p-4 rounded-lg border border-slate-200 shadow-xs"
      >
        <div className="relative sm:col-span-1">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-400" />
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search reference, title, ID..."
            className="pl-9 text-xs"
          />
        </div>

        <div>
          <Select value={status} onChange={(e) => setStatus(e.target.value)} className="text-xs">
            <option value="">All Evaluation Statuses</option>
            <option value="DRAFT">Draft</option>
            <option value="SUBMITTED">Submitted</option>
            <option value="RETURNED_FOR_REVISION">Returned for Revision</option>
          </Select>
        </div>

        <div>
          <Button type="submit" size="sm" className="w-full h-9">
            Filter
          </Button>
        </div>
      </form>

      {/* Evaluation Directory Table */}
      <Card>
        <CardContent className="p-0">
          {loading ? (
            <div className="p-8 flex items-center justify-center space-x-2 text-xs text-slate-500">
              <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
              <span>Fetching reviewer evaluations...</span>
            </div>
          ) : evaluations.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>PROPOSAL &amp; REFERENCE</TableHead>
                  <TableHead>REVIEWER</TableHead>
                  <TableHead>RUBRIC VERSION</TableHead>
                  <TableHead>OVERALL SCORE</TableHead>
                  <TableHead>STATUS</TableHead>
                  <TableHead className="text-right">ACTION</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {evaluations.map((ev) => (
                  <TableRow key={ev.id}>
                    <TableCell className="font-medium text-slate-900">
                      <div className="max-w-md space-y-1">
                        <div className="flex items-center space-x-2">
                          <Badge variant="outline" className="font-mono text-[10px]">
                            {ev.proposal?.proposalReference || `PR-2026-${ev.proposalId.slice(0, 6)}`}
                          </Badge>
                        </div>
                        <Link
                          href={`/evaluations/${ev.id}`}
                          className="font-semibold text-slate-900 hover:underline line-clamp-2 text-xs"
                        >
                          {ev.proposal?.title || "Proposal Evaluation Workspace"}
                        </Link>
                      </div>
                    </TableCell>
                    <TableCell className="text-xs font-semibold text-slate-800">
                      {ev.reviewerId}
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className="text-[10px] font-mono">
                        {ev.rubricVersion}
                      </Badge>
                    </TableCell>
                    <TableCell className="font-mono text-xs font-bold text-blue-600">
                      {ev.overallScore !== null && ev.overallScore !== undefined ? `${ev.overallScore.toFixed(1)} / 10` : "—"}
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={ev.status === "SUBMITTED" ? "success" : "warning"}
                        className="text-[10px]"
                      >
                        {ev.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <Link href={`/evaluations/${ev.id}`}>
                        <Button variant="outline" size="sm" className="h-7 text-xs">
                          {ev.status === "SUBMITTED" ? "View Evaluation" : "Continue Evaluation"} <ArrowRight className="h-3 w-3 ml-1" />
                        </Button>
                      </Link>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="p-8 text-center text-xs text-slate-500">
              No evaluation records found matching current search criteria.
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
