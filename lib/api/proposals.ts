import { Proposal, ProposalStatus, ProposalPriority } from "../types";
import { DEMO_PROPOSALS } from "../constants";
import { appConfig } from "../config";

interface ApiProposal {
  id: string;
  title: string;
  institution_id: string;
  institution?: {
    id: string;
    name: string;
    code: string;
    type: "ACADEMIC" | "RESEARCH_INSTITUTE" | "INDUSTRY" | "GOVERNMENT";
    location: string;
  };
  principal_investigator: string;
  domain: string;
  problem_statement?: string;
  objectives?: string;
  status: ProposalStatus;
  priority: ProposalPriority;
  budget_total: number;
  submission_date?: string;
  created_at?: string;
}

export const proposalService = {
  async getProposals(params?: { status?: ProposalStatus; domain?: string; search?: string }): Promise<Proposal[]> {
    try {
      const query = new URLSearchParams();
      if (params?.status) query.append("status", params.status);
      if (params?.domain) query.append("domain", params.domain);

      const res = await fetch(`${appConfig.apiBaseUrl}/proposals?${query.toString()}`, {
        cache: "no-store",
      });

      if (res.ok) {
        const rawList: ApiProposal[] = await res.json();
        if (Array.isArray(rawList) && rawList.length > 0) {
          let proposals: Proposal[] = rawList.map((item) => ({
            id: item.id,
            title: item.title,
            institution: {
              id: item.institution?.id || item.institution_id,
              name: item.institution?.name || "Academic Institution",
              code: item.institution?.code || "INST",
              type: item.institution?.type || "ACADEMIC",
              location: item.institution?.location || "India",
            },
            domain: item.domain,
            principalInvestigator: item.principal_investigator,
            submittedDate: item.submission_date || item.created_at || new Date().toISOString(),
            status: item.status,
            priority: item.priority || "MEDIUM",
            proposedBudget: item.budget_total || 0,
            durationMonths: 24,
            summary: item.problem_statement || item.objectives || "No summary provided.",
            keywords: [item.domain],
          }));

          if (params?.search) {
            const q = params.search.toLowerCase();
            proposals = proposals.filter(
              (p) =>
                p.title.toLowerCase().includes(q) ||
                p.id.toLowerCase().includes(q) ||
                p.institution.name.toLowerCase().includes(q)
            );
          }
          return proposals;
        }
      }
    } catch {
      // Fallback to initial demo constants if backend is unreachable
    }

    let results = [...DEMO_PROPOSALS];
    if (params?.status) {
      results = results.filter((p) => p.status === params.status);
    }
    if (params?.domain) {
      results = results.filter((p) => p.domain === params.domain);
    }
    if (params?.search) {
      const q = params.search.toLowerCase();
      results = results.filter(
        (p) =>
          p.title.toLowerCase().includes(q) ||
          p.id.toLowerCase().includes(q) ||
          p.institution.name.toLowerCase().includes(q)
      );
    }
    return results;
  },

  async getProposalById(id: string): Promise<Proposal | null> {
    try {
      const res = await fetch(`${appConfig.apiBaseUrl}/proposals/${id}`, {
        cache: "no-store",
      });
      if (res.ok) {
        const item: ApiProposal = await res.json();
        return {
          id: item.id,
          title: item.title,
          institution: {
            id: item.institution?.id || item.institution_id,
            name: item.institution?.name || "Academic Institution",
            code: item.institution?.code || "INST",
            type: item.institution?.type || "ACADEMIC",
            location: item.institution?.location || "India",
          },
          domain: item.domain,
          principalInvestigator: item.principal_investigator,
          submittedDate: item.submission_date || item.created_at || new Date().toISOString(),
          status: item.status,
          priority: item.priority || "MEDIUM",
          proposedBudget: item.budget_total || 0,
          durationMonths: 24,
          summary: item.problem_statement || item.objectives || "No summary provided.",
          keywords: [item.domain],
        };
      }
    } catch {
      // Fallback
    }

    const proposal = DEMO_PROPOSALS.find((p) => p.id.toLowerCase() === id.toLowerCase());
    return proposal || DEMO_PROPOSALS[0];
  },

  async createProposal(data: {
    title: string;
    institution_id: string;
    principal_investigator: string;
    domain: string;
    budget_total: number;
    problem_statement?: string;
    objectives?: string;
  }): Promise<Proposal> {
    const res = await fetch(`${appConfig.apiBaseUrl}/proposals`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      throw new Error(`Failed to create proposal: ${res.statusText}`);
    }
    const item: ApiProposal = await res.json();
    return {
      id: item.id,
      title: item.title,
      institution: {
        id: item.institution?.id || item.institution_id,
        name: item.institution?.name || "Academic Institution",
        code: item.institution?.code || "INST",
        type: item.institution?.type || "ACADEMIC",
        location: item.institution?.location || "India",
      },
      domain: item.domain,
      principalInvestigator: item.principal_investigator,
      submittedDate: item.submission_date || item.created_at || new Date().toISOString(),
      status: item.status,
      priority: item.priority || "MEDIUM",
      proposedBudget: item.budget_total || 0,
      durationMonths: 24,
      summary: item.problem_statement || item.objectives || "No summary provided.",
      keywords: [item.domain],
    };
  },
};
