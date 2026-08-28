import { HistoricalProject } from "../types";
import { DEMO_HISTORICAL_PROJECTS } from "../constants";
import { appConfig } from "../config";

interface ApiHistoricalProject {
  id: string;
  project_code: string;
  title: string;
  institution: string;
  domain: string;
  objectives?: string;
  methodology?: string;
  technology?: string;
  expected_outcomes?: string;
  status: "COMPLETED" | "ONGOING" | "TERMINATED" | "NEEDS_REVIEW";
  approved_cost: number;
  approved_cost_raw?: string | null;
  completion_date?: string;
  source: string;
  source_type: "OFFICIAL" | "PUBLIC" | "SYNTHETIC" | "MANUAL";
  source_url?: string | null;
  source_document_name?: string | null;
  source_page_start?: number | null;
  source_page_end?: number | null;
  raw_record_text?: string | null;
  verification_status: "NEEDS_REVIEW" | "VERIFIED" | "REJECTED";
  verification_timestamp?: string | null;
}

export const projectService = {
  async getHistoricalProjects(params?: {
    domain?: string;
    institution?: string;
    status?: string;
    sourceType?: string;
    verificationStatus?: string;
    search?: string;
  }): Promise<HistoricalProject[]> {
    try {
      const query = new URLSearchParams();
      if (params?.domain) query.append("domain", params.domain);
      if (params?.institution) query.append("institution", params.institution);
      if (params?.status) query.append("status", params.status);
      if (params?.sourceType) query.append("source_type", params.sourceType);
      if (params?.verificationStatus) query.append("verification_status", params.verificationStatus);
      if (params?.search) query.append("search", params.search);

      const res = await fetch(`${appConfig.apiBaseUrl}/projects?${query.toString()}`, {
        cache: "no-store",
      });

      if (res.ok) {
        const rawList: ApiHistoricalProject[] = await res.json();
        if (Array.isArray(rawList) && rawList.length > 0) {
          return rawList.map((item) => ({
            id: item.id,
            projectCode: item.project_code,
            title: item.title,
            institution: {
              id: item.id,
              name: item.institution,
              code: "INST",
              type: "RESEARCH_INSTITUTE",
              location: "India",
            },
            domain: item.domain,
            principalInvestigator: "Archived PI",
            status: item.status || "ONGOING",
            completionYear: item.completion_date ? new Date(item.completion_date).getFullYear() : 2026,
            totalCost: item.approved_cost || 0,
            approvedCostRaw: item.approved_cost_raw,
            technologyStack: item.technology ? item.technology.split(",").map((t) => t.trim()) : ["R&D Tech"],
            summary: item.objectives || item.methodology || item.raw_record_text || "Historical benchmark project record.",
            source: item.source || "CIL/CMPDI",
            sourceType: item.source_type || "OFFICIAL",
            sourceUrl: item.source_url,
            sourceDocumentName: item.source_document_name,
            sourcePageStart: item.source_page_start,
            sourcePageEnd: item.source_page_end,
            rawRecordText: item.raw_record_text,
            verificationStatus: item.verification_status || "NEEDS_REVIEW",
            verificationTimestamp: item.verification_timestamp,
            similarityScore: 0.8,
          }));
        }
      }
    } catch {
      // Fallback to initial demo constants if backend is unreachable
    }

    let results = [...DEMO_HISTORICAL_PROJECTS];
    if (params?.domain) {
      results = results.filter((p) => p.domain === params.domain);
    }
    if (params?.search) {
      const q = params.search.toLowerCase();
      results = results.filter(
        (p) =>
          p.title.toLowerCase().includes(q) ||
          p.id.toLowerCase().includes(q) ||
          p.technologyStack.some((tech) => tech.toLowerCase().includes(q))
      );
    }
    return results;
  },

  async getHistoricalProjectById(id: string): Promise<HistoricalProject | null> {
    try {
      const res = await fetch(`${appConfig.apiBaseUrl}/projects/${id}`, {
        cache: "no-store",
      });
      if (res.ok) {
        const item: ApiHistoricalProject = await res.json();
        return {
          id: item.id,
          projectCode: item.project_code,
          title: item.title,
          institution: {
            id: item.id,
            name: item.institution,
            code: "INST",
            type: "RESEARCH_INSTITUTE",
            location: "India",
          },
          domain: item.domain,
          principalInvestigator: "Archived PI",
          status: item.status || "ONGOING",
          completionYear: item.completion_date ? new Date(item.completion_date).getFullYear() : 2026,
          totalCost: item.approved_cost || 0,
          approvedCostRaw: item.approved_cost_raw,
          technologyStack: item.technology ? item.technology.split(",").map((t) => t.trim()) : ["R&D Tech"],
          summary: item.objectives || item.methodology || item.raw_record_text || "Historical benchmark project record.",
          source: item.source || "CIL/CMPDI",
          sourceType: item.source_type || "OFFICIAL",
          sourceUrl: item.source_url,
          sourceDocumentName: item.source_document_name,
          sourcePageStart: item.source_page_start,
          sourcePageEnd: item.source_page_end,
          rawRecordText: item.raw_record_text,
          verificationStatus: item.verification_status || "NEEDS_REVIEW",
          verificationTimestamp: item.verification_timestamp,
          similarityScore: 0.8,
        };
      }
    } catch {
      // Fallback
    }

    const project = DEMO_HISTORICAL_PROJECTS.find((p) => p.id.toLowerCase() === id.toLowerCase());
    return project || DEMO_HISTORICAL_PROJECTS[0];
  },

  async updateVerificationStatus(id: string, verificationStatus: "VERIFIED" | "REJECTED" | "NEEDS_REVIEW"): Promise<HistoricalProject> {
    const res = await fetch(`${appConfig.apiBaseUrl}/projects/${id}/verification`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ verification_status: verificationStatus }),
    });

    if (!res.ok) {
      throw new Error(`Failed to update verification status: ${res.statusText}`);
    }

    const item: ApiHistoricalProject = await res.json();
    return {
      id: item.id,
      projectCode: item.project_code,
      title: item.title,
      institution: {
        id: item.id,
        name: item.institution,
        code: "INST",
        type: "RESEARCH_INSTITUTE",
        location: "India",
      },
      domain: item.domain,
      principalInvestigator: "Archived PI",
      status: item.status || "ONGOING",
      completionYear: item.completion_date ? new Date(item.completion_date).getFullYear() : 2026,
      totalCost: item.approved_cost || 0,
      approvedCostRaw: item.approved_cost_raw,
      technologyStack: item.technology ? item.technology.split(",").map((t) => t.trim()) : ["R&D Tech"],
      summary: item.objectives || item.methodology || item.raw_record_text || "Historical benchmark project record.",
      source: item.source || "CIL/CMPDI",
      sourceType: item.source_type || "OFFICIAL",
      sourceUrl: item.source_url,
      sourceDocumentName: item.source_document_name,
      sourcePageStart: item.source_page_start,
      sourcePageEnd: item.source_page_end,
      rawRecordText: item.raw_record_text,
      verificationStatus: item.verification_status || "NEEDS_REVIEW",
      verificationTimestamp: item.verification_timestamp,
      similarityScore: 0.8,
    };
  },
};
