import React from "react";
import Link from "next/link";
import { Plus, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { proposalService } from "@/lib/api/proposals";
import { RESEARCH_DOMAINS } from "@/lib/constants";
import { formatCurrency } from "@/lib/utils";

export default async function ProposalsListPage() {
  const proposals = await proposalService.getProposals();

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "UNDER_REVIEW":
        return <Badge variant="info">Under Review</Badge>;
      case "AWAITING_REVIEW":
        return <Badge variant="warning">Awaiting Review</Badge>;
      case "POTENTIAL_ISSUES":
        return <Badge variant="danger">Potential Issues</Badge>;
      case "COMPLETED":
        return <Badge variant="success">Completed</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">R&amp;D Proposals Directory</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            All submitted research proposals undergoing technical &amp; compliance evaluation.
          </p>
        </div>
        <Link href="/upload">
          <Button size="sm">
            <Plus className="h-3.5 w-3.5 mr-1.5" />
            Upload New Proposal
          </Button>
        </Link>
      </div>

      {/* Filter & Search Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 bg-white p-4 rounded-lg border border-slate-200 shadow-xs">
        <div className="relative">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-400" />
          <Input placeholder="Filter by Title, ID or PI..." className="pl-9" />
        </div>
        <div>
          <Select defaultValue="">
            <option value="">All Research Domains</option>
            {RESEARCH_DOMAINS.map((domain) => (
              <option key={domain} value={domain}>
                {domain}
              </option>
            ))}
          </Select>
        </div>
        <div>
          <Select defaultValue="">
            <option value="">All Statuses</option>
            <option value="UNDER_REVIEW">Under Review</option>
            <option value="AWAITING_REVIEW">Awaiting Review</option>
            <option value="POTENTIAL_ISSUES">Potential Issues</option>
            <option value="COMPLETED">Completed</option>
          </Select>
        </div>
      </div>

      {/* Proposals Directory Table */}
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>PROPOSAL ID</TableHead>
            <TableHead>TITLE &amp; DETAILS</TableHead>
            <TableHead>INSTITUTION</TableHead>
            <TableHead>BUDGET</TableHead>
            <TableHead>STATUS</TableHead>
            <TableHead className="text-right">ACTION</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {proposals.map((proposal) => (
            <TableRow key={proposal.id}>
              <TableCell className="font-mono text-xs font-bold text-slate-800">
                {proposal.id}
              </TableCell>
              <TableCell>
                <div className="max-w-lg">
                  <Link
                    href={`/proposals/${proposal.id}`}
                    className="font-semibold text-slate-900 hover:underline line-clamp-1"
                  >
                    {proposal.title}
                  </Link>
                  <div className="text-[11px] text-slate-500 mt-0.5 flex items-center space-x-2 font-mono">
                    <span>PI: {proposal.principalInvestigator}</span>
                    <span>•</span>
                    <span>{proposal.domain}</span>
                  </div>
                </div>
              </TableCell>
              <TableCell>
                <span className="font-medium text-slate-800">{proposal.institution.name}</span>
                <span className="text-[10px] text-slate-500 block">{proposal.institution.type}</span>
              </TableCell>
              <TableCell className="font-mono text-xs font-semibold text-slate-800">
                {formatCurrency(proposal.proposedBudget)}
              </TableCell>
              <TableCell>{getStatusBadge(proposal.status)}</TableCell>
              <TableCell className="text-right">
                <Link href={`/proposals/${proposal.id}`}>
                  <Button variant="outline" size="sm" className="h-7 text-xs">
                    Evaluate Workspace
                  </Button>
                </Link>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
