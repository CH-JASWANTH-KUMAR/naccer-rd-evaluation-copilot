import hashlib
import json
from datetime import UTC, datetime
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.decision_pack import EvaluationDecisionPack
from app.models.evaluation import Evaluation
from app.models.evaluation_audit import EvaluationAuditEvent
from app.schemas.search import SimilaritySearchRequest
from app.services.ai_evidence_service import AIEvidenceService
from app.services.financial_compliance import FinancialComplianceService
from app.services.historical_search_service import HistoricalProjectSearchService
from app.services.proposal_completeness import ProposalCompletenessService


class DecisionPackSafetyValidator:
    """Enforces safety boundaries on decision packs to prevent autonomous AI decision statements."""

    DISALLOWED_TERMS = [
        "AUTONOMOUS_APPROVAL",
        "AUTONOMOUS_REJECTION",
        "DECLARING_NOT_NOVEL",
        "DECLARING_DUPLICATE",
        "GRANTING_FUNDING_AMOUNT",
    ]

    @classmethod
    def validate_decision_pack(cls, content_dict: dict[str, Any]) -> None:
        text_check = json.dumps(content_dict, default=str).upper()
        for term in cls.DISALLOWED_TERMS:
            if term in text_check:
                raise ValueError(f"Decision pack contains prohibited autonomous decision term '{term}'.")


class ReviewerIntelligenceService:
    def __init__(self, db: Session):
        self.db = db

    def get_review_context(self, evaluation_id: str) -> dict[str, Any]:
        evaluation = self._get_evaluation(evaluation_id)
        proposal = evaluation.proposal

        # 1. P0.5 Scrutiny
        comp = ProposalCompletenessService.evaluate_completeness(proposal)
        fin = FinancialComplianceService.evaluate_financial_compliance(proposal)

        # 2. P0.4 Historical Benchmarks
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

        # 3. P0.8 RAG AI Analysis
        ai_service = AIEvidenceService(self.db)
        ai_analysis_data = None
        try:
            ai_res = ai_service.get_or_generate_analysis(evaluation_id)
            ai_analysis_data = ai_res.model_dump()
        except Exception:
            pass

        # 4. Review Progress & Scorecard
        criteria_list = [
            {
                "id": c.id,
                "criterion_key": c.criterion_key or c.name,
                "name": c.name,
                "description": c.description,
                "max_score": c.max_score,
                "weight": c.weight,
                "score": c.score,
                "weighted_score": c.weighted_score,
                "comments": c.comments,
                "justification_notes": c.justification_notes,
            }
            for c in evaluation.criteria
        ]

        scored_count = sum(1 for c in evaluation.criteria if c.score is not None)
        total_count = len(evaluation.criteria)
        progress_pct = round((scored_count / total_count * 100.0), 1) if total_count > 0 else 0.0

        # 5. Attention Items
        attention_items = self._build_attention_items(proposal, comp, fin, historical_items, evaluation.criteria)

        # 6. Evidence Coverage Matrix
        coverage_matrix = self._build_evidence_coverage_matrix(evaluation.criteria, evaluation.evidences, proposal, historical_items, fin)

        # 7. Audit Timeline
        audit_events = [
            {
                "id": a.id,
                "action": a.action,
                "actor_id": a.actor_id,
                "previous_value": a.previous_value,
                "new_value": a.new_value,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in sorted(evaluation.audit_events, key=lambda x: x.created_at, reverse=True)
        ]

        return {
            "evaluation": {
                "id": evaluation.id,
                "status": evaluation.status,
                "overall_score": evaluation.overall_score,
                "reviewer_id": evaluation.reviewer_id,
                "rubric_version": evaluation.rubric_version,
                "reviewer_summary": evaluation.reviewer_summary,
                "reviewer_recommendation": evaluation.reviewer_recommendation,
                "started_at": evaluation.started_at.isoformat() if evaluation.started_at else None,
                "completed_at": evaluation.completed_at.isoformat() if evaluation.completed_at else None,
            },
            "proposal": {
                "id": proposal.id,
                "proposal_reference": proposal.proposal_reference,
                "title": proposal.title,
                "institution": proposal.institution.name if proposal.institution else None,
                "principal_investigator": proposal.principal_investigator,
                "domain": proposal.domain,
                "duration_months": proposal.duration_months,
                "budget_total": proposal.budget_total,
                "problem_statement": proposal.problem_statement,
                "objectives": proposal.objectives,
                "methodology": proposal.methodology,
                "technology": proposal.technology,
                "expected_outcomes": proposal.expected_outcomes,
            },
            "scrutiny": {
                "completeness": {"status": comp.status, "missing_fields": comp.missing_fields},
                "financial": {
                    "status": fin.status,
                    "declared_total": fin.declared_total,
                    "arithmetic_mismatch": fin.arithmetic_mismatch,
                    "findings": [getattr(f, "finding_text", str(f)) for f in fin.findings],
                },
            },
            "historical_benchmarks": historical_items,
            "ai_analysis": ai_analysis_data,
            "scorecard": {
                "criteria": criteria_list,
                "overall_score": evaluation.overall_score,
                "progress_percentage": progress_pct,
                "criteria_scored": scored_count,
                "criteria_total": total_count,
            },
            "attention_items": attention_items,
            "evidence_coverage_matrix": coverage_matrix,
            "audit_events": audit_events,
        }

    def create_or_get_decision_pack(self, evaluation_id: str, generated_by: str = "Reviewer") -> dict[str, Any]:
        evaluation = self._get_evaluation(evaluation_id)
        context = self.get_review_context(evaluation_id)
        input_hash = hashlib.sha256(json.dumps(context, default=str, sort_keys=True).encode("utf-8")).hexdigest()

        # Check existing decision pack for matching input_hash
        stmt = (
            select(EvaluationDecisionPack)
            .where(EvaluationDecisionPack.evaluation_id == evaluation.id)
            .order_by(EvaluationDecisionPack.version.desc())
        )
        existing_packs = list(self.db.scalars(stmt).all())
        if existing_packs and existing_packs[0].input_hash == input_hash:
            pack = existing_packs[0]
            return {
                "id": pack.id,
                "evaluation_id": pack.evaluation_id,
                "version": pack.version,
                "input_hash": pack.input_hash,
                "generated_by": pack.generated_by,
                "status": pack.status,
                "created_at": pack.created_at.isoformat(),
                "content": json.loads(pack.content_json),
            }

        # Build new version
        new_version = (existing_packs[0].version + 1) if existing_packs else 1

        decision_pack_content = {
            "dossier_title": f"Technical Evaluation Decision Pack — {evaluation.proposal.proposal_reference}",
            "generated_at": datetime.now(UTC).isoformat(),
            "generated_by": generated_by,
            "version": f"v{new_version}",
            "review_context": context,
            "disclaimer": "This document is decision-support material. Final technical, novelty, funding, approval, and rejection decisions remain with authorized human reviewers.",
        }

        # Safety Validation
        DecisionPackSafetyValidator.validate_decision_pack(decision_pack_content)

        pack = EvaluationDecisionPack(
            evaluation_id=evaluation.id,
            version=new_version,
            input_hash=input_hash,
            generated_by=generated_by,
            content_json=json.dumps(decision_pack_content, default=str),
            status="FINALIZED",
        )
        self.db.add(pack)
        self.db.commit()
        self.db.refresh(pack)

        # Audit Event
        self.db.add(
            EvaluationAuditEvent(
                evaluation_id=evaluation.id,
                actor_id=generated_by,
                action="DECISION_PACK_GENERATED",
                new_value=f"version=v{new_version}, hash={input_hash[:10]}",
            )
        )
        self.db.commit()

        return {
            "id": pack.id,
            "evaluation_id": pack.evaluation_id,
            "version": pack.version,
            "input_hash": pack.input_hash,
            "generated_by": pack.generated_by,
            "status": pack.status,
            "created_at": pack.created_at.isoformat(),
            "content": decision_pack_content,
        }

    def generate_decision_pack_pdf_html(self, evaluation_id: str) -> str:
        pack_data = self.create_or_get_decision_pack(evaluation_id)
        content = pack_data["content"]
        ctx = content["review_context"]
        proposal = ctx["proposal"]
        eval_info = ctx["evaluation"]
        scrutiny = ctx["scrutiny"]
        scorecard = ctx["scorecard"]

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"/>
    <title>NaCCER R&D Evaluation Dossier - {proposal['proposal_reference']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; color: #1e293b; line-height: 1.5; }}
        h1 {{ color: #0f172a; font-size: 22px; border-bottom: 2px solid #2563eb; padding-bottom: 8px; }}
        h2 {{ color: #1e3a8a; font-size: 16px; margin-top: 24px; border-bottom: 1px solid #cbd5e1; padding-bottom: 4px; }}
        .badge {{ display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; background: #e2e8f0; color: #334155; }}
        .badge-success {{ background: #dcfce7; color: #166534; }}
        .badge-warning {{ background: #fef3c7; color: #92400e; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 13px; }}
        th, td {{ border: 1px solid #cbd5e1; padding: 8px; text-align: left; }}
        th {{ background-color: #f8fafc; font-weight: bold; }}
        .disclaimer {{ background: #eff6ff; border: 1px solid #bfdbfe; padding: 12px; margin-top: 30px; font-size: 12px; color: #1e40af; border-radius: 6px; }}
        .footer {{ margin-top: 40px; font-size: 11px; color: #64748b; text-align: center; border-top: 1px solid #e2e8f0; padding-top: 12px; }}
    </style>
</head>
<body>
    <h1>NaCCER R&D Evaluation Copilot — Technical Dossier</h1>
    <p><strong>Proposal Reference:</strong> {proposal['proposal_reference']} | <strong>Generated:</strong> {content['generated_at']} | <strong>Dossier Version:</strong> {pack_data['version']}</p>
    
    <h2>1. Executive Proposal Summary</h2>
    <p><strong>Title:</strong> {proposal['title']}</p>
    <p><strong>Submitting Institution:</strong> {proposal['institution'] or 'CMPDI Submitting Unit'} | <strong>PI:</strong> {proposal['principal_investigator']}</p>
    <p><strong>Domain:</strong> {proposal['domain']} | <strong>Duration:</strong> {proposal['duration_months']} months | <strong>Requested Budget:</strong> Rs. {proposal['budget_total']:,.2f}</p>

    <h2>2. Preliminary Scrutiny &amp; Compliance</h2>
    <p>
        <strong>Completeness Status:</strong> <span class="badge {'badge-success' if scrutiny['completeness']['status'] == 'COMPLETE' else 'badge-warning'}">{scrutiny['completeness']['status']}</span>
        &nbsp;&nbsp;&nbsp;&nbsp;
        <strong>Financial Status:</strong> <span class="badge {'badge-success' if scrutiny['financial']['status'] == 'COMPLIANT' else 'badge-warning'}">{scrutiny['financial']['status']}</span>
    </p>

    <h2>3. Configurable Rubric Evaluation Scorecard</h2>
    <p><strong>Reviewer ID:</strong> {eval_info['reviewer_id']} | <strong>Rubric Version:</strong> {eval_info['rubric_version']} | <strong>Status:</strong> {eval_info['status']}</p>
    <p><strong>Weighted Overall Score:</strong> <strong style="font-size: 18px; color: #2563eb;">{eval_info['overall_score'] if eval_info['overall_score'] is not None else '—'} / 10.0</strong></p>

    <table>
        <thead>
            <tr>
                <th>Criterion</th>
                <th>Weight</th>
                <th>Score</th>
                <th>Weighted Score</th>
                <th>Reviewer Justification</th>
            </tr>
        </thead>
        <tbody>
"""
        for c in scorecard["criteria"]:
            html += f"""
            <tr>
                <td><strong>{c['name']}</strong></td>
                <td>{int(c['weight'] * 100)}%</td>
                <td>{c['score'] if c['score'] is not None else '—'} / {c['max_score']}</td>
                <td>{c['weighted_score'] if c['weighted_score'] is not None else '—'}</td>
                <td>{c['justification_notes'] or c['comments'] or '—'}</td>
            </tr>
"""
        html += f"""
        </tbody>
    </table>

    <h2>4. Human Reviewer Final Recommendation</h2>
    <p><strong>Recommendation:</strong> <span class="badge badge-success">{eval_info['reviewer_recommendation']}</span></p>
    <p><strong>Reviewer Executive Summary:</strong> {eval_info['reviewer_summary'] or 'Reviewer summary recorded in evaluation workspace.'}</p>

    <div class="disclaimer">
        <strong>HUMAN REVIEWER SAFETY NOTICE:</strong><br/>
        {content['disclaimer']}
    </div>

    <div class="footer">
        NaCCER R&D Evaluation Copilot — Document SHA-256 Input Hash: {pack_data['input_hash'][:16]}...
    </div>
</body>
</html>
"""
        return html

    def _get_evaluation(self, evaluation_id: str) -> Evaluation:
        eval_item = self.db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
        if not eval_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Evaluation with ID '{evaluation_id}' not found.",
            )
        return eval_item

    def _build_attention_items(self, proposal: Any, comp: Any, fin: Any, historical: list[dict[str, Any]], criteria: list[Any]) -> list[dict[str, Any]]:
        items = []
        if comp.status == "INCOMPLETE":
            items.append({
                "severity": "HIGH",
                "category": "COMPLETENESS",
                "title": "Missing Proposal Scrutiny Fields",
                "description": f"Missing mandatory fields: {', '.join(comp.missing_fields)}.",
                "action": "Request applicant to submit missing section details.",
            })

        if fin.status != "COMPLIANT" or fin.arithmetic_mismatch:
            items.append({
                "severity": "HIGH",
                "category": "FINANCIAL",
                "title": "Financial Cost Head Mismatch",
                "description": "Component cost head totals variance detected against declared budget.",
                "action": "Reconcile cost head breakdown in financial compliance view.",
            })

        if historical and historical[0].get("similarity_percentage", 0) >= 75:
            top_h = historical[0]
            items.append({
                "severity": "MEDIUM",
                "category": "HISTORICAL_OVERLAP",
                "title": "High Conceptual Historical Overlap",
                "description": f"Potential conceptual similarity ({top_h.get('similarity_percentage')}%) with historical project '{top_h.get('project_code')}'.",
                "action": "Inspect historical benchmark comparison for novelty differentiation.",
            })

        unscored = [c for c in criteria if c.score is None]
        if unscored:
            items.append({
                "severity": "MEDIUM",
                "category": "SCORING",
                "title": f"{len(unscored)} Criteria Remaining Unscored",
                "description": f"Unscored criteria: {', '.join(c.name for c in unscored)}.",
                "action": "Assign criteria scores in rubric scorecard.",
            })

        return items

    def _build_evidence_coverage_matrix(self, criteria: list[Any], evidences: list[Any], proposal: Any, historical: list[dict[str, Any]], fin: Any) -> list[dict[str, Any]]:
        matrix = []
        for c in criteria:
            ckey = c.criterion_key or c.name
            has_prop = bool(proposal.problem_statement or proposal.methodology or proposal.technology)
            has_hist = len(historical) > 0 if ckey in ["NOVELTY", "TECHNICAL_SOUNDNESS"] else False
            has_fin = fin.status == "COMPLIANT" if ckey == "FINANCIAL_REASONABLENESS" else False
            has_rev = any(e.criterion_id == c.id for e in evidences)

            matrix.append({
                "criterion_key": ckey,
                "criterion_name": c.name,
                "has_proposal_evidence": has_prop,
                "has_historical_evidence": has_hist,
                "has_financial_evidence": has_fin,
                "has_reviewer_evidence": has_rev,
                "coverage_status": "FULL" if (has_prop and (has_hist or has_fin or has_rev)) else "PARTIAL",
            })
        return matrix
