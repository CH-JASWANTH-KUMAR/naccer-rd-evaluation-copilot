"""Evidence Readiness Score Service.

Deterministically calculates the transparent 0-100 Evidence Readiness Score summarizing
available evaluation evidence across completeness, scientific coverage, MoC guideline rubric,
financial verification, historical/literature support, and reviewer completion.

CRITICAL POLICY ENFORCEMENT:
- System NEVER predicts approval, rejection, funding, or publication probability.
- Neutral interpretations only (Strong, Moderate, Attention Required, Substantial Gaps).
- Explainable score components with contributing check lists.
"""

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.evaluation import Evaluation
from app.models.proposal import Proposal
from app.schemas.evidence_readiness import (
    EvidenceReadinessComponentDetail,
    EvidenceReadinessItem,
    EvidenceReadinessScoreResponse,
)
from app.services.financial_compliance import FinancialComplianceService
from app.services.proposal_completeness import ProposalCompletenessService
from app.services.proposal_scientific_comparison_service import ProposalScientificComparisonService
from app.services.rubric_evidence_engine import RubricEvidenceEngine


class EvidenceReadinessService:
    def __init__(self, db: Session):
        self.db = db

    def calculate_evidence_readiness(self, proposal_id: str) -> EvidenceReadinessScoreResponse:
        proposal = self.db.scalars(select(Proposal).where(Proposal.id == proposal_id)).first()
        if not proposal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Proposal with ID '{proposal_id}' not found.",
            )

        is_demo = bool(
            "[DEMO]" in (proposal.title or "")
            or "[DEMO DATA]" in (proposal.title or "")
            or "PRED-MAINT" in (proposal.proposal_reference or "")
        )

        # 1. Component A: Proposal Completeness (max 20 pts)
        comp_report = ProposalCompletenessService.evaluate_completeness(proposal)
        missing_count = len(comp_report.missing_fields)
        if missing_count == 0:
            score_a = 20.0
            status_a = "COMPLETE"
            expl_a = "All mandatory proposal fields are fully specified in the document."
            checks_a = ["All 10 required proposal sections present."]
        else:
            score_a = max(0.0, round(20.0 * (1.0 - (missing_count / 10.0)), 1))
            status_a = "PARTIAL"
            expl_a = f"{missing_count} mandatory proposal field(s) missing or incomplete."
            checks_a = [f"Missing fields: {', '.join(comp_report.missing_fields)}"]

        # 2. Component B: Scientific Evidence Coverage (max 20 pts)
        sci_report = ProposalScientificComparisonService(self.db).generate_comparison(proposal_id)
        matching_count = sci_report.comparison_summary.get("matching", 0) + sci_report.comparison_summary.get(
            "partially_matching", 0
        )
        total_dims = len(sci_report.comparisons) if sci_report.comparisons else 4
        score_b = round(min(20.0, (matching_count / max(1, total_dims)) * 20.0), 1)
        status_b = "HIGH_COVERAGE" if score_b >= 15.0 else "PARTIAL_COVERAGE"
        expl_b = f"{matching_count}/{total_dims} scientific methodology dimensions covered by extracted evidence."
        checks_b = [f"{c.dimension}: {c.comparison_status}" for c in sci_report.comparisons[:4]]

        # 3. Component C: MoC Guideline Evidence Coverage (max 20 pts)
        rubric_res = RubricEvidenceEngine(self.db).evaluate_proposal_rubric_matrix(proposal_id)
        raw_criteria = rubric_res.get("criteria", []) if isinstance(rubric_res, dict) else getattr(rubric_res, "criteria", [])
        grounded_count = sum(
            1
            for r in raw_criteria
            if (r.get("evidence_matrix") if isinstance(r, dict) else getattr(r, "evidence_matrix", None))
        )
        total_criteria = len(raw_criteria) if raw_criteria else 8
        score_c = round((grounded_count / max(1, total_criteria)) * 20.0, 1)
        status_c = "GROUNDED" if score_c >= 15.0 else "PARTIAL"
        expl_c = f"{grounded_count}/{total_criteria} MoC guideline evaluation criteria supported by verified evidence."
        checks_c = [
            f"Criterion '{r.get('name') if isinstance(r, dict) else getattr(r, 'name', '')}': Grounded"
            for r in raw_criteria[:4]
        ]
        if not checks_c:
            checks_c = ["MoC guideline criteria evaluation in progress."]

        # 4. Component D: Financial Verification (max 15 pts)
        fin_report = FinancialComplianceService.evaluate_financial_compliance(proposal)
        if fin_report.status == "COMPLIANT":
            score_d = 15.0
            status_d = "VERIFIED"
            expl_d = "Budget component breakdown sum matches declared total budget."
            checks_d = ["Declared total budget matches component arithmetic sum."]
        elif fin_report.extraction_summary_status == "PARTIAL_BREAKDOWN":
            score_d = 10.0
            status_d = "PARTIAL"
            expl_d = "Partial budget breakdown extracted. Some cost heads missing."
            checks_d = ["Partial itemized budget heads extracted from proposal."]
        elif fin_report.status == "NEEDS_JUSTIFICATION":
            score_d = 5.0
            status_d = "NEEDS_JUSTIFICATION"
            expl_d = "No itemized budget components extracted; declared total unverified."
            checks_d = ["Itemized cost component breakdown was not identified."]
        else:
            score_d = 0.0
            status_d = "FLAGGED"
            expl_d = f"Financial arithmetic mismatch error: Rs. {fin_report.difference_amount:,.2f} variance."
            checks_d = [f"Arithmetic mismatch: Rs. {fin_report.difference_amount:,.2f} difference."]

        # 5. Component E: Historical & Research Literature Support (max 15 pts)
        hist_count = len(sci_report.evidence_sources)
        if hist_count >= 3:
            score_e = 15.0
            status_e = "STRONG_SUPPORT"
            expl_e = "Multiple relevant historical CIL projects and research papers identified."
            checks_e = [f"{hist_count} evidence sources linked with high relevance."]
        elif hist_count > 0:
            score_e = 10.0
            status_e = "MODERATE_SUPPORT"
            expl_e = f"{hist_count} prior art evidence source(s) identified."
            checks_e = [f"{hist_count} evidence sources found in knowledge base."]
        else:
            score_e = 5.0
            status_e = "LIMITED_SUPPORT"
            expl_e = "Limited historical CIL project or research paper prior art found."
            checks_e = ["No direct historical project matches found."]

        # 6. Component F: Reviewer Evaluation Completion (max 10 pts)
        eval_item = self.db.scalars(select(Evaluation).where(Evaluation.proposal_id == proposal_id)).first()
        if eval_item and eval_item.assignments:
            completed_n = sum(1 for a in eval_item.assignments if a.status == "COMPLETED")
            total_n = len(eval_item.assignments)
            score_f = round((completed_n / max(1, total_n)) * 10.0, 1)
            status_f = "COMPLETE" if completed_n == total_n else "IN_PROGRESS"
            expl_f = f"{completed_n}/{total_n} assigned independent reviewer assessments submitted."
            checks_f = [f"Reviewer assessment completion: {completed_n}/{total_n}"]
        elif eval_item and eval_item.status == "SUBMITTED":
            score_f = 10.0
            status_f = "COMPLETE"
            expl_f = "Assigned reviewer assessment submitted."
            checks_f = ["Reviewer assessment submitted."]
        else:
            score_f = 0.0
            status_f = "PENDING"
            expl_f = "Independent reviewer assessments pending submission."
            checks_f = ["Reviewer assessments pending."]

        total_score = min(100, int(round(score_a + score_b + score_c + score_d + score_e + score_f)))

        # Interpretation Labels (Neutral Language only)
        if total_score >= 80:
            interp = "Strong evidence coverage"
        elif total_score >= 60:
            interp = "Moderate evidence coverage"
        elif total_score >= 40:
            interp = "Evidence gaps require reviewer attention"
        else:
            interp = "Substantial evidence gaps"

        components = [
            EvidenceReadinessComponentDetail(
                name="Proposal Completeness",
                score=score_a,
                max_score=20.0,
                status=status_a,
                explanation=expl_a,
                contributing_checks=checks_a,
            ),
            EvidenceReadinessComponentDetail(
                name="Scientific Evidence Coverage",
                score=score_b,
                max_score=20.0,
                status=status_b,
                explanation=expl_b,
                contributing_checks=checks_b,
            ),
            EvidenceReadinessComponentDetail(
                name="MoC Guideline Evidence Coverage",
                score=score_c,
                max_score=20.0,
                status=status_c,
                explanation=expl_c,
                contributing_checks=checks_c,
            ),
            EvidenceReadinessComponentDetail(
                name="Financial Verification",
                score=score_d,
                max_score=15.0,
                status=status_d,
                explanation=expl_d,
                contributing_checks=checks_d,
            ),
            EvidenceReadinessComponentDetail(
                name="Historical / Research Evidence Support",
                score=score_e,
                max_score=15.0,
                status=status_e,
                explanation=expl_e,
                contributing_checks=checks_e,
            ),
            EvidenceReadinessComponentDetail(
                name="Reviewer Evaluation Completion",
                score=score_f,
                max_score=10.0,
                status=status_f,
                explanation=expl_f,
                contributing_checks=checks_f,
            ),
        ]

        # Strengths & Attention Required Items with valid evidence IDs
        strengths: list[EvidenceReadinessItem] = []
        attention: list[EvidenceReadinessItem] = []

        # Populate Strengths
        for s in sci_report.evidence_sources[:3]:
            strengths.append(
                EvidenceReadinessItem(
                    evidence_id=s.evidence_id,
                    title=f"Prior Art Support: {s.title}",
                    description=f"Surfaced {s.source_type.lower()} record matching domain concepts.",
                    source_type=s.source_type,
                )
            )
        if score_a == 20.0:
            strengths.append(
                EvidenceReadinessItem(
                    evidence_id="PROP-COMPLETENESS",
                    title="Complete Proposal Structuring",
                    description="All mandatory sections and technical fields reported in PDF document.",
                    source_type="PROPOSAL",
                )
            )

        # Populate Attention Required
        for g in sci_report.evidence_gaps[:3]:
            attention.append(
                EvidenceReadinessItem(
                    evidence_id=f"GAP-{g.dimension[:6].upper()}",
                    title=f"Technical Gap: {g.dimension}",
                    description=g.gap,
                    source_type="EVIDENCE_GAP",
                )
            )
        if fin_report.status != "COMPLIANT":
            attention.append(
                EvidenceReadinessItem(
                    evidence_id="FIN-BREAKDOWN",
                    title="Financial Breakdown Verification",
                    description=fin_report.explanation,
                    source_type="FINANCIAL_SCRUTINY",
                )
            )

        return EvidenceReadinessScoreResponse(
            proposal_id=proposal_id,
            total_score=total_score,
            interpretation_label=interp,
            is_demo=is_demo,
            proposal_completeness_score=score_a,
            scientific_evidence_coverage_score=score_b,
            moc_guideline_coverage_score=score_c,
            financial_verification_score=score_d,
            historical_research_support_score=score_e,
            reviewer_completion_score=score_f,
            components=components,
            strengths=strengths,
            attention_required=attention,
        )
