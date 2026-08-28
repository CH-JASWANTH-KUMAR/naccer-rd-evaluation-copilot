import { Proposal } from "../types";
import { appConfig } from "../config";
import { SimilaritySearchResponse } from "./projects";

export interface ProposalCompletenessReport {
  proposalId: string;
  status: "COMPLETE" | "INCOMPLETE";
  missingFields: string[];
  warnings: string[];
  findings: Array<{
    field: string;
    severity: "ERROR" | "WARNING" | "INFO";
    message: string;
  }>;
}

export interface FinancialComplianceReport {
  proposalId: string;
  status: "COMPLIANT" | "FLAGGED" | "NEEDS_JUSTIFICATION";
  declaredTotal: number;
  calculatedTotal: number;
  arithmeticMismatch: boolean;
  differenceAmount: number;
  findings: Array<{
    costHead: string;
    proposedAmount: number;
    complianceStatus: string;
    notes?: string | null;
  }>;
}

export interface ProposalSourceProvenance {
  proposalId: string;
  proposalReference: string;
  title: string;
  documents: Array<{
    documentId: string;
    filename: string;
    fileSize: number;
    documentHash?: string | null;
    pageCount: number;
    storagePath: string;
    pages: Array<{
      pageNumber: number;
      characterCount: number;
      extractedText: string;
    }>;
  }>;
}

interface ApiProposal {
  id: string;
  proposal_reference: string;
  title: string;
  institution_id: string;
  institution?: { id: string; name: string; code: string; type: string; location: string };
  principal_investigator: string;
  domain: string;
  problem_statement?: string | null;
  objectives?: string | null;
  methodology?: string | null;
  technology?: string | null;
  expected_outcomes?: string | null;
  duration_months?: number | null;
  status: string;
  priority: string;
  budget_total: number;
  completeness_status: "COMPLETE" | "INCOMPLETE";
  compliance_status: "COMPLIANT" | "FLAGGED" | "NEEDS_JUSTIFICATION";
  processing_status: string;
  processing_error?: string | null;
  submission_date: string;
  created_at: string;
}

interface ApiSimilarityEvidence {
  field: string;
  snippet: string;
  reason: string;
  strength: "DIRECT_MATCH" | "RELATED" | "WEAKLY_RELATED";
}

interface ApiSimilarityProvenance {
  source: string;
  source_type: "OFFICIAL" | "PUBLIC" | "SYNTHETIC" | "MANUAL";
  source_url?: string | null;
  source_document_name?: string | null;
  source_page_start?: number | null;
  source_page_end?: number | null;
  source_record_identifier?: string | null;
  verification_status: "NEEDS_REVIEW" | "VERIFIED" | "REJECTED";
  verification_timestamp?: string | null;
}

interface ApiSimilarityItem {
  project_id: string;
  project_code: string;
  project_title: string;
  institution: string;
  domain: string;
  status: string;
  approved_cost: number;
  approved_cost_raw?: string | null;
  similarity_score: number;
  similarity_percentage: number;
  relationship: "POTENTIALLY_RELATED" | "CONCEPTUAL_OVERLAP" | "WEAK_RELATIONSHIP";
  matched_fields: string[];
  evidence: ApiSimilarityEvidence[];
  provenance: ApiSimilarityProvenance;
  summary?: string | null;
  raw_record_text?: string | null;
}

export const proposalService = {
  async getProposals(params?: {
    domain?: string;
    status?: string;
    completenessStatus?: string;
    complianceStatus?: string;
    search?: string;
  }): Promise<Proposal[]> {
    try {
      const query = new URLSearchParams();
      if (params?.domain) query.append("domain", params.domain);
      if (params?.status) query.append("status", params.status);
      if (params?.completenessStatus) query.append("completeness_status", params.completenessStatus);
      if (params?.complianceStatus) query.append("compliance_status", params.complianceStatus);
      if (params?.search) query.append("search", params.search);

      const res = await fetch(`${appConfig.apiBaseUrl}/proposals?${query.toString()}`, { cache: "no-store" });
      if (res.ok) {
        const list: ApiProposal[] = await res.json();
        return list.map((item) => proposalService._mapProposal(item));
      }
    } catch {
      // Fallback
    }
    return [];
  },

  async getProposalById(id: string): Promise<Proposal | null> {
    try {
      const res = await fetch(`${appConfig.apiBaseUrl}/proposals/${id}`, { cache: "no-store" });
      if (res.ok) {
        const item: ApiProposal = await res.json();
        return proposalService._mapProposal(item);
      }
    } catch {
      // Fallback
    }
    return null;
  },

  async uploadProposalPdf(formData: FormData): Promise<Proposal> {
    const res = await fetch(`${appConfig.apiBaseUrl}/proposals/upload`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      throw new Error(`Failed to upload proposal: ${res.statusText}`);
    }
    const item: ApiProposal = await res.json();
    return proposalService._mapProposal(item);
  },

  async getProposalSource(id: string): Promise<ProposalSourceProvenance | null> {
    try {
      const res = await fetch(`${appConfig.apiBaseUrl}/proposals/${id}/source`, { cache: "no-store" });
      if (res.ok) {
        return await res.json();
      }
    } catch {
      // Fallback
    }
    return null;
  },

  async getProposalCompleteness(id: string): Promise<ProposalCompletenessReport | null> {
    try {
      const res = await fetch(`${appConfig.apiBaseUrl}/proposals/${id}/completeness`, { cache: "no-store" });
      if (res.ok) {
        const raw = await res.json();
        return {
          proposalId: raw.proposal_id,
          status: raw.status,
          missingFields: raw.missing_fields || [],
          warnings: raw.warnings || [],
          findings: raw.findings || [],
        };
      }
    } catch {
      // Fallback
    }
    return null;
  },

  async getProposalCompliance(id: string): Promise<FinancialComplianceReport | null> {
    try {
      const res = await fetch(`${appConfig.apiBaseUrl}/proposals/${id}/compliance`, { cache: "no-store" });
      if (res.ok) {
        const raw = await res.json();
        return {
          proposalId: raw.proposal_id,
          status: raw.status,
          declaredTotal: raw.declared_total,
          calculatedTotal: raw.calculated_total,
          arithmeticMismatch: raw.arithmetic_mismatch,
          differenceAmount: raw.difference_amount,
          findings: raw.findings || [],
        };
      }
    } catch {
      // Fallback
    }
    return null;
  },

  async reprocessProposal(id: string): Promise<Proposal> {
    const res = await fetch(`${appConfig.apiBaseUrl}/proposals/${id}/reprocess`, {
      method: "POST",
    });
    if (!res.ok) throw new Error("Reprocess failed");
    const item: ApiProposal = await res.json();
    return proposalService._mapProposal(item);
  },

  async findSimilarProjectsForProposal(id: string, topK = 5): Promise<SimilaritySearchResponse> {
    const res = await fetch(`${appConfig.apiBaseUrl}/proposals/${id}/similar-projects?top_k=${topK}`, {
      method: "POST",
    });
    if (!res.ok) throw new Error("Similar projects search failed");
    const data = await res.json();
    return {
      querySummary: data.query_summary,
      totalCandidatesEvaluated: data.total_candidates_evaluated,
      resultsCount: data.results_count,
      disclaimer: data.disclaimer,
      results: ((data.results as ApiSimilarityItem[]) || []).map((item) => ({
        projectId: item.project_id,
        projectCode: item.project_code,
        projectTitle: item.project_title,
        institution: item.institution,
        domain: item.domain,
        status: item.status,
        approvedCost: item.approved_cost,
        approvedCostRaw: item.approved_cost_raw,
        similarityScore: item.similarity_score,
        similarityPercentage: item.similarity_percentage,
        relationship: item.relationship,
        matchedFields: item.matched_fields || [],
        evidence: (item.evidence || []).map((e) => ({
          field: e.field,
          snippet: e.snippet,
          reason: e.reason,
          strength: e.strength,
        })),
        provenance: {
          source: item.provenance.source,
          sourceType: item.provenance.source_type,
          sourceUrl: item.provenance.source_url,
          sourceDocumentName: item.provenance.source_document_name,
          sourcePageStart: item.provenance.source_page_start,
          sourcePageEnd: item.provenance.source_page_end,
          sourceRecordIdentifier: item.provenance.source_record_identifier,
          verificationStatus: item.provenance.verification_status,
          verificationTimestamp: item.provenance.verification_timestamp,
        },
        summary: item.summary,
        rawRecordText: item.raw_record_text,
      })),
    };
  },

  _mapProposal(item: ApiProposal): Proposal {
    return {
      id: item.id,
      title: item.title,
      institution: {
        id: item.institution?.id || item.institution_id,
        name: item.institution?.name || "CMPDI Submitting Institute",
        code: item.institution?.code || "CMPDI",
        type: "RESEARCH_INSTITUTE",
        location: "India",
      },
      principalInvestigator: item.principal_investigator,
      domain: item.domain,
      status: (item.status as unknown) as Proposal["status"],
      priority: (item.priority as unknown) as Proposal["priority"],
      submittedDate: item.submission_date || item.created_at,
      submissionDate: item.submission_date || item.created_at,
      proposedBudget: item.budget_total || 0,
      budgetTotal: item.budget_total || 0,
      proposalReference: item.proposal_reference || `PR-2026-${item.id.slice(0, 6)}`,
      summary: item.objectives || item.problem_statement || item.title,
      problemStatement: item.problem_statement || undefined,
      objectives: item.objectives || undefined,
      methodology: item.methodology || undefined,
      technology: item.technology || undefined,
      expectedOutcomes: item.expected_outcomes || undefined,
      durationMonths: item.duration_months || 12,
      completenessStatus: item.completeness_status || "INCOMPLETE",
      complianceStatus: item.compliance_status || "COMPLIANT",
      processingStatus: item.processing_status || "UPLOADED",
      processingError: item.processing_error || undefined,
      keywords: [item.domain],
    };
  },
};
