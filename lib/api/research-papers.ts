import { appConfig } from "../config";

export interface ResearchPaperPage {
  id: string;
  researchPaperId: string;
  pageNumber: number;
  extractedText: string;
  characterCount: number;
  detectedSections?: string | null;
  extractionStatus: string;
  createdAt: string;
}

export interface ResearchPaper {
  id: string;
  title: string;
  authors?: string | null;
  abstract?: string | null;
  publicationYear?: number | null;
  journalOrConference?: string | null;
  doi?: string | null;
  researchDomain: string;
  keywords?: string | null;
  sourceFilename: string;
  sourceDocumentType: string;
  pageCount: number;
  fileHash: string;
  extractionStatus: string;
  createdAt: string;
  updatedAt: string;
  pages: ResearchPaperPage[];
}

export interface ResearchPaperSearchResult {
  paperId: string;
  evidenceId: string;
  paperIndex: number;
  title: string;
  authors?: string | null;
  publicationYear?: number | null;
  researchDomain: string;
  pageNumber: number;
  matchedSections: string[];
  matchedDimensions: string[];
  relevanceScore: number;
  snippet: string;
  sourceFilename: string;
}

export interface ResearchPaperSearchResponse {
  querySummary: Record<string, unknown>;
  totalPapersEvaluated: number;
  resultsCount: number;
  disclaimer: string;
  results: ResearchPaperSearchResult[];
}

export interface ScientificMetric {
  metricName: string;
  rawValue: string;
  normalizedValue?: number | null;
  unit?: string | null;
  comparisonTarget?: string | null;
  sourcePage: number;
  sourceSection?: string | null;
  evidenceId: string;
  sourceText: string;
}

export interface ScientificDataset {
  datasetName: string;
  datasetSource?: string | null;
  sampleCountRaw?: string | null;
  sampleCountNumeric?: number | null;
  sensorCount?: number | null;
  featureCount?: number | null;
  sourcePage: number;
  evidenceId: string;
  sourceText: string;
}

export interface ScientificExperiment {
  algorithms: string[];
  baselines: string[];
  validationStrategy?: string | null;
  hardwareSensors: string[];
  sourcePage: number;
  evidenceId: string;
  sourceText: string;
}

export interface ComparisonRecord {
  dimension: string;
  proposalValue: string;
  paperValue: string;
  sourceEvidenceId: string;
  status: "MATCHING" | "DIFFERENT" | "PARTIALLY_MATCHING" | "NOT_REPORTED" | "NOT_COMPARABLE";
}

export interface ComparisonSummary {
  proposalId: string;
  paperId: string;
  paperTitle: string;
  comparisons: ComparisonRecord[];
}

export const researchPaperService = {
  async getResearchPapers(domain?: string): Promise<ResearchPaper[]> {
    try {
      const url = domain
        ? `${appConfig.apiBaseUrl}/research-papers?domain=${encodeURIComponent(domain)}`
        : `${appConfig.apiBaseUrl}/research-papers`;
      const res = await fetch(url, { cache: "no-store" });
      if (!res.ok) return [];
      const data = await res.json();
      return data.map(this._mapPaper);
    } catch {
      return [];
    }
  },

  async getResearchPaperById(id: string): Promise<ResearchPaper | null> {
    try {
      const res = await fetch(`${appConfig.apiBaseUrl}/research-papers/${id}`, { cache: "no-store" });
      if (!res.ok) return null;
      const item = await res.json();
      return this._mapPaper(item);
    } catch {
      return null;
    }
  },

  async getPaperMetrics(paperId: string): Promise<ScientificMetric[]> {
    try {
      const res = await fetch(`${appConfig.apiBaseUrl}/research-papers/${paperId}/metrics`, { cache: "no-store" });
      if (!res.ok) return [];
      const data = await res.json();
      return data.map((item: Record<string, unknown>) => ({
        metricName: item.metric_name as string,
        rawValue: item.raw_value as string,
        normalizedValue: (item.normalized_value as number) || null,
        unit: (item.unit as string) || null,
        comparisonTarget: (item.comparison_target as string) || null,
        sourcePage: item.source_page as number,
        sourceSection: (item.source_section as string) || null,
        evidenceId: item.evidence_id as string,
        sourceText: item.source_text as string,
      }));
    } catch {
      return [];
    }
  },

  async getPaperDatasets(paperId: string): Promise<ScientificDataset[]> {
    try {
      const res = await fetch(`${appConfig.apiBaseUrl}/research-papers/${paperId}/datasets`, { cache: "no-store" });
      if (!res.ok) return [];
      const data = await res.json();
      return data.map((item: Record<string, unknown>) => ({
        datasetName: item.dataset_name as string,
        datasetSource: (item.dataset_source as string) || null,
        sampleCountRaw: (item.sample_count_raw as string) || null,
        sampleCountNumeric: (item.sample_count_numeric as number) || null,
        sensorCount: (item.sensor_count as number) || null,
        featureCount: (item.feature_count as number) || null,
        sourcePage: item.source_page as number,
        evidenceId: item.evidence_id as string,
        sourceText: item.source_text as string,
      }));
    } catch {
      return [];
    }
  },

  async getPaperExperiments(paperId: string): Promise<ScientificExperiment[]> {
    try {
      const res = await fetch(`${appConfig.apiBaseUrl}/research-papers/${paperId}/experiments`, { cache: "no-store" });
      if (!res.ok) return [];
      const data = await res.json();
      return data.map((item: Record<string, unknown>) => ({
        algorithms: (item.algorithms as string[]) || [],
        baselines: (item.baselines as string[]) || [],
        validationStrategy: (item.validation_strategy as string) || null,
        hardwareSensors: (item.hardware_sensors as string[]) || [],
        sourcePage: item.source_page as number,
        evidenceId: item.evidence_id as string,
        sourceText: item.source_text as string,
      }));
    } catch {
      return [];
    }
  },

  async searchResearchPapers(query: string, domain?: string, topK = 5): Promise<ResearchPaperSearchResponse> {
    const res = await fetch(`${appConfig.apiBaseUrl}/research-papers/search`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, research_domain: domain, top_k: topK }),
    });
    if (!res.ok) throw new Error("Research paper search failed");
    const data = await res.json();
    return {
      querySummary: data.query_summary,
      totalPapersEvaluated: data.total_papers_evaluated,
      resultsCount: data.results_count,
      disclaimer: data.disclaimer,
      results: (data.results || []).map((item: Record<string, unknown>) => ({
        paperId: item.paper_id as string,
        evidenceId: item.evidence_id as string,
        paperIndex: item.paper_index as number,
        title: item.title as string,
        authors: (item.authors as string) || null,
        publicationYear: (item.publication_year as number) || null,
        researchDomain: item.research_domain as string,
        pageNumber: item.page_number as number,
        matchedSections: (item.matched_sections as string[]) || [],
        matchedDimensions: (item.matched_dimensions as string[]) || [],
        relevanceScore: item.relevance_score as number,
        snippet: item.snippet as string,
        sourceFilename: item.source_filename as string,
      })),
    };
  },

  async seedResearchPaperFixture(): Promise<ResearchPaper> {
    const res = await fetch(`${appConfig.apiBaseUrl}/research-papers/seed`, { method: "POST" });
    if (!res.ok) throw new Error("Failed to seed research paper fixture");
    const item = await res.json();
    return this._mapPaper(item);
  },

  async uploadResearchPaper(file: File, domain = "Coal Mining & Automation"): Promise<ResearchPaper> {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${appConfig.apiBaseUrl}/research-papers/upload?research_domain=${encodeURIComponent(domain)}`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) throw new Error("Failed to upload research paper");
    const item = await res.json();
    return this._mapPaper(item);
  },

  _mapPaper(item: Record<string, unknown>): ResearchPaper {
    return {
      id: item.id as string,
      title: item.title as string,
      authors: (item.authors as string) || null,
      abstract: (item.abstract as string) || null,
      publicationYear: (item.publication_year as number) || null,
      journalOrConference: (item.journal_or_conference as string) || null,
      doi: (item.doi as string) || null,
      researchDomain: item.research_domain as string,
      keywords: (item.keywords as string) || null,
      sourceFilename: item.source_filename as string,
      sourceDocumentType: (item.source_document_type as string) || "PDF",
      pageCount: item.page_count as number,
      fileHash: item.file_hash as string,
      extractionStatus: item.extraction_status as string,
      createdAt: item.created_at as string,
      updatedAt: item.updated_at as string,
      pages: ((item.pages as Record<string, unknown>[]) || []).map((p) => ({
        id: p.id as string,
        researchPaperId: p.research_paper_id as string,
        pageNumber: p.page_number as number,
        extractedText: p.extracted_text as string,
        characterCount: p.character_count as number,
        detectedSections: (p.detected_sections as string) || null,
        extractionStatus: p.extraction_status as string,
        createdAt: p.created_at as string,
      })),
    };
  },
};
