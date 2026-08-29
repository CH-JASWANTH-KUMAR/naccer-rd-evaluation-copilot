import { appConfig } from "../config";

export interface ReviewerAssignedProposalCard {
  evaluationId: string;
  proposalId: string;
  proposalReference: string;
  proposalTitle: string;
  institution: string;
  domain: string;
  taskTitle?: string;
  priority?: string;
  isDemo?: boolean;
  evidenceSourcesCount?: number;
  reviewStatus: string;
  assignmentDate: string;
  dueDate: string | null;
  rubricCompletedCount: number;
  rubricTotalCount: number;
  scientificComparisonAvailable: boolean;
  evidenceGapsCount: number;
  consensusStatus: string;
  actionRequired: string;
}

export interface EvidenceReadinessComponentDetail {
  name: string;
  score: number;
  maxScore: number;
  status: string;
  explanation: string;
  contributingChecks: string[];
}

export interface EvidenceReadinessItem {
  evidenceId: string;
  title: string;
  description: string;
  sourceType: string;
}

export interface EvidenceReadinessResponse {
  proposalId: string;
  totalScore: number;
  maxScore: number;
  interpretationLabel: string;
  isDemo: boolean;
  disclaimer: string;
  proposalCompletenessScore: number;
  scientificEvidenceCoverageScore: number;
  mocGuidelineCoverageScore: number;
  financialVerificationScore: number;
  historicalResearchSupportScore: number;
  reviewerCompletionScore: number;
  components: EvidenceReadinessComponentDetail[];
  strengths: { evidenceId: string; title: string; description: string; sourceType: string }[];
  attentionRequired: { evidenceId: string; title: string; description: string; sourceType: string }[];
}

export interface ReviewerWorkspaceQueue {
  reviewerId: string;
  pendingReviews: ReviewerAssignedProposalCard[];
  completedReviews: ReviewerAssignedProposalCard[];
  coiReviews: ReviewerAssignedProposalCard[];
}

export interface ChairReviewerProgressItem {
  reviewerId: string;
  reviewerName: string;
  status: string;
  submittedAt: string | null;
}

export interface ChairProposalCoordinationItem {
  proposalId: string;
  evaluationId: string | null;
  proposalReference: string;
  proposalTitle: string;
  institution: string;
  domain: string;
  reviewers: ChairReviewerProgressItem[];
  rubricProgress: string;
  scientificComparisonStatus: string;
  financialStatus: string;
  consensusStatus: string;
  maxScoreVariance: number;
  decisionReadiness: string;
  blockingReasons: string[];
  primaryAction: string;
}

export interface ChairDashboardResponse {
  totalProposals: number;
  readyCount: number;
  notReadyCount: number;
  needsAttentionCount: number;
  items: ChairProposalCoordinationItem[];
}

export interface DecisionReadinessCheck {
  proposalId: string;
  status: string;
  isReady: boolean;
  blockingReasons: string[];
  prerequisites: Record<string, boolean>;
}

export interface DecisionBriefScientificEvidenceItem {
  evidenceId: string;
  sourceType: string;
  title: string;
  snippet: string;
  sourceProvenance: string;
}

export interface DecisionBriefRubricCriterionItem {
  criterionKey: string;
  criterionName: string;
  maxScore: number;
  averageScore: number | null;
  reviewerScores: Record<string, number>;
  evidenceGroundingStatus: string;
  justificationNotes: string[];
}

export interface DecisionBriefDisagreementItem {
  criterionName: string;
  scoresByReviewer: Record<string, number>;
  difference: number;
  disagreementStatus: string;
  permittedComments: string[];
}

export interface DecisionBriefResponse {
  proposalId: string;
  title: string;
  institution: string;
  principalInvestigator: string;
  domain: string;
  durationMonths: number | null;
  declaredTotalBudget: number | null;

  reviewerCompletion: string;
  rubricCompletion: string;
  scientificComparisonStatus: string;
  financialVerificationStatus: string;
  completenessStatus: string;
  decisionReadiness: string;
  blockingReasons: string[];

  relevantHistoricalProjects: DecisionBriefScientificEvidenceItem[];
  relevantResearchPapers: DecisionBriefScientificEvidenceItem[];
  evidenceGaps: string[];
  reviewerQuestions: string[];

  rubricCriteria: DecisionBriefRubricCriterionItem[];

  consensusStatus: string;
  disagreementFlags: DecisionBriefDisagreementItem[];
  consensusDisclaimer: string;

  outstandingActions: string[];
  generatedAt: string;
}

export const coordinationService = {
  async getReviewerWorkspace(reviewerId: string): Promise<ReviewerWorkspaceQueue> {
    const res = await fetch(`${appConfig.apiBaseUrl}/reviewer/workspace?reviewer_id=${reviewerId}`, { cache: "no-store" });
    if (!res.ok) throw new Error("Failed to fetch reviewer workspace queue");
    const data = await res.json();
    return {
      reviewerId: data.reviewer_id,
      pendingReviews: (data.pending_reviews || []).map(mapCard),
      completedReviews: (data.completed_reviews || []).map(mapCard),
      coiReviews: (data.coi_reviews || []).map(mapCard),
    };
  },

  async getChairDashboard(role = "ADMIN"): Promise<ChairDashboardResponse> {
    const res = await fetch(`${appConfig.apiBaseUrl}/chair/dashboard?role=${role}`, { cache: "no-store" });
    if (!res.ok) throw new Error("Failed to fetch Chair dashboard");
    const data = await res.json();
    return {
      totalProposals: data.total_proposals || 0,
      readyCount: data.ready_count || 0,
      notReadyCount: data.not_ready_count || 0,
      needsAttentionCount: data.needs_attention_count || 0,
      items: (data.items || []).map((item: Record<string, unknown>) => ({
        proposalId: item.proposal_id as string,
        evaluationId: (item.evaluation_id as string) || null,
        proposalReference: item.proposal_reference as string,
        proposalTitle: item.proposal_title as string,
        institution: item.institution as string,
        domain: item.domain as string,
        reviewers: ((item.reviewers as Record<string, unknown>[]) || []).map((r) => ({
          reviewerId: r.reviewer_id as string,
          reviewerName: r.reviewer_name as string,
          status: r.status as string,
          submittedAt: (r.submitted_at as string) || null,
        })),
        rubricProgress: item.rubric_progress as string,
        scientificComparisonStatus: item.scientific_comparison_status as string,
        financialStatus: item.financial_status as string,
        consensusStatus: item.consensus_status as string,
        maxScoreVariance: (item.max_score_variance as number) || 0,
        decisionReadiness: item.decision_readiness as string,
        blockingReasons: (item.blocking_reasons as string[]) || [],
        primaryAction: item.primary_action as string,
      })),
    };
  },

  async getDecisionReadiness(proposalId: string): Promise<DecisionReadinessCheck> {
    const res = await fetch(`${appConfig.apiBaseUrl}/proposals/${proposalId}/decision-readiness`, { cache: "no-store" });
    if (!res.ok) throw new Error("Failed to fetch decision readiness");
    const data = await res.json();
    return {
      proposalId: data.proposal_id,
      status: data.status,
      isReady: Boolean(data.is_ready),
      blockingReasons: data.blocking_reasons || [],
      prerequisites: data.prerequisites || {},
    };
  },

  async getDecisionBrief(proposalId: string, reviewerId?: string, role = "ADMIN"): Promise<DecisionBriefResponse> {
    let url = `${appConfig.apiBaseUrl}/proposals/${proposalId}/decision-brief?role=${role}`;
    if (reviewerId) url += `&reviewer_id=${reviewerId}`;
    const res = await fetch(url, { cache: "no-store" });
    if (!res.ok) throw new Error("Failed to fetch decision brief");
    const data = await res.json();
    return {
      proposalId: data.proposal_id,
      title: data.title,
      institution: data.institution,
      principalInvestigator: data.principal_investigator,
      domain: data.domain,
      durationMonths: (data.duration_months as number) || null,
      declaredTotalBudget: (data.declared_total_budget as number) || null,
      reviewerCompletion: data.reviewer_completion,
      rubricCompletion: data.rubric_completion,
      scientificComparisonStatus: data.scientific_comparison_status,
      financialVerificationStatus: data.financial_verification_status,
      completenessStatus: data.completeness_status,
      decisionReadiness: data.decision_readiness,
      blockingReasons: data.blocking_reasons || [],
      relevantHistoricalProjects: (data.relevant_historical_projects || []).map(mapEvItem),
      relevantResearchPapers: (data.relevant_research_papers || []).map(mapEvItem),
      evidenceGaps: data.evidence_gaps || [],
      reviewerQuestions: data.reviewer_questions || [],
      rubricCriteria: (data.rubric_criteria || []).map((c: Record<string, unknown>) => ({
        criterionKey: c.criterion_key as string,
        criterionName: c.criterion_name as string,
        maxScore: c.max_score as number,
        averageScore: (c.average_score as number) || null,
        reviewerScores: (c.reviewer_scores as Record<string, number>) || {},
        evidenceGroundingStatus: c.evidence_grounding_status as string,
        justificationNotes: (c.justification_notes as string[]) || [],
      })),
      consensusStatus: data.consensus_status,
      disagreementFlags: (data.disagreement_flags || []).map((d: Record<string, unknown>) => ({
        criterionName: d.criterion_name as string,
        scoresByReviewer: (d.scores_by_reviewer as Record<string, number>) || {},
        difference: d.difference as number,
        disagreementStatus: d.disagreement_status as string,
        permittedComments: (d.permitted_comments as string[]) || [],
      })),
      consensusDisclaimer: data.consensus_disclaimer,
      outstandingActions: data.outstanding_actions || [],
      generatedAt: data.generated_at,
    };
  },
  async getEvidenceReadiness(proposalId: string): Promise<EvidenceReadinessResponse> {
    const res = await fetch(`${appConfig.apiBaseUrl}/proposals/${proposalId}/evidence-readiness`, { cache: "no-store" });
    if (!res.ok) throw new Error("Failed to fetch evidence readiness score");
    const data = await res.json();
    return {
      proposalId: data.proposal_id,
      totalScore: data.total_score,
      maxScore: data.max_score || 100,
      interpretationLabel: data.interpretation_label,
      isDemo: Boolean(data.is_demo),
      disclaimer: data.disclaimer,
      proposalCompletenessScore: data.proposal_completeness_score,
      scientificEvidenceCoverageScore: data.scientific_evidence_coverage_score,
      mocGuidelineCoverageScore: data.moc_guideline_coverage_score,
      financialVerificationScore: data.financial_verification_score,
      historicalResearchSupportScore: data.historical_research_support_score,
      reviewerCompletionScore: data.reviewer_completion_score,
      components: (data.components || []).map((c: Record<string, unknown>) => ({
        name: c.name as string,
        score: c.score as number,
        maxScore: c.max_score as number,
        status: c.status as string,
        explanation: c.explanation as string,
        contributingChecks: (c.contributing_checks as string[]) || [],
      })),
      strengths: (data.strengths || []).map((s: Record<string, unknown>) => ({
        evidenceId: s.evidence_id as string,
        title: s.title as string,
        description: s.description as string,
        sourceType: s.source_type as string,
      })),
      attentionRequired: (data.attention_required || []).map((s: Record<string, unknown>) => ({
        evidenceId: s.evidence_id as string,
        title: s.title as string,
        description: s.description as string,
        sourceType: s.source_type as string,
      })),
    } as unknown as EvidenceReadinessResponse;
  },
};

function mapCard(item: Record<string, unknown>): ReviewerAssignedProposalCard {
  return {
    evaluationId: item.evaluation_id as string,
    proposalId: item.proposal_id as string,
    proposalReference: item.proposal_reference as string,
    proposalTitle: item.proposal_title as string,
    institution: item.institution as string,
    domain: item.domain as string,
    taskTitle: (item.task_title as string) || `Review ${item.proposal_title}`,
    priority: (item.priority as string) || "MEDIUM",
    isDemo: Boolean(item.is_demo),
    evidenceSourcesCount: (item.evidence_sources_count as number) || 6,
    reviewStatus: item.review_status as string,
    assignmentDate: item.assignment_date as string,
    dueDate: (item.due_date as string) || null,
    rubricCompletedCount: item.rubric_completed_count as number,
    rubricTotalCount: item.rubric_total_count as number,
    scientificComparisonAvailable: Boolean(item.scientific_comparison_available),
    evidenceGapsCount: item.evidence_gaps_count as number,
    consensusStatus: item.consensus_status as string,
    actionRequired: item.action_required as string,
  };
}

function mapEvItem(item: Record<string, unknown>): DecisionBriefScientificEvidenceItem {
  return {
    evidenceId: item.evidence_id as string,
    sourceType: item.source_type as string,
    title: item.title as string,
    snippet: item.snippet as string,
    sourceProvenance: item.source_provenance as string,
  };
}
