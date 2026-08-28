import React from "react";
import Link from "next/link";
import { notFound } from "next/navigation";
import {
  Building,
  Calendar,
  IndianRupee,
  User,
  History,
} from "lucide-react";
import { proposalService } from "@/lib/api/proposals";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { ModulePlaceholder } from "@/components/shared/ModulePlaceholder";
import { ProposalDocumentViewer } from "@/components/proposal/ProposalDocumentViewer";
import { formatCurrency, formatDate } from "@/lib/utils";

interface ProposalDetailPageProps {
  params: Promise<{ id: string }>;
}

export default async function ProposalDetailPage({ params }: ProposalDetailPageProps) {
  const { id } = await params;
  const proposal = await proposalService.getProposalById(id);

  if (!proposal) {
    notFound();
  }

  return (
    <div className="space-y-6">
      {/* Top Header Card */}
      <Card className="bg-white border-slate-200">
        <CardContent className="p-6">
          <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
            <div className="space-y-2 max-w-3xl">
              <div className="flex items-center space-x-2">
                <Badge variant="outline" className="font-mono text-xs bg-slate-100">
                  {proposal.id}
                </Badge>
                <Badge variant="info" className="text-xs">
                  {proposal.status.replace("_", " ")}
                </Badge>
                <Badge variant="secondary" className="text-xs">
                  {proposal.domain}
                </Badge>
              </div>
              <h1 className="text-lg font-bold text-slate-900 leading-snug">{proposal.title}</h1>
              <div className="flex flex-wrap items-center gap-4 text-xs text-slate-600 font-medium">
                <span className="flex items-center">
                  <Building className="h-3.5 w-3.5 mr-1 text-slate-400" />
                  {proposal.institution.name} ({proposal.institution.code})
                </span>
                <span className="flex items-center">
                  <User className="h-3.5 w-3.5 mr-1 text-slate-400" />
                  PI: {proposal.principalInvestigator}
                </span>
                <span className="flex items-center">
                  <Calendar className="h-3.5 w-3.5 mr-1 text-slate-400" />
                  Submitted: {formatDate(proposal.submittedDate)}
                </span>
                <span className="flex items-center font-mono font-bold text-slate-900">
                  <IndianRupee className="h-3.5 w-3.5 mr-0.5 text-slate-500" />
                  {formatCurrency(proposal.proposedBudget)}
                </span>
              </div>
            </div>

            <div className="flex items-center space-x-2 flex-shrink-0">
              <Link href={`/evaluations/${proposal.id}`}>
                <Button size="sm">Evaluate Proposal</Button>
              </Link>
              <Link href={`/reports?id=${proposal.id}`}>
                <Button variant="outline" size="sm">
                  View Report
                </Button>
              </Link>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 9 Workspaces Tabs Navigation */}
      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="bg-slate-200/60 p-1 border border-slate-300">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="document">Proposal Document</TabsTrigger>
          <TabsTrigger value="completeness">Completeness</TabsTrigger>
          <TabsTrigger value="financial">Financial</TabsTrigger>
          <TabsTrigger value="benchmark">Historical Benchmark</TabsTrigger>
          <TabsTrigger value="novelty">Novelty</TabsTrigger>
          <TabsTrigger value="evaluation">Evaluation</TabsTrigger>
          <TabsTrigger value="evidence">Evidence</TabsTrigger>
          <TabsTrigger value="history">Review History</TabsTrigger>
        </TabsList>

        {/* Tab 1: Overview */}
        <TabsContent value="overview">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Executive Proposal Summary</CardTitle>
              <CardDescription>Structured submission details &amp; key parameters.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-xs text-slate-700 leading-relaxed bg-slate-50 p-4 rounded-md border border-slate-200">
                {proposal.summary}
              </p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
                <div className="border border-slate-200 rounded-md p-3 bg-white">
                  <span className="text-[10px] font-mono text-slate-500 uppercase block">Duration</span>
                  <span className="text-sm font-bold text-slate-900">{proposal.durationMonths} Months</span>
                </div>
                <div className="border border-slate-200 rounded-md p-3 bg-white">
                  <span className="text-[10px] font-mono text-slate-500 uppercase block">Institution Type</span>
                  <span className="text-sm font-bold text-slate-900">{proposal.institution.type}</span>
                </div>
                <div className="border border-slate-200 rounded-md p-3 bg-white">
                  <span className="text-[10px] font-mono text-slate-500 uppercase block">Keywords</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {proposal.keywords.map((kw) => (
                      <Badge key={kw} variant="secondary" className="text-[10px]">
                        {kw}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab 2: Proposal Document */}
        <TabsContent value="document">
          <ProposalDocumentViewer proposalId={proposal.id} />
        </TabsContent>

        {/* Tab 3: Completeness */}
        <TabsContent value="completeness">
          <ModulePlaceholder
            moduleName="Proposal Completeness & Compliance Engine"
            phase="P0"
            description="Automated evaluation of proposal structure, required attachments, clearance certificates, and PI eligibility."
            plannedFeatures={[
              "Check presence of mandatory DST / NaCCER forms",
              "Verify Ethical Clearance & Environmental No-Objection certificates",
              "Validate Principal Investigator eligibility criteria",
            ]}
          />
        </TabsContent>

        {/* Tab 4: Financial */}
        <TabsContent value="financial">
          <ModulePlaceholder
            moduleName="Financial Compliance & Cost Head Checking"
            phase="P0"
            description="Automated breakdown of equipment, manpower, consumables, and travel costs against standard NaCCER expenditure norms."
            plannedFeatures={[
              "Identify equipment cost inflation versus market baseline",
              "Validate Senior Research Fellow (SRF/JRF) fellowship rates",
              "Flag overhead and contingency fund allocation anomalies",
            ]}
          />
        </TabsContent>

        {/* Tab 5: Historical Benchmark */}
        <TabsContent value="benchmark">
          <ModulePlaceholder
            moduleName="Historical R&D Project Benchmarking"
            phase="P0"
            description="Dense vector similarity search against 15+ years of prior Coal India / NaCCER funded projects."
            plannedFeatures={[
              "Semantic matching of technical methodologies with prior deliverables",
              "PI past project completion track record verification",
              "Overlap detection with completed and active CIL projects",
            ]}
          />
        </TabsContent>

        {/* Tab 6: Novelty */}
        <TabsContent value="novelty">
          <ModulePlaceholder
            moduleName="Evidence-Based Novelty Analysis"
            phase="P0"
            description="Deep NLP similarity & novelty assessment against global scientific literature and national patents."
            plannedFeatures={[
              "Calculate objective novelty distance score",
              "Extract claims and cross-check against prior literature",
              "Generate citation-backed novelty evidence summary",
            ]}
          />
        </TabsContent>

        {/* Tab 7: Evaluation */}
        <TabsContent value="evaluation">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Technical Review Rubric Workspace</CardTitle>
              <CardDescription>
                Reviewer workspace for manual scoring and AI finding verification.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between p-4 bg-slate-100 rounded-md border border-slate-200 mb-4">
                <div>
                  <p className="text-xs font-semibold text-slate-800">
                    Evaluation Workspace Ready
                  </p>
                  <p className="text-[11px] text-slate-600">
                    Configure criterion scores and reviewer decision in the dedicated workspace.
                  </p>
                </div>
                <Link href={`/evaluations/${proposal.id}`}>
                  <Button size="sm">Launch Evaluation Workspace</Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab 8: Evidence */}
        <TabsContent value="evidence">
          <ModulePlaceholder
            moduleName="Evidence & Citation Repository"
            phase="P0"
            description="Consolidated index of extracted text snippets, document page references, and similarity benchmarks."
            plannedFeatures={[
              "Traceable page-number citations to source PDF pages",
              "Confidence scores for AI-assisted findings",
              "Reviewer snippet bookmarking & annotation log",
            ]}
          />
        </TabsContent>

        {/* Tab 9: Review History */}
        <TabsContent value="history">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Audit Trail &amp; Review History</CardTitle>
              <CardDescription>
                Chronological log of reviewer actions, score updates, and system events.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-start space-x-3 p-3 bg-slate-50 rounded-md border border-slate-200">
                  <History className="h-4 w-4 text-slate-500 mt-0.5" />
                  <div>
                    <p className="text-xs font-semibold text-slate-800">Proposal Created &amp; Ingested</p>
                    <p className="text-[11px] text-slate-500">System • {formatDate(proposal.submittedDate)}</p>
                    <p className="text-xs text-slate-600 mt-1">
                      Base proposal record created in system directory.
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
