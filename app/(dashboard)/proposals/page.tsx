"use client";

import React, { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { FileText, Search, Plus, Loader2, ArrowRight } from "lucide-react";
import { proposalService } from "@/lib/api/proposals";
import { Proposal } from "@/lib/types";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { Card, CardContent } from "@/components/ui/card";
import { RESEARCH_DOMAINS } from "@/lib/constants";
import { formatCurrency } from "@/lib/utils";

export default function ProposalsPage() {
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [search, setSearch] = useState("");
  const [domain, setDomain] = useState("");
  const [completenessStatus, setCompletenessStatus] = useState("");
  const [complianceStatus, setComplianceStatus] = useState("");

  const fetchProposals = useCallback(() => {
    setLoading(true);
    proposalService
      .getProposals({
        search: search || undefined,
        domain: domain || undefined,
        completenessStatus: completenessStatus || undefined,
        complianceStatus: complianceStatus || undefined,
      })
      .then((data) => {
        setProposals(data);
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  }, [search, domain, completenessStatus, complianceStatus]);

  useEffect(() => {
    let isMounted = true;
    proposalService
      .getProposals({
        search: search || undefined,
        domain: domain || undefined,
        completenessStatus: completenessStatus || undefined,
        complianceStatus: complianceStatus || undefined,
      })
      .then((data) => {
        if (isMounted) {
          setProposals(data);
          setLoading(false);
        }
      })
      .catch(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [search, domain, completenessStatus, complianceStatus]);

  return (
    <div className="space-y-6">
      {/* Page Title & Upload Action */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight flex items-center space-x-2">
            <FileText className="h-5 w-5 text-blue-600" />
            <span>R&amp;D Proposal Intake &amp; Preliminary Scrutiny</span>
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Upload proposal PDFs, parse structured document fields, and evaluate completeness &amp; rule-based financial compliance.
          </p>
        </div>

        <Link href="/upload">
          <Button size="sm" className="bg-blue-600 hover:bg-blue-700 text-white">
            <Plus className="h-4 w-4 mr-1.5" />
            Upload Proposal PDF
          </Button>
        </Link>
      </div>

      {/* Filter Bar */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          fetchProposals();
        }}
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 bg-white p-4 rounded-lg border border-slate-200 shadow-xs"
      >
        <div className="relative">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-400" />
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search reference, title, PI..."
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
          <Select
            value={completenessStatus}
            onChange={(e) => setCompletenessStatus(e.target.value)}
            className="text-xs"
          >
            <option value="">All Completeness</option>
            <option value="COMPLETE">Complete (Pass)</option>
            <option value="INCOMPLETE">Incomplete</option>
          </Select>
        </div>

        <div>
          <Select value={complianceStatus} onChange={(e) => setComplianceStatus(e.target.value)} className="text-xs">
            <option value="">All Financial Compliance</option>
            <option value="COMPLIANT">Compliant</option>
            <option value="FLAGGED">Flagged (Mismatch)</option>
            <option value="NEEDS_JUSTIFICATION">Needs Justification</option>
          </Select>
        </div>

        <div>
          <Button type="submit" size="sm" className="w-full h-9">
            Filter
          </Button>
        </div>
      </form>

      {/* Proposals Directory Table */}
      <Card>
        <CardContent className="p-0">
          {loading ? (
            <div className="p-8 flex items-center justify-center space-x-2 text-xs text-slate-500">
              <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
              <span>Fetching proposal records...</span>
            </div>
          ) : proposals.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>PROPOSAL REFERENCE &amp; TITLE</TableHead>
                  <TableHead>INSTITUTION &amp; PI</TableHead>
                  <TableHead>REQUESTED BUDGET</TableHead>
                  <TableHead>COMPLETENESS</TableHead>
                  <TableHead>FINANCIAL CHECK</TableHead>
                  <TableHead className="text-right">ACTION</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {proposals.map((prop) => (
                  <TableRow key={prop.id}>
                    <TableCell className="font-medium text-slate-900">
                      <div className="max-w-md space-y-1">
                        <div className="flex items-center space-x-2">
                          <Badge variant="outline" className="font-mono text-[10px]">
                            {prop.proposalReference || prop.id}
                          </Badge>
                          <span className="text-[10px] text-slate-500 font-mono">{prop.domain}</span>
                        </div>
                        <Link
                          href={`/proposals/${prop.id}`}
                          className="font-semibold text-slate-900 hover:underline line-clamp-2 text-xs"
                        >
                          {prop.title}
                        </Link>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="text-xs space-y-0.5">
                        <span className="font-semibold text-slate-800 block">{prop.institution.name}</span>
                        <span className="text-slate-500 font-mono text-[11px]">PI: {prop.principalInvestigator}</span>
                      </div>
                    </TableCell>
                    <TableCell className="font-mono text-xs font-semibold text-slate-800">
                      {formatCurrency(prop.budgetTotal || prop.proposedBudget || 0)}
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={prop.completenessStatus === "COMPLETE" ? "success" : "warning"}
                        className="text-[10px]"
                      >
                        {prop.completenessStatus}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          prop.complianceStatus === "COMPLIANT"
                            ? "info"
                            : prop.complianceStatus === "FLAGGED"
                            ? "danger"
                            : "warning"
                        }
                        className="text-[10px]"
                      >
                        {prop.complianceStatus}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <Link href={`/proposals/${prop.id}`}>
                        <Button variant="outline" size="sm" className="h-7 text-xs">
                          Review Proposal <ArrowRight className="h-3 w-3 ml-1" />
                        </Button>
                      </Link>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="p-8 text-center text-xs text-slate-500">
              No proposal intake records found matching current search criteria.
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
