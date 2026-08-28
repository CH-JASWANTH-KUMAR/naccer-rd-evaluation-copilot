import React from "react";
import Link from "next/link";
import { FileText, Clock, AlertTriangle, CheckCircle2, ArrowRight, Upload } from "lucide-react";
import { MetricsCard } from "@/components/dashboard/MetricsCard";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { proposalService } from "@/lib/api/proposals";
import { formatDate } from "@/lib/utils";

export default async function DashboardPage() {
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

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case "HIGH":
        return <Badge variant="danger" className="text-[10px]">High Priority</Badge>;
      case "MEDIUM":
        return <Badge variant="warning" className="text-[10px]">Medium Priority</Badge>;
      default:
        return <Badge variant="outline" className="text-[10px]">Low Priority</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner / Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">
            R&D Proposal Evaluation Workspace
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            NaCCER / CMPDI Technical Review & Benchmarking Portal (Frontend Base Foundation)
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <Link href="/upload">
            <Button size="sm">
              <Upload className="h-3.5 w-3.5 mr-1.5" />
              Upload Proposal
            </Button>
          </Link>
        </div>
      </div>

      {/* Metrics Shell (Placeholder Demo Data) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricsCard
          title="Proposals Under Review"
          value={12}
          subtitle="Currently active in evaluation workspace"
          icon={FileText}
          variant="slate"
        />
        <MetricsCard
          title="Awaiting Review"
          value={5}
          subtitle="Pending initial screening & rubric assignment"
          icon={Clock}
          variant="amber"
        />
        <MetricsCard
          title="Potential Issues"
          value={3}
          subtitle="Flagged for financial or compliance variance"
          icon={AlertTriangle}
          variant="amber"
        />
        <MetricsCard
          title="Completed Evaluations"
          value={28}
          subtitle="Finalized assessment reports logged"
          icon={CheckCircle2}
          variant="emerald"
        />
      </div>

      {/* Recent Proposals Table Section */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-sm font-bold text-slate-900">Recent R&D Proposals</h2>
            <p className="text-xs text-slate-500">
              Overview of recent submissions queued for technical & financial benchmarking.
            </p>
          </div>
          <Link href="/proposals">
            <Button variant="outline" size="sm" className="text-xs">
              View All Proposals
              <ArrowRight className="h-3 w-3 ml-1" />
            </Button>
          </Link>
        </div>

        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>PROPOSAL</TableHead>
              <TableHead>INSTITUTION</TableHead>
              <TableHead>DOMAIN</TableHead>
              <TableHead>SUBMITTED</TableHead>
              <TableHead>STATUS</TableHead>
              <TableHead>PRIORITY</TableHead>
              <TableHead className="text-right">ACTION</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {proposals.map((prop) => (
              <TableRow key={prop.id}>
                <TableCell className="font-medium text-slate-900">
                  <div className="max-w-md">
                    <Link
                      href={`/proposals/${prop.id}`}
                      className="hover:underline text-slate-900 font-semibold line-clamp-1"
                    >
                      {prop.title}
                    </Link>
                    <span className="text-[10px] font-mono text-slate-500 block mt-0.5">
                      {prop.id} • PI: {prop.principalInvestigator}
                    </span>
                  </div>
                </TableCell>
                <TableCell>
                  <span className="font-semibold text-slate-800">{prop.institution.name}</span>
                  <span className="text-[10px] text-slate-500 block">{prop.institution.location}</span>
                </TableCell>
                <TableCell className="text-slate-700 font-mono text-[11px]">
                  {prop.domain}
                </TableCell>
                <TableCell className="text-slate-600 font-mono text-[11px]">
                  {formatDate(prop.submittedDate)}
                </TableCell>
                <TableCell>{getStatusBadge(prop.status)}</TableCell>
                <TableCell>{getPriorityBadge(prop.priority)}</TableCell>
                <TableCell className="text-right">
                  <Link href={`/proposals/${prop.id}`}>
                    <Button variant="outline" size="sm" className="h-7 px-2.5 text-[11px]">
                      Workspace
                    </Button>
                  </Link>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
