// Core Domain Entities for NaCCER R&D Evaluation Copilot

export type ProposalStatus =
  | "UNDER_REVIEW"
  | "AWAITING_REVIEW"
  | "POTENTIAL_ISSUES"
  | "COMPLETED"
  | "REJECTED"
  | "READY_FOR_REVIEW"
  | "INCOMPLETE"
  | "UPLOADED";

export type ProposalPriority = "HIGH" | "MEDIUM" | "LOW";

export interface Institution {
  id: string;
  name: string;
  code: string;
  type: "ACADEMIC" | "RESEARCH_INSTITUTE" | "INDUSTRY" | "GOVERNMENT";
  location: string;
}

export interface Proposal {
  id: string;
  proposalReference?: string;
  title: string;
  institution: Institution;
  domain: string;
  principalInvestigator: string;
  extractedPrincipalInvestigator?: string | null;
  submittedDate: string;
  submissionDate?: string;
  status: ProposalStatus;
  priority: ProposalPriority;
  proposedBudget?: number | null;
  budgetTotal?: number | null;
  rawBudgetText?: string | null;
  durationMonths: number;
  summary: string;
  problemStatement?: string;
  objectives?: string;
  methodology?: string;
  technology?: string;
  expectedOutcomes?: string;
  completenessStatus?: "COMPLETE" | "INCOMPLETE";
  complianceStatus?: "COMPLIANT" | "FLAGGED" | "NEEDS_JUSTIFICATION";
  processingStatus?: string;
  processingError?: string;
  documentUrl?: string;
  keywords: string[];
}

export interface HistoricalProject {
  id: string;
  projectCode: string;
  title: string;
  institution: Institution;
  subImplementingAgencies?: string | null;
  domain: string;
  principalInvestigator: string;
  status: "COMPLETED" | "ONGOING" | "TERMINATED" | "NEEDS_REVIEW";
  completionYear: number;
  totalCost: number;
  approvedCostRaw?: string | null;
  technologyStack: string[];
  summary: string;
  source: string;
  sourceType: "OFFICIAL" | "PUBLIC" | "SYNTHETIC" | "MANUAL";
  sourceUrl?: string | null;
  sourceDocumentName?: string | null;
  sourcePageStart?: number | null;
  sourcePageEnd?: number | null;
  rawRecordText?: string | null;
  verificationStatus: "NEEDS_REVIEW" | "VERIFIED" | "REJECTED";
  verificationTimestamp?: string | null;
  similarityScore?: number; // Benchmarking score placeholder
}

export type CriterionCategory =
  | "NOVELTY"
  | "METHODOLOGY"
  | "FINANCIAL"
  | "FEASIBILITY"
  | "COMPLIANCE";

export interface EvaluationCriterion {
  id: string;
  title: string;
  description: string;
  category: CriterionCategory;
  weight: number;
  maxScore: number;
  assignedScore?: number;
  findingsPlaceholder?: string;
  reviewerNotes?: string;
}

export interface Evidence {
  id: string;
  sourceDocument: string;
  pageNumber: number;
  extractedSnippet: string;
  relevanceDescription: string;
  confidenceScore?: number;
}

export interface FinancialCheck {
  id: string;
  costHead: string;
  proposedAmount: number;
  benchmarkAmount?: number;
  complianceStatus: "COMPLIANT" | "FLAGGED" | "NEEDS_JUSTIFICATION";
  notes: string;
}

export interface ReviewComment {
  id: string;
  proposalId: string;
  authorName: string;
  authorRole: string;
  content: string;
  createdAt: string;
  isInternal: boolean;
}

export interface AuditEvent {
  id: string;
  proposalId: string;
  action: string;
  performedBy: string;
  timestamp: string;
  details: string;
}

export interface Evaluation {
  id: string;
  proposalId: string;
  evaluatorId: string;
  evaluatorName: string;
  overallStatus: "DRAFT" | "SUBMITTED" | "FINALIZED";
  overallScore?: number;
  criteria: EvaluationCriterion[];
  financialChecks: FinancialCheck[];
  evidences: Evidence[];
  updatedAt: string;
}
