import json
import re

from sqlalchemy.orm import Session

from app.models.research_paper import ResearchPaper
from app.repositories.research_papers import ResearchPaperRepository
from app.schemas.research_paper import (
    ResearchPaperSearchRequest,
    ResearchPaperSearchResponse,
    ResearchPaperSearchResultItem,
)

PAPER_DISCLAIMER = (
    "Research paper search results provide scientific evidence items for human reviewer evaluation "
    "and do not constitute an automated novelty, duplication, or funding decision."
)


class ResearchPaperSearchService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ResearchPaperRepository(db)

    def search_papers(self, request: ResearchPaperSearchRequest) -> ResearchPaperSearchResponse:
        query_text = (request.query or "").strip()
        papers = self.repo.get_all(research_domain=request.research_domain)

        if not papers:
            # Fallback to all papers if domain filter returned empty
            papers = self.repo.get_all()

        if not query_text or not papers:
            return ResearchPaperSearchResponse(
                query_summary={"query": query_text, "top_k": request.top_k},
                total_papers_evaluated=len(papers),
                results_count=0,
                disclaimer=PAPER_DISCLAIMER,
                results=[],
            )

        q_tokens = self._extract_tokens(query_text)
        results: list[tuple[float, ResearchPaper, int, str, list[str], list[str]]] = []

        for _p_idx, paper in enumerate(papers, start=1):
            for page in paper.pages:
                page_text = page.extracted_text or ""
                p_tokens = self._extract_tokens(f"{paper.title} {paper.abstract or ''} {page_text}")
                overlap = q_tokens.intersection(p_tokens)

                if not overlap:
                    continue

                token_score = len(overlap) / float(len(q_tokens))
                exact_phrase_bonus = 0.3 if query_text.lower() in page_text.lower() or query_text.lower() in paper.title.lower() else 0.0
                rel_score = round(max(0.0, min(1.0, float(0.7 * token_score + exact_phrase_bonus))), 4)

                if rel_score < 0.05:
                    continue

                sections = []
                if page.detected_sections:
                    try:
                        sections = json.loads(page.detected_sections)
                    except Exception:
                        pass

                matched_dimensions = self._determine_matched_dimensions(q_tokens, page_text, paper)
                snippet = self._build_snippet(page_text, overlap)

                results.append((rel_score, paper, page.page_number, snippet, sections, matched_dimensions))

        # Sort descending by relevance score
        results.sort(key=lambda x: x[0], reverse=True)
        top_candidates = results[: request.top_k]

        final_items: list[ResearchPaperSearchResultItem] = []
        paper_index_map: dict[str, int] = {}
        paper_counter = 1

        for score, paper, page_num, snippet, sections, dims in top_candidates:
            if paper.id not in paper_index_map:
                paper_index_map[paper.id] = paper_counter
                paper_counter += 1

            p_num_val = paper_index_map[paper.id]
            evidence_id = f"PAPER-{p_num_val:03d}-P{page_num:02d}"

            final_items.append(
                ResearchPaperSearchResultItem(
                    paper_id=paper.id,
                    evidence_id=evidence_id,
                    paper_index=p_num_val,
                    title=paper.title,
                    authors=paper.authors,
                    publication_year=paper.publication_year,
                    research_domain=paper.research_domain,
                    page_number=page_num,
                    matched_sections=sections,
                    matched_dimensions=dims,
                    relevance_score=score,
                    snippet=snippet,
                    source_filename=paper.source_filename,
                )
            )

        return ResearchPaperSearchResponse(
            query_summary={"query": query_text, "domain": request.research_domain, "top_k": request.top_k},
            total_papers_evaluated=len(papers),
            results_count=len(final_items),
            disclaimer=PAPER_DISCLAIMER,
            results=final_items,
        )

    def _extract_tokens(self, text: str) -> set[str]:
        clean = re.sub(r"[^\w\s]", "", text.lower())
        tokens = set(clean.split())
        stopwords = {"and", "the", "for", "with", "using", "paper", "data", "system", "real", "time", "based"}
        return {t for t in tokens if len(t) > 2 and t not in stopwords}

    def _determine_matched_dimensions(self, q_tokens: set[str], page_text: str, paper: ResearchPaper) -> list[str]:
        dims: list[str] = []
        lower_page = page_text.lower()
        lower_title = paper.title.lower()

        if q_tokens.intersection(self._extract_tokens(lower_title)):
            dims.append("title")

        if paper.abstract and q_tokens.intersection(self._extract_tokens(paper.abstract)):
            dims.append("abstract")

        tech_terms = {"vibration", "temperature", "telemetry", "sensor", "iot", "lstm", "random forest", "neural", "learning"}
        if any(term in lower_page for term in tech_terms):
            dims.append("technology")

        method_terms = {"methodology", "algorithm", "architecture", "feature extraction", "processing", "model"}
        if any(term in lower_page for term in method_terms):
            dims.append("methodology")

        exp_terms = {"experiment", "field trial", "test", "dataset", "precision", "recall", "f1", "anomaly"}
        if any(term in lower_page for term in exp_terms):
            dims.append("experiment")

        return dims

    def _build_snippet(self, page_text: str, overlap: set[str]) -> str:
        lines = page_text.split("\n")
        for line in lines:
            if any(term in line.lower() for term in overlap):
                return line.strip()[:300]
        return page_text[:250].strip() + ("..." if len(page_text) > 250 else "")
