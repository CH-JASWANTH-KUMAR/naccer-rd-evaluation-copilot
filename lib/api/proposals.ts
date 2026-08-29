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
  status: "COMPLIANT" | "FLAGGED" | "NEEDS_JUSTIFICATION" | string;
  declaredTotal: number;
  calculatedTotal: number | null;
  arithmeticStatus: "MATCH" | "MISMATCH" | "NOT_VERIFIABLE" | string;
  varianceAmount: number | null;
  extractionSummaryStatus: "FULL_BREAKDOWN" | "PARTIAL_BREAKDOWN" | "MISSING_BREAKDOWN" | string;
  explanation: string;
  arithmeticMismatch: boolean;
  differenceAmount: number;
  findings: Array<{
    costHead: string;
    proposedAmount: number;
    normalizedAmount?: number | null;
    rawAmountString?: string | null;
    complianceStatus: string;
    sourcePage?: number | null;
    extractionStatus?: string | null;
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

export interface ScientificComparisonRecord {
  comparisonId: string;
  dimension: string;
  proposalField: string;
  proposalValue: string;
  evidenceSourceType: string;
  evidenceSourceId: string;
  evidenceValue: string;
  comparisonStatus: "MATCHING" | "PARTIALLY_MATCHING" | "DIFFERENT" | "NOT_REPORTED" | "NOT_COMPARABLE" | "UNRESOLVED" | "CONFLICTING_EVIDENCE";
  explanation: string;
  sourcePageStart?: number | null;
  sourcePageEnd?: number | null;
  evidenceId: string;
  confidence: string;
}

export interface EvidenceGapRecord {
  dimension: string;
  gap: string;
  reviewerAction: string;
  evidenceSupportingGap: string;
}

export interface ReviewerQuestionRecord {
  questionId: string;
  dimension: string;
  question: string;
  evidenceId: string;
  rationale: string;
}

export interface EvidenceSourceSummary {
  sourceType: string;
  evidenceId: string;
  title: string;
  relevanceScore: number;
  matchedDimensions: string[];
}

export interface ProposalScientificComparisonResponse {
  proposalId: string;
  comparisonSummary: Record<string, number>;
  comparisons: ScientificComparisonRecord[];
  evidenceGaps: EvidenceGapRecord[];
  reviewerQuestions: ReviewerQuestionRecord[];
  evidenceSources: EvidenceSourceSummary[];
}

interface ApiProposal {
  id: string;
  proposal_reference: string;
  title: string;
  institution_id: string;
  institution?: { id: string; name: string; code: string; type: string; location: string };
  principal_investigator: string;
  extracted_principal_investigator?: string | null;
  domain: string;
  problem_statement?: string | null;
  objectives?: string | null;
  methodology?: string | null;
  technology?: string | null;
  expected_outcomes?: string | null;
  duration_months?: number | null;
  status: string;
  priority: string;
  budget_total?: number | null;
  raw_budget_text?: string | null;
  completeness_status: "COMPLETE" | "INCOMPLETE";
  compliance_status: "COMPLIANT" | "FLAGGED" | "NEEDS_JUSTIFICATION";
  processing_status: string;
  processing_error?: string | null;
  document_type?: string | null;
  document_type_confidence?: string | null;
  document_type_reasons?: string[] | null;
  structured_sections?: Record<string, unknown>[] | null;
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
  evidence_id?: string;
  project_title: string;
  institution: string;
  sub_implementing_agencies?: string | null;
  domain: string;
  status: string;
  approved_cost: number;
  approved_cost_raw?: string | null;
  similarity_score: number;
  similarity_percentage: number;
  relationship: "POTENTIALLY_RELATED" | "CONCEPTUAL_OVERLAP" | "WEAK_RELATIONSHIP";
  matched_fields: string[];
  matched_dimensions?: string[];
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
      if (!res.ok) return null;
      const item: ApiProposal = await res.json();
      return proposalService._mapProposal(item);
    } catch {
      return null;
    }
  },

  async uploadProposalPdf(formData: FormData): Promise<Proposal> {
    const res = await fetch(`${appConfig.apiBaseUrl}/proposals/upload`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => null);
      throw new Error(err?.detail || `Upload failed with status ${res.status}`);
    }
    const item: ApiProposal = await res.json();
    return proposalService._mapProposal(item);
  },

  async getProposalCompleteness(id: string): Promise<ProposalCompletenessReport | null> {
    try {
      const res = await fetch(`${appConfig.apiBaseUrl}/proposals/${id}/completeness`, { cache: "no-store" });
      if (!res.ok) return null;
      const data = await res.json();
      return {
        proposalId: data.proposal_id || id,
        status: data.status,
        missingFields: data.missing_fields || [],
        warnings: data.warnings || [],
        findings: (data.findings || []).map((f: Record<string, unknown>) => ({
          field: f.field as string,
          severity: f.severity as "ERROR" | "WARNING" | "INFO",
          message: f.message as string,
        })),
      };
    } catch {
      return null;
    }
  },

  async getProposalCompliance(id: string): Promise<FinancialComplianceReport | null> {
    try {
      const res = await fetch(`${appConfig.apiBaseUrl}/proposals/${id}/compliance`, { cache: "no-store" });
      if (!res.ok) return null;
      const data = await res.json();
      return {
        proposalId: data.proposal_id || id,
        status: data.status,
        declaredTotal: data.declared_total ?? 0,
        calculatedTotal: data.calculated_total !== undefined && data.calculated_total !== null ? data.calculated_total : null,
        arithmeticStatus: data.arithmetic_status || (data.arithmetic_mismatch ? "MISMATCH" : "MATCH"),
        varianceAmount: data.variance_amount !== undefined && data.variance_amount !== null ? data.variance_amount : null,
        extractionSummaryStatus: data.extraction_summary_status || "FULL_BREAKDOWN",
        explanation: data.explanation || "",
        arithmeticMismatch: data.arithmetic_mismatch || false,
        differenceAmount: data.difference_amount || 0,
        findings: (data.findings || []).map((f: Record<string, unknown>) => ({
          costHead: f.cost_head as string,
          proposedAmount: f.proposed_amount as number,
          normalizedAmount: f.normalized_amount as number | undefined,
          rawAmountString: (f.raw_amount_string as string) || undefined,
          complianceStatus: (f.compliance_status as string) || "COMPLIANT",
          sourcePage: (f.source_page as number) || undefined,
          extractionStatus: (f.extraction_status as string) || "EXTRACTED",
          notes: (f.notes as string) || undefined,
        })),
      };
    } catch {
      return null;
    }
  },

  async getProposalSource(id: string): Promise<ProposalSourceProvenance | null> {
    try {
      const res = await fetch(`${appConfig.apiBaseUrl}/proposals/${id}/source`, { cache: "no-store" });
      if (!res.ok) return null;
      const data = await res.json();
      return {
        proposalId: data.proposal_id || id,
        proposalReference: data.proposal_reference || "",
        title: data.title || "",
        documents: (data.documents || []).map((d: Record<string, unknown>) => ({
          documentId: d.document_id as string,
          filename: d.filename as string,
          fileSize: d.file_size as number,
          documentHash: (d.document_hash as string) || null,
          pageCount: d.page_count as number,
          storagePath: d.storage_path as string,
          pages: ((d.pages as Record<string, unknown>[]) || []).map((p) => ({
            pageNumber: p.page_number as number,
            characterCount: p.character_count as number,
            extractedText: (p.extracted_text as string) || "",
          })),
        })),
      };
    } catch {
      return null;
    }
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
        evidenceId: item.evidence_id || "HIST-000",
        projectTitle: item.project_title,
        institution: item.institution,
        subImplementingAgencies: item.sub_implementing_agencies || null,
        domain: item.domain,
        status: item.status,
        approvedCost: item.approved_cost,
        approvedCostRaw: item.approved_cost_raw,
        similarityScore: item.similarity_score,
        similarityPercentage: item.similarity_percentage,
        relationship: item.relationship,
        matchedFields: item.matched_fields || [],
        matchedDimensions: item.matched_dimensions || [],
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

  async getScientificComparison(proposalId: string): Promise<ProposalScientificComparisonResponse> {
    const res = await fetch(`${appConfig.apiBaseUrl}/proposals/${proposalId}/scientific-comparison`, {
      cache: "no-store",
    });
    if (!res.ok) throw new Error("Failed to load scientific comparison");
    const data = await res.json();
    return {
      proposalId: data.proposal_id,
      comparisonSummary: data.comparison_summary || {},
      comparisons: (data.comparisons || []).map((c: Record<string, unknown>) => ({
        comparisonId: c.comparison_id as string,
        dimension: c.dimension as string,
        proposalField: c.proposal_field as string,
        proposalValue: c.proposal_value as string,
        evidenceSourceType: c.evidence_source_type as string,
        evidenceSourceId: c.evidence_source_id as string,
        evidenceValue: c.evidence_value as string,
        comparisonStatus: c.comparison_status as ScientificComparisonRecord["comparisonStatus"],
        explanation: c.explanation as string,
        sourcePageStart: (c.source_page_start as number) || null,
        sourcePageEnd: (c.source_page_end as number) || null,
        evidenceId: c.evidence_id as string,
        confidence: (c.confidence as string) || "HIGH",
      })),
      evidenceGaps: (data.evidence_gaps || []).map((g: Record<string, unknown>) => ({
        dimension: g.dimension as string,
        gap: g.gap as string,
        reviewerAction: g.reviewer_action as string,
        evidenceSupportingGap: g.evidence_supporting_gap as string,
      })),
      reviewerQuestions: (data.reviewer_questions || []).map((q: Record<string, unknown>) => ({
        questionId: q.question_id as string,
        dimension: q.dimension as string,
        question: q.question as string,
        evidenceId: q.evidence_id as string,
        rationale: q.rationale as string,
      })),
      evidenceSources: (data.evidence_sources || []).map((s: Record<string, unknown>) => ({
        sourceType: s.source_type as string,
        evidenceId: s.evidence_id as string,
        title: s.title as string,
        relevanceScore: s.relevance_score as number,
        matchedDimensions: (s.matched_dimensions as string[]) || [],
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
      extractedPrincipalInvestigator: item.extracted_principal_investigator,
      domain: item.domain,
      status: (item.status as unknown) as Proposal["status"],
      priority: (item.priority as unknown) as Proposal["priority"],
      submittedDate: item.submission_date || item.created_at,
      submissionDate: item.submission_date || item.created_at,
      proposedBudget: item.budget_total,
      budgetTotal: item.budget_total,
      rawBudgetText: item.raw_budget_text,
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
      documentType: item.document_type || "R&D_PROPOSAL",
      documentTypeConfidence: item.document_type_confidence || "HIGH",
      documentTypeReasons: item.document_type_reasons || [],
      structuredSections: (item.structured_sections || []).map((s: Record<string, unknown>) => ({
        key: s.key as string,
        displayTitle: s.display_title as string,
        content: s.content as string,
        summary: s.summary as string,
        status: s.status as string,
        sourcePageStart: s.source_page_start as number,
        sourcePageEnd: s.source_page_end as number,
        extractionConfidence: s.extraction_confidence as string,
        evidenceId: s.evidence_id as string,
      })),
      keywords: [item.domain],
    };
  },
};
