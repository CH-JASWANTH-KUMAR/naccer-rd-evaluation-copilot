import { appConfig } from "../config";

export interface ApiDocumentDetail {
  id: string;
  proposal_id: string;
  filename: string;
  file_type: string;
  file_size: number;
  storage_path: string;
  processing_status: "UPLOADED" | "PROCESSING" | "PROCESSED" | "FAILED";
  processing_error?: string | null;
  created_at: string;
  updated_at: string;
  pages_count: number;
  sections_count: number;
}

export interface ApiDocumentPage {
  id: string;
  document_id: string;
  page_number: number;
  text: string;
  created_at: string;
}

export interface ApiProposalSection {
  id: string;
  proposal_id: string;
  document_id: string;
  section_type: string;
  section_title: string;
  content: string;
  start_page: number;
  end_page: number;
  confidence: number;
  created_at: string;
  updated_at: string;
}

export const documentService = {
  async uploadDocument(proposalId: string, file: File): Promise<ApiDocumentDetail> {
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${appConfig.apiBaseUrl}/proposals/${proposalId}/documents`, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => null);
      throw new Error(errData?.detail || `Failed to upload document: ${res.statusText}`);
    }

    return await res.json();
  },

  async getProposalDocuments(proposalId: string): Promise<ApiDocumentDetail[]> {
    try {
      const res = await fetch(`${appConfig.apiBaseUrl}/proposals/${proposalId}/documents`, {
        cache: "no-store",
      });
      if (res.ok) {
        return await res.json();
      }
    } catch {
      // Fallback
    }
    return [];
  },

  async getDocument(documentId: string): Promise<ApiDocumentDetail | null> {
    try {
      const res = await fetch(`${appConfig.apiBaseUrl}/documents/${documentId}`, {
        cache: "no-store",
      });
      if (res.ok) {
        return await res.json();
      }
    } catch {
      // Fallback
    }
    return null;
  },

  async getDocumentPages(documentId: string): Promise<ApiDocumentPage[]> {
    try {
      const res = await fetch(`${appConfig.apiBaseUrl}/documents/${documentId}/pages`, {
        cache: "no-store",
      });
      if (res.ok) {
        return await res.json();
      }
    } catch {
      // Fallback
    }
    return [];
  },

  async getDocumentSections(documentId: string): Promise<ApiProposalSection[]> {
    try {
      const res = await fetch(`${appConfig.apiBaseUrl}/documents/${documentId}/sections`, {
        cache: "no-store",
      });
      if (res.ok) {
        return await res.json();
      }
    } catch {
      // Fallback
    }
    return [];
  },
};
