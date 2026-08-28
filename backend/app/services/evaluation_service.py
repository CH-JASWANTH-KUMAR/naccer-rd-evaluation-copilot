from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.evaluation import Evaluation, EvaluationCriterion
from app.models.evaluation_audit import EvaluationAuditEvent
from app.models.evaluation_evidence import EvaluationEvidence
from app.models.proposal import Proposal
from app.schemas.evaluation import EvaluationCreate, EvaluationEvidenceCreate, EvaluationRead, EvaluationUpdate
from app.services.financial_compliance import FinancialComplianceService
from app.services.historical_search_service import HistoricalProjectSearchService
from app.services.proposal_completeness import ProposalCompletenessService
from app.services.rubric_service import RubricService


class EvaluationService:
    def __init__(self, db: Session):
        self.db = db
        self.rubric_service = RubricService(db)

    def create_evaluation(self, data: EvaluationCreate) -> EvaluationRead:
        # Check proposal existence
        proposal = self.db.query(Proposal).filter(Proposal.id == data.proposal_id).first()
        if not proposal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Proposal with ID '{data.proposal_id}' not found.",
            )

        # Reuse existing draft evaluation if present
        existing = (
            self.db.query(Evaluation)
            .filter(Evaluation.proposal_id == data.proposal_id, Evaluation.reviewer_id == data.reviewer_id)
            .first()
        )
        if existing:
            return self.get_evaluation_by_id(existing.id)

        # Get active rubric for version binding
        rubric = self.rubric_service.get_or_create_active_rubric()

        evaluation = Evaluation(
            proposal_id=proposal.id,
            reviewer_id=data.reviewer_id,
            rubric_id=rubric.id,
            rubric_version=rubric.version,
            status="DRAFT",
            reviewer_recommendation="FAVORABLE_WITH_CONDITIONS",
            started_at=datetime.now(UTC),
        )
        self.db.add(evaluation)
        self.db.commit()
        self.db.refresh(evaluation)

        # Snapshot rubric criteria for version stability
        for r_crit in rubric.criteria:
            e_crit = EvaluationCriterion(
                evaluation_id=evaluation.id,
                criterion_key=r_crit.key,
                name=r_crit.name,
                description=r_crit.description,
                max_score=r_crit.max_score,
                weight=r_crit.weight,
                score=None,
                weighted_score=None,
            )
            self.db.add(e_crit)

        self.db.commit()
        self.db.refresh(evaluation)

        # Auto-Populate Preliminary Evidence Items from P0.5 & P0.4
        self._populate_initial_evidence(evaluation, proposal)

        # Audit Event
        self._record_audit(evaluation.id, data.reviewer_id, "EVALUATION_STARTED", None, "DRAFT")

        return self.get_evaluation_by_id(evaluation.id)

    def get_evaluation_by_id(self, evaluation_id: str) -> EvaluationRead:
        stmt = (
            select(Evaluation)
            .options(
                joinedload(Evaluation.proposal).joinedload(Proposal.institution),
                joinedload(Evaluation.criteria),
                joinedload(Evaluation.evidences),
            )
            .where(Evaluation.id == evaluation_id)
        )
        eval_item = self.db.scalars(stmt).unique().first()
        if not eval_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Evaluation with ID '{evaluation_id}' not found.",
            )
        return EvaluationRead.model_validate(eval_item)

    def get_evaluations_list(
        self, proposal_id: str | None = None, status_filter: str | None = None
    ) -> list[EvaluationRead]:
        stmt = (
            select(Evaluation)
            .options(
                joinedload(Evaluation.proposal).joinedload(Proposal.institution),
                joinedload(Evaluation.criteria),
            )
            .order_by(Evaluation.created_at.desc())
        )
        if proposal_id:
            stmt = stmt.where(Evaluation.proposal_id == proposal_id)
        if status_filter:
            stmt = stmt.where(Evaluation.status == status_filter)

        evals = self.db.scalars(stmt).unique().all()
        return [EvaluationRead.model_validate(e) for e in evals]

    def update_evaluation_draft(self, evaluation_id: str, data: EvaluationUpdate) -> EvaluationRead:
        evaluation = self.db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
        if not evaluation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Evaluation with ID '{evaluation_id}' not found.",
            )

        if evaluation.status == "SUBMITTED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Submitted evaluations are read-only and cannot be altered.",
            )

        if data.reviewer_summary is not None:
            evaluation.reviewer_summary = data.reviewer_summary
        if data.reviewer_recommendation is not None:
            evaluation.reviewer_recommendation = data.reviewer_recommendation

        # Update criteria scores & comments
        if data.criteria:
            for item in data.criteria:
                crit = self.db.query(EvaluationCriterion).filter(
                    EvaluationCriterion.id == item.id,
                    EvaluationCriterion.evaluation_id == evaluation.id,
                ).first()
                if crit:
                    prev_val = f"score={crit.score}"
                    if item.score is not None:
                        crit.score = min(max(item.score, 0.0), crit.max_score)
                        crit.weighted_score = (crit.score / crit.max_score) * crit.weight
                    if item.comments is not None:
                        crit.comments = item.comments
                    if item.justification_notes is not None:
                        crit.justification_notes = item.justification_notes

                    self._record_audit(
                        evaluation.id, evaluation.reviewer_id, "SCORE_UPDATED", prev_val, f"score={crit.score}"
                    )

        # Recalculate Overall Score
        self._recalculate_overall_score(evaluation)

        self.db.commit()
        return self.get_evaluation_by_id(evaluation.id)

    def submit_evaluation(self, evaluation_id: str) -> EvaluationRead:
        evaluation = self.db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
        if not evaluation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Evaluation with ID '{evaluation_id}' not found.",
            )

        # Validation: Check mandatory criteria scores and required justifications
        unscored = [c.name for c in evaluation.criteria if c.score is None]
        if unscored:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Cannot submit evaluation: missing scores for criteria ({', '.join(unscored)}).",
            )

        # Validation: Justification required for low scores (<= 5.0)
        low_unjustified = [
            c.name for c in evaluation.criteria if (c.score or 0) <= 5.0 and not c.justification_notes
        ]
        if low_unjustified:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Low score justification required for criteria: ({', '.join(low_unjustified)}).",
            )

        evaluation.status = "SUBMITTED"
        evaluation.completed_at = datetime.now(UTC)
        self.db.commit()

        self._record_audit(evaluation.id, evaluation.reviewer_id, "EVALUATION_SUBMITTED", "DRAFT", "SUBMITTED")
        return self.get_evaluation_by_id(evaluation.id)

    def add_evaluation_evidence(self, evaluation_id: str, data: EvaluationEvidenceCreate) -> EvaluationRead:
        evaluation = self.db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
        if not evaluation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Evaluation with ID '{evaluation_id}' not found.",
            )

        evidence = EvaluationEvidence(
            evaluation_id=evaluation.id,
            criterion_id=data.criterion_id,
            evidence_type=data.evidence_type,
            source_type=data.source_type,
            source_reference=data.source_reference,
            source_page_start=data.source_page_start,
            source_page_end=data.source_page_end,
            evidence_text=data.evidence_text,
            reviewer_note=data.reviewer_note,
        )
        self.db.add(evidence)
        self.db.commit()

        self._record_audit(evaluation.id, evaluation.reviewer_id, "EVIDENCE_ADDED", None, data.evidence_text[:100])
        return self.get_evaluation_by_id(evaluation.id)

    def generate_draft_summary(self, evaluation_id: str) -> dict[str, str]:
        evaluation = self.db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
        if not evaluation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Evaluation with ID '{evaluation_id}' not found.",
            )

        strengths = [c.name for c in evaluation.criteria if (c.score or 0) >= 8.0]
        concerns = [c.name for c in evaluation.criteria if (c.score or 0) <= 5.0]

        summary_text = (
            f"EVALUATION SUMMARY DRAFT:\n"
            f"Overall Score: {evaluation.overall_score or 0.0:.1f} / 10.0\n"
            f"Strengths: {', '.join(strengths) if strengths else 'Standard technical compliance'}\n"
            f"Areas of Concern: {', '.join(concerns) if concerns else 'None identified'}\n"
            f"Preliminary Scrutiny: Completeness ({evaluation.proposal.completeness_status}), Financial ({evaluation.proposal.compliance_status})"
        )

        return {"draft_summary": summary_text}

    def _recalculate_overall_score(self, evaluation: Evaluation) -> None:
        total_weight = sum(c.weight for c in evaluation.criteria)
        if total_weight <= 0:
            return

        weighted_sum = sum(c.weighted_score or 0.0 for c in evaluation.criteria if c.weighted_score is not None)
        # Normalize to 0-10 scale
        evaluation.overall_score = round((weighted_sum / total_weight) * 10.0, 2)

    def _populate_initial_evidence(self, evaluation: Evaluation, proposal: Proposal) -> None:
        # 1. P0.5 Completeness Evidence
        comp = ProposalCompletenessService.evaluate_completeness(proposal)
        self.db.add(
            EvaluationEvidence(
                evaluation_id=evaluation.id,
                evidence_type="COMPLETENESS_CHECK",
                source_type="PROPOSAL",
                source_reference="P0.5 Scrutiny Checklist Engine",
                evidence_text=f"Completeness Status: {comp.status}. Missing Fields: {', '.join(comp.missing_fields) if comp.missing_fields else 'None'}.",
            )
        )

        # 2. P0.5 Financial Evidence
        fin = FinancialComplianceService.evaluate_financial_compliance(proposal)
        self.db.add(
            EvaluationEvidence(
                evaluation_id=evaluation.id,
                evidence_type="FINANCIAL_CHECK",
                source_type="PROPOSAL",
                source_reference="P0.5 Financial Rules Engine",
                evidence_text=f"Financial Status: {fin.status}. Declared Total: Rs. {fin.declared_total:,.2f}. Arithmetic Mismatch: {fin.arithmetic_mismatch}.",
            )
        )

        # 3. P0.4 Historical Benchmark Similarity Evidence
        try:
            search_service = HistoricalProjectSearchService(self.db)
            from app.schemas.search import SimilaritySearchRequest
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
                    top_k=2,
                )
            )
            for item in res.results:
                self.db.add(
                    EvaluationEvidence(
                        evaluation_id=evaluation.id,
                        evidence_type="HISTORICAL_BENCHMARK",
                        source_type="HISTORICAL_PROJECT",
                        source_reference=f"Project Code: {item.project_code} ({item.provenance.source})",
                        source_page_start=item.provenance.source_page_start,
                        source_page_end=item.provenance.source_page_end,
                        evidence_text=f"Historical Project Overlap ({item.similarity_percentage}% similarity): '{item.project_title}'. Matched Concepts: {', '.join(item.matched_fields)}.",
                    )
                )
        except Exception:
            pass

        self.db.commit()

    def _record_audit(
        self,
        evaluation_id: str,
        actor_id: str,
        action: str,
        prev_val: str | None,
        new_val: str | None,
        criterion_id: str | None = None,
    ) -> None:
        audit = EvaluationAuditEvent(
            evaluation_id=evaluation_id,
            actor_id=actor_id,
            action=action,
            criterion_id=criterion_id,
            previous_value=prev_val,
            new_value=new_val,
        )
        self.db.add(audit)
        self.db.commit()
