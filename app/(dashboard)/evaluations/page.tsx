import React from "react";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { proposalService } from "@/lib/api/proposals";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";

export default async function EvaluationsListPage() {
  const proposals = await proposalService.getProposals();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">
            Technical Evaluation Workspaces
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Active reviewer scoring sheets and compliance check panels for R&amp;D proposals.
          </p>
        </div>
      </div>

      {/* Evaluations List Table */}
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>PROPOSAL ID</TableHead>
            <TableHead>PROPOSAL TITLE</TableHead>
            <TableHead>INSTITUTION</TableHead>
            <TableHead>STATUS</TableHead>
            <TableHead className="text-right">EVALUATION WORKSPACE</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {proposals.map((prop) => (
            <TableRow key={prop.id}>
              <TableCell className="font-mono text-xs font-bold text-slate-800">
                {prop.id}
              </TableCell>
              <TableCell>
                <Link
                  href={`/evaluations/${prop.id}`}
                  className="font-semibold text-slate-900 hover:underline line-clamp-1 max-w-md"
                >
                  {prop.title}
                </Link>
                <span className="text-[10px] text-slate-500 block font-mono">PI: {prop.principalInvestigator}</span>
              </TableCell>
              <TableCell className="font-medium text-slate-800">
                {prop.institution.name}
              </TableCell>
              <TableCell>
                <Badge variant="info">Workstation Draft</Badge>
              </TableCell>
              <TableCell className="text-right">
                <Link href={`/evaluations/${prop.id}`}>
                  <Button size="sm" className="h-7 text-xs">
                    Launch Rubric Workspace
                    <ArrowRight className="h-3 w-3 ml-1" />
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
