import { Proposal } from "../types";
import { appConfig } from "../config";
import { proposalService } from "./proposals";

export interface EvaluationCriterion {
  id: string;
  criterionKey?: string | null;
  name: string;
  description?: string | null;
  maxScore: number;
  weight: number;
  score?: number | null;
  weightedScore?: number | null;
  comments?: string | null;
  justificationNotes?: string | null;
}

export interface EvaluationEvidenceItem {
  id: string;
  evaluationId: string;
  criterionId?: string | null;
  evidenceType: string;
  sourceType: string;
  sourceReference?: string | null;
  sourcePageStart?: number | null;
  sourcePageEnd?: number | null;
  evidenceText: string;
  reviewerNote?: string | null;
  createdAt: string;
}

export interface EvaluationDetail {
  id: string;
  proposalId: string;
  reviewerId: string;
  rubricId?: string | null;
  rubricVersion: string;
  status: "DRAFT" | "SUBMITTED" | "RETURNED_FOR_REVISION";
  overallScore?: number | null;
  reviewerSummary?: string | null;
  reviewerRecommendation: "FAVORABLE" | "FAVORABLE_WITH_CONDITIONS" | "REQUIRES_REVISION" | "NOT_RECOMMENDED";
  startedAt: string;
  completedAt?: string | null;
  createdAt: string;
  proposal?: Proposal;
  criteria: EvaluationCriterion[];
  evidences: EvaluationEvidenceItem[];
}

export interface AIAnalysisResult {
  overallObservation: string;
  criterionAnalysis: Array<{
    criterionKey: string;
    criterionName: string;
    observation: string;
    supportingEvidence: Array<{
      sourceType: string;
      sourceReference: string;
      pageStart?: number | null;
      pageEnd?: number | null;
      evidenceText: string;
    }>;
    evidenceGaps: string[];
    reviewerQuestions: string[];
  }>;
  strengths: Array<{
    title: string;
    description: string;
    supportingEvidence: Array<{
      sourceType: string;
      sourceReference: string;
      evidenceText: string;
    }>;
  }>;
  concerns: Array<{
    title: string;
    description: string;
    supportingEvidence: Array<{
      sourceType: string;
      sourceReference: string;
      evidenceText: string;
    }>;
  }>;
  evidenceGaps: Array<{
    criterionKey: string;
    gapDescription: string;
    impact: string;
    reviewerAction: string;
  }>;
  reviewerQuestions: Array<{
    criterionKey: string;
    question: string;
    rationale: string;
  }>;
  contradictions: Array<{
    fieldA: string;
    fieldB: string;
    observation: string;
    severity: string;
  }>;
  disclaimer: string;
}

export interface AIAnalysisRead {
  id: string;
  evaluationId: string;
  provider: string;
  model: string;
  promptVersion: string;
  inputHash: string;
  status: string;
  createdAt: string;
  analysisResult: AIAnalysisResult;
}

export interface EvaluationRubric {
  id: string;
  name: string;
  version: string;
  description?: string | null;
  isActive: boolean;
  criteria: Array<{
    id: string;
    key: string;
    name: string;
    description: string;
    category: string;
    maxScore: number;
    weight: number;
    displayOrder: number;
    required: boolean;
    evidenceRequired: boolean;
  }>;
}

interface ApiEvaluationCriterion {
  id: string;
  criterion_key?: string | null;
  name: string;
  description?: string | null;
  max_score: number;
  weight: number;
  score?: number | null;
  weighted_score?: number | null;
  comments?: string | null;
  justification_notes?: string | null;
}

interface ApiEvaluationEvidence {
  id: string;
  evaluation_id: string;
  criterion_id?: string | null;
  evidence_type: string;
  source_type: string;
  source_reference?: string | null;
  source_page_start?: number | null;
  source_page_end?: number | null;
  evidence_text: string;
  reviewer_note?: string | null;
  created_at: string;
}

interface ApiEvaluationDetail {
  id: string;
  proposal_id: string;
  reviewer_id: string;
  rubric_id?: string | null;
  rubric_version: string;
  status: "DRAFT" | "SUBMITTED" | "RETURNED_FOR_REVISION";
  overall_score?: number | null;
  reviewer_summary?: string | null;
  reviewer_recommendation: "FAVORABLE" | "FAVORABLE_WITH_CONDITIONS" | "REQUIRES_REVISION" | "NOT_RECOMMENDED";
  started_at: string;
  completed_at?: string | null;
  created_at: string;
  proposal?: Proposal;
  criteria?: ApiEvaluationCriterion[];
  evidences?: ApiEvaluationEvidence[];
}

export const evaluationService = {
  async getEvaluations(params?: { proposalId?: string; status?: string }): Promise<EvaluationDetail[]> {
    try {
      const query = new URLSearchParams();
      if (params?.proposalId) query.append("proposal_id", params.proposalId);
      if (params?.status) query.append("status", params.status);

      const res = await fetch(`${appConfig.apiBaseUrl}/evaluations?${query.toString()}`, { cache: "no-store" });
      if (res.ok) {
        const list: ApiEvaluationDetail[] = await res.json();
        return list.map((item) => evaluationService._mapEvaluation(item));
      }
    } catch {
      // Fallback
    }
    return [];
  },

  async getEvaluationById(id: string): Promise<EvaluationDetail | null> {
    try {
      const res = await fetch(`${appConfig.apiBaseUrl}/evaluations/${id}`, { cache: "no-store" });
      if (res.ok) {
        const item: ApiEvaluationDetail = await res.json();
        return evaluationService._mapEvaluation(item);
      }
    } catch {
      // Fallback
    }
    return null;
  },

  async createEvaluation(proposalId: string, reviewerId = "Dr. S. K. Singh"): Promise<EvaluationDetail> {
    const res = await fetch(`${appConfig.apiBaseUrl}/evaluations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ proposal_id: proposalId, reviewer_id: reviewerId }),
    });
    if (!res.ok) {
      throw new Error(`Failed to create evaluation: ${res.statusText}`);
    }
    const item: ApiEvaluationDetail = await res.json();
    return evaluationService._mapEvaluation(item);
  },

  async updateEvaluationDraft(
    id: string,
    payload: {
      reviewerSummary?: string;
      reviewerRecommendation?: string;
      criteria?: Array<{ id: string; score?: number | null; comments?: string | null; justificationNotes?: string | null }>;
    }
  ): Promise<EvaluationDetail> {
    const body: Record<string, unknown> = {};
    if (payload.reviewerSummary !== undefined) body.reviewer_summary = payload.reviewerSummary;
    if (payload.reviewerRecommendation !== undefined) body.reviewer_recommendation = payload.reviewerRecommendation;
    if (payload.criteria) {
      body.criteria = payload.criteria.map((c) => ({
        id: c.id,
        score: c.score,
        comments: c.comments,
        justification_notes: c.justificationNotes,
      }));
    }

    const res = await fetch(`${appConfig.apiBaseUrl}/evaluations/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error("Failed to update evaluation draft");
    const item: ApiEvaluationDetail = await res.json();
    return evaluationService._mapEvaluation(item);
  },

  async submitEvaluation(id: string): Promise<EvaluationDetail> {
    const res = await fetch(`${appConfig.apiBaseUrl}/evaluations/${id}/submit`, {
      method: "POST",
    });
    if (!res.ok) {
      const err = await res.json().catch(() => null);
      throw new Error(err?.detail || "Failed to submit evaluation.");
    }
    const item: ApiEvaluationDetail = await res.json();
    return evaluationService._mapEvaluation(item);
  },

  async addEvaluationEvidence(
    id: string,
    payload: {
      criterionId?: string | null;
      evidenceType: string;
      sourceType: string;
      sourceReference?: string | null;
      sourcePageStart?: number | null;
      sourcePageEnd?: number | null;
      evidenceText: string;
      reviewerNote?: string | null;
    }
  ): Promise<EvaluationDetail> {
    const res = await fetch(`${appConfig.apiBaseUrl}/evaluations/${id}/evidence`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        criterion_id: payload.criterionId,
        evidence_type: payload.evidenceType,
        source_type: payload.sourceType,
        source_reference: payload.sourceReference,
        source_page_start: payload.sourcePageStart,
        source_page_end: payload.sourcePageEnd,
        evidence_text: payload.evidenceText,
        reviewer_note: payload.reviewerNote,
      }),
    });
    if (!res.ok) throw new Error("Failed to add reviewer evidence");
    const item: ApiEvaluationDetail = await res.json();
    return evaluationService._mapEvaluation(item);
  },

  async generateDraftSummary(id: string): Promise<string> {
    const res = await fetch(`${appConfig.apiBaseUrl}/evaluations/${id}/summary`, { method: "POST" });
    if (!res.ok) throw new Error("Failed to generate summary");
    const data = await res.json();
    return data.draft_summary;
  },

  async getActiveRubric(): Promise<EvaluationRubric | null> {
    try {
      const res = await fetch(`${appConfig.apiBaseUrl}/rubrics/active`, { cache: "no-store" });
      if (res.ok) {
        const raw = await res.json();
        return {
          id: raw.id,
          name: raw.name,
          version: raw.version,
          description: raw.description,
          isActive: raw.is_active,
          criteria: (raw.criteria || []).map((c: Record<string, unknown>) => ({
            id: c.id as string,
            key: c.key as string,
            name: c.name as string,
            description: c.description as string,
            category: c.category as string,
            maxScore: c.max_score as number,
            weight: c.weight as number,
            displayOrder: c.display_order as number,
            required: c.required as boolean,
            evidenceRequired: c.evidence_required as boolean,
          })),
        };
      }
    } catch {
      // Fallback
    }
    return null;
  },

  async generateAIAnalysis(evaluationId: string): Promise<AIAnalysisRead> {
    const res = await fetch(`${appConfig.apiBaseUrl}/evaluations/${evaluationId}/ai-analysis`, {
      method: "POST",
    });
    if (!res.ok) throw new Error("Failed to generate AI analysis");
    const raw = await res.json();
    return evaluationService._mapAIAnalysis(raw);
  },

  async refreshAIAnalysis(evaluationId: string): Promise<AIAnalysisRead> {
    const res = await fetch(`${appConfig.apiBaseUrl}/evaluations/${evaluationId}/ai-analysis/refresh`, {
      method: "POST",
    });
    if (!res.ok) throw new Error("Failed to refresh AI analysis");
    const raw = await res.json();
    return evaluationService._mapAIAnalysis(raw);
  },

  _mapAIAnalysis(raw: Record<string, unknown>): AIAnalysisRead {
    const res = (raw.analysis_result || {}) as Record<string, unknown>;
    return {
      id: raw.id as string,
      evaluationId: raw.evaluation_id as string,
      provider: raw.provider as string,
      model: raw.model as string,
      promptVersion: raw.prompt_version as string,
      inputHash: raw.input_hash as string,
      status: raw.status as string,
      createdAt: raw.created_at as string,
      analysisResult: {
        overallObservation: (res.overall_observation as string) || "",
        criterionAnalysis: ((res.criterion_analysis as Record<string, unknown>[]) || []).map((ca) => ({
          criterionKey: ca.criterion_key as string,
          criterionName: ca.criterion_name as string,
          observation: ca.observation as string,
          supportingEvidence: ((ca.supporting_evidence as Record<string, unknown>[]) || []).map((e) => ({
            sourceType: e.source_type as string,
            sourceReference: e.source_reference as string,
            pageStart: e.page_start as number | undefined,
            pageEnd: e.page_end as number | undefined,
            evidenceText: e.evidence_text as string,
          })),
          evidenceGaps: (ca.evidence_gaps as string[]) || [],
          reviewerQuestions: (ca.reviewer_questions as string[]) || [],
        })),
        strengths: ((res.strengths as Record<string, unknown>[]) || []).map((s) => ({
          title: s.title as string,
          description: s.description as string,
          supportingEvidence: ((s.supporting_evidence as Record<string, unknown>[]) || []).map((e) => ({
            sourceType: e.source_type as string,
            sourceReference: e.source_reference as string,
            evidenceText: e.evidence_text as string,
          })),
        })),
        concerns: ((res.concerns as Record<string, unknown>[]) || []).map((c) => ({
          title: c.title as string,
          description: c.description as string,
          supportingEvidence: ((c.supporting_evidence as Record<string, unknown>[]) || []).map((e) => ({
            sourceType: e.source_type as string,
            sourceReference: e.source_reference as string,
            evidenceText: e.evidence_text as string,
          })),
        })),
        evidenceGaps: ((res.evidence_gaps as Record<string, unknown>[]) || []).map((eg) => ({
          criterionKey: eg.criterion_key as string,
          gapDescription: eg.gap_description as string,
          impact: eg.impact as string,
          reviewerAction: eg.reviewer_action as string,
        })),
        reviewerQuestions: ((res.reviewer_questions as Record<string, unknown>[]) || []).map((rq) => ({
          criterionKey: rq.criterion_key as string,
          question: rq.question as string,
          rationale: rq.rationale as string,
        })),
        contradictions: ((res.contradictions as Record<string, unknown>[]) || []).map((cd) => ({
          fieldA: cd.field_a as string,
          fieldB: cd.field_b as string,
          observation: cd.observation as string,
          severity: cd.severity as string,
        })),
        disclaimer: (res.disclaimer as string) || "",
      },
    };
  },

  _mapEvaluation(item: ApiEvaluationDetail): EvaluationDetail {
    return {
      id: item.id,
      proposalId: item.proposal_id,
      reviewerId: item.reviewer_id,
      rubricId: item.rubric_id,
      rubricVersion: item.rubric_version || "v1.0",
      status: item.status,
      overallScore: item.overall_score,
      reviewerSummary: item.reviewer_summary,
      reviewerRecommendation: item.reviewer_recommendation || "FAVORABLE_WITH_CONDITIONS",
      startedAt: item.started_at,
      completedAt: item.completed_at,
      createdAt: item.created_at,
      proposal: item.proposal ? proposalService._mapProposal(item.proposal as unknown as Parameters<typeof proposalService._mapProposal>[0]) : undefined,
      criteria: (item.criteria || []).map((c) => ({
        id: c.id,
        criterionKey: c.criterion_key,
        name: c.name,
        description: c.description,
        maxScore: c.max_score,
        weight: c.weight,
        comments: c.comments,
        justificationNotes: c.justification_notes,
      })),
      evidences: (item.evidences || []).map((e) => ({
        id: e.id,
        evaluationId: e.evaluation_id,
        criterionId: e.criterion_id,
        evidenceType: e.evidence_type,
        sourceType: e.source_type,
        sourceReference: e.source_reference,
        sourcePageStart: e.source_page_start,
        sourcePageEnd: e.source_page_end,
        evidenceText: e.evidence_text,
        reviewerNote: e.reviewer_note,
        createdAt: e.created_at,
      })),
    };
  },

  async getReviewContext(evaluationId: string): Promise<Record<string, unknown>> {
    const res = await fetch(`${appConfig.apiBaseUrl}/evaluations/${evaluationId}/review-context`, { cache: "no-store" });
    if (!res.ok) throw new Error("Failed to load review context");
    return await res.json();
  },

  async createDecisionPack(evaluationId: string): Promise<Record<string, unknown>> {
    const res = await fetch(`${appConfig.apiBaseUrl}/evaluations/${evaluationId}/decision-pack`, {
      method: "POST",
    });
    if (!res.ok) throw new Error("Failed to generate decision pack");
    return await res.json();
  },

  getDecisionPackPdfUrl(evaluationId: string): string {
    return `${appConfig.apiBaseUrl}/evaluations/${evaluationId}/decision-pack.pdf`;
  },

  async getReviewerQueue(reviewerId: string): Promise<Record<string, unknown>[]> {
    const res = await fetch(`${appConfig.apiBaseUrl}/reviewer/queue?reviewer_id=${encodeURIComponent(reviewerId)}`, { cache: "no-store" });
    if (!res.ok) throw new Error("Failed to load reviewer queue");
    return await res.json();
  },

  async assignReviewer(evaluationId: string, reviewerId: string): Promise<Record<string, unknown>> {
    const res = await fetch(`${appConfig.apiBaseUrl}/evaluations/${evaluationId}/assign`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reviewer_id: reviewerId, assigned_by: "System Admin" }),
    });
    if (!res.ok) throw new Error("Failed to assign reviewer");
    return await res.json();
  },

  async returnForRevision(evaluationId: string, reason: string): Promise<Record<string, unknown>> {
    const res = await fetch(`${appConfig.apiBaseUrl}/evaluations/${evaluationId}/return`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ returned_by: "Committee Chair", reason }),
    });
    if (!res.ok) throw new Error("Failed to return evaluation for revision");
    return await res.json();
  },

  async getSystemReadiness(): Promise<Record<string, unknown>> {
    const res = await fetch(`${appConfig.apiBaseUrl}/health/readiness`, { cache: "no-store" });
    if (!res.ok) throw new Error("Failed to check system readiness");
    return await res.json();
  },

  async getReviewerComparison(evaluationId: string): Promise<Record<string, unknown>> {
    const res = await fetch(`${appConfig.apiBaseUrl}/evaluations/${evaluationId}/reviewer-comparison`, { cache: "no-store" });
    if (!res.ok) {
      const errPayload = await res.json().catch(() => ({}));
      throw new Error(errPayload.detail || "Failed to load reviewer comparison");
    }
    return await res.json();
  },

  async finalizeGovernance(evaluationId: string, recommendation: string, note: string): Promise<Record<string, unknown>> {
    const res = await fetch(`${appConfig.apiBaseUrl}/evaluations/${evaluationId}/finalize-governance`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ finalized_by: "Governance Chair", recommendation, note }),
    });
    if (!res.ok) {
      const errPayload = await res.json().catch(() => ({}));
      throw new Error(errPayload.detail || "Failed to finalize governance record");
    }
    return await res.json();
  },
};
