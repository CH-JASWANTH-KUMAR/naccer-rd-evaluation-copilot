import { Institution } from "../types";
import { MOCK_INSTITUTIONS } from "../constants";
import { appConfig } from "../config";

interface ApiInstitution {
  id: string;
  name: string;
  code: string;
  type: "ACADEMIC" | "RESEARCH_INSTITUTE" | "INDUSTRY" | "GOVERNMENT";
  location: string;
}

export const institutionService = {
  async getInstitutions(): Promise<Institution[]> {
    try {
      const res = await fetch(`${appConfig.apiBaseUrl}/institutions`, {
        cache: "no-store",
      });
      if (res.ok) {
        const data: ApiInstitution[] = await res.json();
        if (Array.isArray(data) && data.length > 0) {
          return data.map((inst) => ({
            id: inst.id,
            name: inst.name,
            code: inst.code,
            type: inst.type,
            location: inst.location,
          }));
        }
      }
    } catch {
      // Fallback to initial demo constants if backend is unreachable
    }
    return MOCK_INSTITUTIONS;
  },

  async createInstitution(data: { name: string; code: string; type: string; location: string }): Promise<Institution> {
    const res = await fetch(`${appConfig.apiBaseUrl}/institutions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      throw new Error(`Failed to create institution: ${res.statusText}`);
    }
    return await res.json();
  },
};
