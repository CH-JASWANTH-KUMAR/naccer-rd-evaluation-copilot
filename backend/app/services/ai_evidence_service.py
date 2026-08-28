import json
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ai_analysis import AIAnalysis
from app.models.evaluation import Evaluation
from app.models.evaluation_audit import EvaluationAuditEvent
from app.schemas.ai_analysis import AIAnalysisRead, AIAnalysisResult
from app.schemas.search import SimilarityResultItem, SimilaritySearchRequest
from app.services.ai_analysis_provider import AIProviderFactory
from app.services.citation_validator import CitationValidator
from app.services.financial_compliance import FinancialComplianceService
from app.services.historical_search_service import HistoricalProjectSearchService
from app.services.proposal_completeness import ProposalCompletenessService
from app.services.rag_context_builder import RAGContextBuilder, RAGEvidencePackage


class AIEvidenceService:
    def __init__(self, db: Session):
        self.db = db

    def get_or_generate_analysis(self, evaluation_id: str) -> AIAnalysisRead:
        evaluation = self._get_evaluation(evaluation_id)
        context, rag_package = self._build_rag_evidence_package(evaluation)
        input_hash = rag_package.context_hash

        # Check for existing cached analysis snapshot matching input_hash
        stmt = (
            select(AIAnalysis)
            .where(AIAnalysis.evaluation_id == evaluation.id, AIAnalysis.input_hash == input_hash)
            .order_by(AIAnalysis.created_at.desc())
        )
        cached = self.db.scalars(stmt).first()
        if cached:
            return self._to_read_schema(cached)

        # Generate new RAG analysis snapshot
        return self._generate_new_snapshot(evaluation, context, rag_package)

    def refresh_analysis(self, evaluation_id: str) -> AIAnalysisRead:
        evaluation = self._get_evaluation(evaluation_id)
        context, rag_package = self._build_rag_evidence_package(evaluation)

        # Force generation of fresh analysis snapshot
        return self._generate_new_snapshot(
            evaluation, context, rag_package, action_name="AI_ANALYSIS_REFRESHED"
        )

    def _get_evaluation(self, evaluation_id: str) -> Evaluation:
        eval_item = self.db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
        if not eval_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Evaluation with ID '{evaluation_id}' not found.",
            )
        return eval_item

    def _build_rag_evidence_package(
        self, evaluation: Evaluation
    ) -> tuple[dict[str, Any], RAGEvidencePackage]:
        proposal = evaluation.proposal
        comp = ProposalCompletenessService.evaluate_completeness(proposal)
        fin = FinancialComplianceService.evaluate_financial_compliance(proposal)

        # P0.4 Historical Benchmark Search Integration
        historical_results: list[SimilarityResultItem] = []
        historical_items: list[dict[str, Any]] = []
        try:
            search_service = HistoricalProjectSearchService(self.db)
            res = search_service.search_similar_projects(
                SimilaritySearchRequest(
                    title=proposal.title,
                    objectives=proposal.objectives,
                    problem_statement=proposal.problem_statement,
                    methodology=proposal.methodology,
                    technology=proposal.technology,
                    expected_outcomes=proposal.expected_outcomes,
                    domain=proposal.domain,
                    institution=proposal.institution.name if proposal.institution else None,
                    top_k=5,
                )
            )
            historical_results = res.results
            for r in res.results:
                historical_items.append(
                    {
                        "project_code": r.project_code,
                        "project_title": r.project_title,
                        "approved_cost": r.approved_cost,
                        "similarity_percentage": r.similarity_percentage,
                        "matched_fields": r.matched_fields,
                        "provenance": {
                            "source": r.provenance.source,
                            "source_page_start": r.provenance.source_page_start,
                            "source_page_end": r.provenance.source_page_end,
                        },
                    }
                )
        except Exception:
            pass

        completeness_dict = {"status": comp.status, "missing_fields": comp.missing_fields}
        financial_dict = {
            "status": fin.status,
            "declared_total": fin.declared_total,
            "arithmetic_mismatch": fin.arithmetic_mismatch,
        }

        # Build RAGEvidencePackage
        rag_package = RAGContextBuilder.build_context_package(
            evaluation=evaluation,
            proposal=proposal,
            completeness=completeness_dict,
            financial=financial_dict,
            historical_results=historical_results,
        )

        criteria_list = [
            {
                "id": c.id,
                "key": c.criterion_key or c.name,
                "name": c.name,
                "description": c.description,
                "weight": c.weight,
                "score": c.score,
                "comments": c.comments,
            }
            for c in evaluation.criteria
        ]

        context = {
            "proposal": {
                "id": proposal.id,
                "title": proposal.title,
                "problem_statement": proposal.problem_statement,
                "objectives": proposal.objectives,
                "methodology": proposal.methodology,
                "technology": proposal.technology,
                "expected_outcomes": proposal.expected_outcomes,
                "duration_months": proposal.duration_months,
                "budget_total": proposal.budget_total,
                "institution": proposal.institution.name if proposal.institution else None,
            },
            "completeness": completeness_dict,
            "financial": financial_dict,
            "historical": historical_items,
            "criteria": criteria_list,
        }

        return context, rag_package

    def _generate_new_snapshot(
        self,
        evaluation: Evaluation,
        context: dict[str, Any],
        rag_package: RAGEvidencePackage,
        action_name: str = "AI_ANALYSIS_GENERATED",
    ) -> AIAnalysisRead:
        provider = AIProviderFactory.get_provider()
        raw_result: AIAnalysisResult = provider.analyze_evidence(context, rag_package)

        # Validate citations and enrich evidence references from RAG context
        validated_result = CitationValidator.validate_and_enrich_result(
            result=raw_result,
            valid_evidence_ids=rag_package.valid_evidence_ids,
            evidence_id_map=rag_package.evidence_id_map,
        )

        analysis = AIAnalysis(
            evaluation_id=evaluation.id,
            provider=provider.provider_name,
            model=provider.model_name,
            prompt_version=provider.prompt_version,
            input_hash=rag_package.context_hash,
            output_json=validated_result.model_dump_json(),
            status="GENERATED",
        )
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)

        # Audit Event
        self.db.add(
            EvaluationAuditEvent(
                evaluation_id=evaluation.id,
                actor_id=evaluation.reviewer_id,
                action=action_name,
                new_value=f"provider={provider.provider_name}, hash={rag_package.context_hash[:10]}",
            )
        )
        self.db.commit()

        return self._to_read_schema(analysis)

    def _to_read_schema(self, snapshot: AIAnalysis) -> AIAnalysisRead:
        raw_result = json.loads(snapshot.output_json)
        result_model = AIAnalysisResult.model_validate(raw_result)

        return AIAnalysisRead(
            id=snapshot.id,
            evaluation_id=snapshot.evaluation_id,
            provider=snapshot.provider,
            model=snapshot.model,
            prompt_version=snapshot.prompt_version,
            input_hash=snapshot.input_hash,
            status=snapshot.status,
            created_at=snapshot.created_at,
            analysis_result=result_model,
        )
