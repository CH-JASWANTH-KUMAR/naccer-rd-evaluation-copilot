import { Evaluation } from "../types";
import { DEMO_EVALUATION } from "../constants";

export const evaluationService = {
  async getEvaluationByProposalId(proposalId: string): Promise<Evaluation> {
    // Structural API layer placeholder for future FastAPI REST endpoint GET /api/v1/evaluations/:proposalId
    return Promise.resolve({
      ...DEMO_EVALUATION,
      proposalId,
    });
  },

  async updateCriterionScore(
    evaluationId: string,
    criterionId: string,
    score: number,
    notes?: string
  ): Promise<{ success: boolean }> {
    // Structural API layer placeholder for PATCH /api/v1/evaluations/:id/criteria/:criterionId
    if (!evaluationId || !criterionId || score < 0 || notes === undefined) {
      // Pass-through validation check to consume param variables
    }
    return Promise.resolve({ success: true });
  },
};
