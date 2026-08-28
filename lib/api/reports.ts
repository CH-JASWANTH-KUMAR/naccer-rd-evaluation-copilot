import { Proposal, Evaluation } from "../types";
import { DEMO_PROPOSALS, DEMO_EVALUATION } from "../constants";

export interface EvaluationReportSummary {
  proposal: Proposal;
  evaluation: Evaluation;
  generatedAt: string;
  recommendation: "RECOMMENDED_FOR_APPROVAL" | "NEEDS_REVISION" | "NOT_RECOMMENDED";
  executiveSummary: string;
}

export const reportService = {
  async getReportByProposalId(proposalId: string): Promise<EvaluationReportSummary> {
    // Structural API layer placeholder for GET /api/v1/reports/:proposalId
    const proposal = DEMO_PROPOSALS.find((p) => p.id.toLowerCase() === proposalId.toLowerCase()) || DEMO_PROPOSALS[0];
    return Promise.resolve({
      proposal,
      evaluation: DEMO_EVALUATION,
      generatedAt: new Date().toISOString(),
      recommendation: "NEEDS_REVISION",
      executiveSummary: "Structural evaluation summary document. Final AI synthesis score report will populate upon backend integration in phase P0.",
    });
  },
};
