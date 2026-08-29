import json
import re

from sqlalchemy.orm import Session

from app.models.historical_project import HistoricalProject
from app.models.historical_project_embedding import HistoricalProjectEmbedding
from app.repositories.projects import HistoricalProjectRepository
from app.schemas.search import (
    EvidenceItemRead,
    ProvenanceRead,
    SimilarityResultItem,
    SimilaritySearchRequest,
    SimilaritySearchResponse,
)
from app.services.embedding_provider import EmbeddingProviderFactory, calculate_cosine_similarity

REVIEWER_DISCLAIMER = "Similarity results are evidence for reviewer assessment and do not constitute an automated novelty or duplication decision."


class HistoricalProjectSearchService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = HistoricalProjectRepository(db)
        self.provider = EmbeddingProviderFactory.get_provider()

    def search_similar_projects(self, request: SimilaritySearchRequest) -> SimilaritySearchResponse:
        # 1. Combine query text
        query_text = self._build_combined_query_text(request)
        if not query_text.strip():
            return SimilaritySearchResponse(
                query_summary={"search_terms": "empty"},
                total_candidates_evaluated=0,
                results_count=0,
                disclaimer=REVIEWER_DISCLAIMER,
                results=[],
            )

        query_vector = self.provider.embed_text(query_text)
        query_tokens = self._extract_tokens(query_text)

        # 2. Retrieve candidates
        candidates = self.repo.get_all(
            domain=request.domain if request.domain else None,
            institution=request.institution if request.institution else None,
        )
        if not candidates:
            # Fallback to all projects if domain filter returned no results
            candidates = self.repo.get_all()

        results: list[SimilarityResultItem] = []

        for proj in candidates:
            # Retrieve or generate project embedding vector
            proj_vector = self._get_or_create_project_embedding(proj)

            # Calculate Component Scores
            sem_score = calculate_cosine_similarity(query_vector, proj_vector)

            title_score = self._calculate_token_overlap(query_tokens, self._extract_tokens(proj.title))
            obj_text = f"{proj.objectives or ''} {proj.raw_record_text or ''}"
            obj_score = self._calculate_token_overlap(query_tokens, self._extract_tokens(obj_text))
            tech_score = self._calculate_token_overlap(query_tokens, self._extract_tokens(proj.technology or ""))

            domain_score = 1.0 if request.domain and request.domain.lower() in proj.domain.lower() else 0.0

            # Explainable Composite Ranking Weighting Formula
            # Composite = 0.40*Semantic + 0.25*Title + 0.20*Objective + 0.10*Tech + 0.05*Domain
            raw_composite = (
                0.40 * sem_score + 0.25 * title_score + 0.20 * obj_score + 0.10 * tech_score + 0.05 * domain_score
            )

            final_score = round(max(0.0, min(1.0, float(raw_composite))), 4)
            similarity_pct = int(round(final_score * 100))

            if final_score < 0.05:
                continue

            # Classify Relationship
            if final_score >= 0.65:
                relationship = "POTENTIALLY_RELATED"
            elif final_score >= 0.35:
                relationship = "CONCEPTUAL_OVERLAP"
            else:
                relationship = "WEAK_RELATIONSHIP"

            # Extract Evidence Items, Matched Fields & Technical Dimensions
            matched_fields, matched_dimensions, evidence_items = self._extract_evidence(request, proj, final_score)

            # Build Provenance Record
            provenance = ProvenanceRead(
                source=proj.source,
                source_type=proj.source_type,
                source_url=proj.source_url,
                source_document_name=proj.source_document_name,
                source_page_start=proj.source_page_start,
                source_page_end=proj.source_page_end,
                source_record_identifier=proj.source_record_identifier or proj.project_code,
                verification_status=proj.verification_status,
                verification_timestamp=proj.verification_timestamp,
            )

            results.append(
                SimilarityResultItem(
                    project_id=proj.id,
                    project_code=proj.project_code,
                    evidence_id="HIST-000",  # Updated after sorting top-K
                    project_title=proj.title,
                    institution=proj.institution,
                    sub_implementing_agencies=proj.sub_implementing_agencies,
                    domain=proj.domain,
                    status=proj.status,
                    approved_cost=proj.approved_cost,
                    approved_cost_raw=proj.approved_cost_raw,
                    similarity_score=final_score,
                    similarity_percentage=similarity_pct,
                    relationship=relationship,
                    matched_fields=matched_fields,
                    matched_dimensions=matched_dimensions,
                    evidence=evidence_items,
                    provenance=provenance,
                    summary=proj.objectives or proj.raw_record_text,
                    raw_record_text=proj.raw_record_text,
                )
            )

        # Sort descending by similarity score
        results.sort(key=lambda r: r.similarity_score, reverse=True)
        top_results = results[: request.top_k]

        # Assign deterministic Evidence IDs (HIST-001, HIST-002, etc.)
        for idx, item in enumerate(top_results, start=1):
            item.evidence_id = f"HIST-{idx:03d}"

        return SimilaritySearchResponse(
            query_summary={
                "title": request.title,
                "domain": request.domain,
                "technology": request.technology,
                "top_k": request.top_k,
            },
            total_candidates_evaluated=len(candidates),
            results_count=len(top_results),
            disclaimer=REVIEWER_DISCLAIMER,
            results=top_results,
        )

    def reindex_all_embeddings(self) -> int:
        """Pre-compute and cache embeddings for all historical projects."""
        projects = self.repo.get_all()
        count = 0
        for proj in projects:
            self._get_or_create_project_embedding(proj)
            count += 1
        return count

    def _get_or_create_project_embedding(self, proj: HistoricalProject) -> list[float]:
        text_content = (
            f"{proj.title} {proj.domain} {proj.objectives or ''} {proj.technology or ''} {proj.raw_record_text or ''}"
        )
        text_hash = str(hash(text_content))

        # Check existing stored embedding
        if proj.embeddings:
            for emb in proj.embeddings:
                if emb.embedding_model == self.provider.model_name and emb.text_hash == text_hash:
                    try:
                        return json.loads(emb.vector_data)
                    except Exception:
                        pass

        # Compute new vector
        vec = self.provider.embed_text(text_content)
        vec_json = json.dumps(vec)

        # Store in DB
        new_emb = HistoricalProjectEmbedding(
            historical_project_id=proj.id,
            embedding_model=self.provider.model_name,
            embedding_dimension=self.provider.dimension,
            vector_data=vec_json,
            text_hash=text_hash,
        )
        self.db.add(new_emb)
        self.db.commit()

        return vec

    def _build_combined_query_text(self, request: SimilaritySearchRequest) -> str:
        parts = []
        if request.title:
            parts.append(request.title)
        if request.objectives:
            parts.append(request.objectives)
        if request.problem_statement:
            parts.append(request.problem_statement)
        if request.methodology:
            parts.append(request.methodology)
        if request.technology:
            parts.append(request.technology)
        if request.expected_outcomes:
            parts.append(request.expected_outcomes)
        if request.domain:
            parts.append(request.domain)
        return " ".join(parts)

    def _extract_tokens(self, text: str) -> set[str]:
        clean = re.sub(r"[^\w\s]", "", text.lower())
        tokens = set(clean.split())
        stopwords = {"and", "the", "for", "with", "using", "project", "cil", "cmpdi", "data", "system", "real", "time"}
        return {t for t in tokens if len(t) > 2 and t not in stopwords}

    def _calculate_token_overlap(self, query_tokens: set[str], doc_tokens: set[str]) -> float:
        if not query_tokens or not doc_tokens:
            return 0.0
        intersection = query_tokens.intersection(doc_tokens)
        return len(intersection) / float(len(query_tokens))

    def _extract_evidence(
        self, request: SimilaritySearchRequest, proj: HistoricalProject, score: float
    ) -> tuple[list[str], list[str], list[EvidenceItemRead]]:
        matched_fields: list[str] = []
        matched_dimensions: list[str] = []
        evidence_items: list[EvidenceItemRead] = []

        q_tokens = self._extract_tokens(self._build_combined_query_text(request))
        strength = "DIRECT_MATCH" if score >= 0.65 else ("RELATED" if score >= 0.35 else "WEAKLY_RELATED")

        mining_keywords = {
            "coal", "mining", "equipment", "underground", "opencast", "sensor", "telemetry", "monitoring",
            "longwall", "continuous", "maintenance", "fire", "gas", "5g", "iot", "predictive", "strata", "paste"
        }

        # 1. Objective / Record Text Evidence
        if proj.objectives or proj.raw_record_text:
            rec_text = proj.objectives or proj.raw_record_text or ""
            rec_tokens = self._extract_tokens(rec_text)
            overlap = q_tokens.intersection(rec_tokens)
            if overlap:
                matched_fields.append("objective")
                matched_dimensions.append("objective")
                sample_terms = ", ".join(list(overlap)[:4])
                snippet = rec_text[:200] + ("..." if len(rec_text) > 200 else "")
                evidence_items.append(
                    EvidenceItemRead(
                        field="objective",
                        snippet=snippet,
                        reason=f"Stored project record contains overlapping concepts: {sample_terms}",
                        strength=strength,
                    )
                )

        # 2. Technology Evidence
        if proj.technology or (
            request.technology and request.technology.lower() in (proj.raw_record_text or "").lower()
        ):
            matched_fields.append("technology")
            matched_dimensions.append("technology")
            tech_str = proj.technology or "Specified R&D Tech Stack"
            evidence_items.append(
                EvidenceItemRead(
                    field="technology",
                    snippet=f"Technology / Methodologies: {tech_str}",
                    reason="Technical methodology or equipment concepts overlap with proposal requirements.",
                    strength=strength,
                )
            )

        # 3. Domain Evidence
        if request.domain and request.domain.lower() in proj.domain.lower():
            matched_fields.append("domain")
            matched_dimensions.append("domain")
            evidence_items.append(
                EvidenceItemRead(
                    field="domain",
                    snippet=f"Research Domain: {proj.domain}",
                    reason=f"Both project and proposal operate within the '{proj.domain}' domain.",
                    strength="DIRECT_MATCH",
                )
            )

        # 4. Title Evidence
        t_tokens = self._extract_tokens(proj.title)
        if q_tokens.intersection(t_tokens):
            if "title" not in matched_fields:
                matched_fields.append("title")
                matched_dimensions.append("title")
            evidence_items.append(
                EvidenceItemRead(
                    field="title",
                    snippet=f"Title: {proj.title}",
                    reason="Historical project title contains related technical keywords.",
                    strength=strength,
                )
            )

        # 5. Mining Context Dimension Check
        all_doc_text = f"{proj.title} {proj.domain} {proj.objectives or ''} {proj.technology or ''}".lower()
        doc_mining_tokens = self._extract_tokens(all_doc_text).intersection(mining_keywords)
        query_mining_tokens = q_tokens.intersection(mining_keywords)
        if query_mining_tokens.intersection(doc_mining_tokens):
            if "mining_context" not in matched_dimensions:
                matched_dimensions.append("mining_context")

        return matched_fields, matched_dimensions, evidence_items
