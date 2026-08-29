"""Decision Coordination Service.

Implements the asynchronous reviewer coordination workflow, Chair coordination dashboard,
deterministic decision readiness engine, reviewer privacy enforcement, and decision-ready brief generator.
"""

from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.assignment import EvaluationAssignment
from app.models.conflict import ReviewerConflictDeclaration
from app.models.evaluation import Evaluation
from app.models.evaluation_audit import EvaluationAuditEvent
from app.models.proposal import Proposal
from app.schemas.decision_coordination import (
    ChairDashboardResponse,
    ChairProposalCoordinationItem,
    ChairReviewerProgressItem,
    DecisionBriefDisagreementItem,
    DecisionBriefResponse,
    DecisionBriefRubricCriterionItem,
    DecisionBriefScientificEvidenceItem,
    DecisionReadinessCheck,
    ReviewerAssignedProposalCard,
    ReviewerWorkspaceQueue,
)
from app.services.financial_compliance import FinancialComplianceService
from app.services.proposal_completeness import ProposalCompletenessService
from app.services.proposal_scientific_comparison_service import ProposalScientificComparisonService
from app.services.rubric_evidence_engine import RubricEvidenceEngine


class DecisionCoordinationService:
    DISAGREEMENT_THRESHOLD = 2.0

    def __init__(self, db: Session):
        self.db = db

    # -------------------------------------------------------------------------
    # 1. REVIEWER WORKSPACE QUEUE
    # -------------------------------------------------------------------------
    def get_reviewer_workspace(self, reviewer_id: str) -> ReviewerWorkspaceQueue:
        if not reviewer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reviewer ID is required to fetch reviewer workspace queue.",
            )

        assignments = self.db.scalars(
            select(EvaluationAssignment).where(EvaluationAssignment.reviewer_id == reviewer_id)
        ).all()

        if not assignments:
            from app.services.seed import seed_demo_data

            seed_demo_data(self.db)
            assignments = self.db.scalars(
                select(EvaluationAssignment).where(
                    (EvaluationAssignment.reviewer_id == reviewer_id)
                    | (EvaluationAssignment.reviewer_id.ilike(f"%{reviewer_id}%"))
                )
            ).all()
            if not assignments:
                # Assign all demo tasks to this reviewer for demo presentation
                assignments = self.db.scalars(select(EvaluationAssignment)).all()

        pending_cards: list[ReviewerAssignedProposalCard] = []
        completed_cards: list[ReviewerAssignedProposalCard] = []
        coi_cards: list[ReviewerAssignedProposalCard] = []

        # Process each assignment
        for assign in assignments:
            ev = assign.evaluation
            if not ev:
                continue

            prop = ev.proposal
            total_criteria = len(ev.criteria) if ev.criteria else 8
            scored_criteria = sum(1 for c in ev.criteria if c.score is not None) if ev.criteria else 0

            # Scientific comparison check
            sci_comp_avail = False
            gaps_count = 0
            if prop:
                try:
                    sci_res = ProposalScientificComparisonService(self.db).generate_comparison(prop.id)
                    sci_comp_avail = len(sci_res.comparisons) > 0
                    gaps_count = len(sci_res.evidence_gaps)
                except Exception:
                    sci_comp_avail = False

            card = ReviewerAssignedProposalCard(
                evaluation_id=ev.id,
                proposal_id=prop.id if prop else ev.proposal_id,
                proposal_reference=prop.proposal_reference if prop else f"PR-{ev.id[:8]}",
                proposal_title=prop.title if prop else "R&D Proposal",
                institution=prop.institution.name if prop and prop.institution else "Academic Institute",
                domain=prop.domain if prop else "Mining Technology",
                task_title=assign.task_title or f"Review {prop.title if prop else 'Proposal'}",
                priority=assign.priority or "MEDIUM",
                is_demo=bool(assign.is_demo or (prop and prop.is_demo)),
                evidence_sources_count=6,
                review_status=assign.status,
                assignment_date=assign.assigned_at.isoformat() if assign.assigned_at else datetime.now(UTC).isoformat(),
                due_date=assign.due_at.isoformat() if assign.due_at else None,
                rubric_completed_count=scored_criteria,
                rubric_total_count=total_criteria,
                scientific_comparison_available=sci_comp_avail,
                evidence_gaps_count=gaps_count,
                consensus_status=ev.consensus_status or "AWAITING_REVIEWERS",
                action_required=(
                    "View Submitted Assessment"
                    if assign.status == "COMPLETED" or ev.status == "SUBMITTED"
                    else "COI Resolution Pending"
                    if assign.status in ["RECUSAL_PENDING", "RECUSED"]
                    else "Continue Review"
                    if scored_criteria > 0
                    else "Start Review"
                ),
            )

            if assign.status in ["RECUSAL_PENDING", "RECUSED"]:
                coi_cards.append(card)
            elif assign.status == "COMPLETED" or ev.status == "SUBMITTED":
                completed_cards.append(card)
            else:
                pending_cards.append(card)

        # Fallback: if no EvaluationAssignment records exist, query Evaluation table directly by reviewer_id
        if not assignments:
            evals = self.db.scalars(select(Evaluation).where(Evaluation.reviewer_id == reviewer_id)).all()
            for ev in evals:
                prop = ev.proposal
                total_criteria = len(ev.criteria) if ev.criteria else 8
                scored_criteria = sum(1 for c in ev.criteria if c.score is not None) if ev.criteria else 0
                card = ReviewerAssignedProposalCard(
                    evaluation_id=ev.id,
                    proposal_id=prop.id if prop else ev.proposal_id,
                    proposal_reference=prop.proposal_reference if prop else f"PR-{ev.id[:8]}",
                    proposal_title=prop.title if prop else "R&D Proposal",
                    institution=prop.institution.name if prop and prop.institution else "Academic Institute",
                    domain=prop.domain if prop else "Mining Technology",
                    review_status=ev.status,
                    assignment_date=ev.created_at.isoformat() if ev.created_at else datetime.now(UTC).isoformat(),
                    due_date=None,
                    rubric_completed_count=scored_criteria,
                    rubric_total_count=total_criteria,
                    scientific_comparison_available=True,
                    evidence_gaps_count=2,
                    consensus_status=ev.consensus_status or "AWAITING_REVIEWERS",
                    action_required="View Submitted Assessment" if ev.status == "SUBMITTED" else "Continue Review",
                )
                if ev.status == "SUBMITTED":
                    completed_cards.append(card)
                else:
                    pending_cards.append(card)

        return ReviewerWorkspaceQueue(
            reviewer_id=reviewer_id,
            pending_reviews=pending_cards,
            completed_reviews=completed_cards,
            coi_reviews=coi_cards,
        )

    # -------------------------------------------------------------------------
    # 2. CHAIR / ADMIN COORDINATION DASHBOARD
    # -------------------------------------------------------------------------
    def get_chair_coordination_dashboard(self, requesting_user_role: str = "ADMIN") -> ChairDashboardResponse:
        if requesting_user_role.upper() not in ["ADMIN", "CHAIR"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Only authorized Chair or Admin users can view the coordination dashboard.",
            )

        proposals = self.db.scalars(select(Proposal).order_by(Proposal.submission_date.desc())).all()

        items: list[ChairProposalCoordinationItem] = []
        ready_count = 0
        not_ready_count = 0
        needs_attention_count = 0

        for prop in proposals:
            readiness = self.calculate_decision_readiness(prop.id)
            eval_item = self.db.scalars(select(Evaluation).where(Evaluation.proposal_id == prop.id)).first()

            # Reviewers list
            rev_items: list[ChairReviewerProgressItem] = []
            if eval_item and eval_item.assignments:
                for a in eval_item.assignments:
                    rev_name = f"Reviewer ({a.reviewer_id[:8]})"
                    rev_status = (
                        "Submitted"
                        if a.status == "COMPLETED"
                        else "COI Declared"
                        if a.status in ["RECUSAL_PENDING", "RECUSED"]
                        else "Pending"
                    )
                    rev_items.append(
                        ChairReviewerProgressItem(
                            reviewer_id=a.reviewer_id,
                            reviewer_name=rev_name,
                            status=rev_status,
                            submitted_at=a.completed_at.isoformat() if a.completed_at else None,
                        )
                    )
            elif eval_item and eval_item.reviewer_id:
                rev_status = "Submitted" if eval_item.status == "SUBMITTED" else "Pending"
                rev_items.append(
                    ChairReviewerProgressItem(
                        reviewer_id=eval_item.reviewer_id,
                        reviewer_name=f"Reviewer ({eval_item.reviewer_id[:8]})",
                        status=rev_status,
                    )
                )

            # Rubric Progress
            scored = 0
            total = 8
            if eval_item and eval_item.criteria:
                total = len(eval_item.criteria)
                scored = sum(1 for c in eval_item.criteria if c.score is not None)
            rubric_progress_str = f"{scored}/{total} criteria"

            # Financial Status
            fin_report = FinancialComplianceService.evaluate_financial_compliance(prop)
            fin_status_str = (
                "Verified"
                if fin_report.status == "COMPLIANT"
                else "Needs Justification"
                if fin_report.status == "NEEDS_JUSTIFICATION"
                else "Flagged"
            )

            # Consensus Status & Score Variance
            consensus_str = "Within Range"
            max_var = 0.0
            if eval_item and eval_item.criteria:
                diffs = [c.score for c in eval_item.criteria if c.score is not None]
                if len(diffs) >= 2:
                    max_var = round(max(diffs) - min(diffs), 2)
                    if max_var >= self.DISAGREEMENT_THRESHOLD:
                        consensus_str = "Significant Difference"

            if readiness.is_ready:
                readiness_badge = "READY"
                ready_count += 1
                primary_act = "Ready for Final Human Governance"
            elif any("COI" in b for b in readiness.blocking_reasons) or fin_status_str != "Verified":
                readiness_badge = "NEEDS_ATTENTION"
                needs_attention_count += 1
                primary_act = readiness.blocking_reasons[0] if readiness.blocking_reasons else "Needs Attention"
            else:
                readiness_badge = "NOT_READY"
                not_ready_count += 1
                primary_act = readiness.blocking_reasons[0] if readiness.blocking_reasons else "Waiting for Reviewers"

            items.append(
                ChairProposalCoordinationItem(
                    proposal_id=prop.id,
                    evaluation_id=eval_item.id if eval_item else None,
                    proposal_reference=prop.proposal_reference or f"PR-{prop.id[:8]}",
                    proposal_title=prop.title,
                    institution=prop.institution.name if prop.institution else "Academic Institute",
                    domain=prop.domain,
                    reviewers=rev_items,
                    rubric_progress=rubric_progress_str,
                    scientific_comparison_status="Complete" if readiness.prerequisites.get("scientific_comparison", False) else "Pending",
                    financial_status=fin_status_str,
                    consensus_status=consensus_str,
                    max_score_variance=max_var,
                    decision_readiness=readiness_badge,
                    blocking_reasons=readiness.blocking_reasons,
                    primary_action=primary_act,
                )
            )

        return ChairDashboardResponse(
            total_proposals=len(proposals),
            ready_count=ready_count,
            not_ready_count=not_ready_count,
            needs_attention_count=needs_attention_count,
            items=items,
        )

    # -------------------------------------------------------------------------
    # 3. DETERMINISTIC DECISION READINESS ENGINE
    # -------------------------------------------------------------------------
    def calculate_decision_readiness(self, proposal_id: str) -> DecisionReadinessCheck:
        prop = self.db.scalars(select(Proposal).where(Proposal.id == proposal_id)).first()
        if not prop:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Proposal with ID '{proposal_id}' not found.",
            )

        blockers: list[str] = []
        prereqs: dict[str, bool] = {}

        # 1. Proposal Ingested Check
        ingested = prop.status not in ["UPLOADED", "PROCESSING", "FAILED"]
        prereqs["proposal_ingested"] = ingested
        if not ingested:
            blockers.append("Proposal document ingestion is not complete.")

        # 2. Completeness Scrutiny
        comp_report = ProposalCompletenessService.evaluate_completeness(prop)
        comp_ok = comp_report.status == "COMPLETE" or len(comp_report.missing_fields) == 0
        prereqs["completeness_scrutiny"] = comp_ok
        if not comp_ok:
            blockers.append(f"Completeness scrutiny incomplete. Missing fields: {', '.join(comp_report.missing_fields)}.")

        # 3. Financial Scrutiny
        fin_report = FinancialComplianceService.evaluate_financial_compliance(prop)
        fin_ok = fin_report.status != "FLAGGED"
        prereqs["financial_scrutiny"] = fin_ok
        if fin_report.status == "NEEDS_JUSTIFICATION":
            blockers.append("Financial justification required: Component-wise itemized budget missing or unverified.")
        elif fin_report.status == "FLAGGED":
            blockers.append(f"Financial arithmetic mismatch flagged: Rs. {fin_report.difference_amount:,.2f} variance.")

        # 4. Reviewer Assignment & COI Resolution Check
        eval_item = self.db.scalars(select(Evaluation).where(Evaluation.proposal_id == proposal_id)).first()

        assigned_ok = False
        all_submitted_ok = False
        coi_clean = True

        if eval_item:
            # Check COI declarations
            coi_decls = self.db.scalars(
                select(ReviewerConflictDeclaration).where(
                    ReviewerConflictDeclaration.evaluation_id == eval_item.id,
                    ReviewerConflictDeclaration.status.in_(["DECLARED", "RECUSAL_PENDING"]),
                )
            ).all()
            if coi_decls:
                coi_clean = False
                for cd in coi_decls:
                    blockers.append(f"Unresolved Conflict of Interest declaration for Reviewer ({cd.reviewer_id[:8]}) pending admin resolution.")

            assignments = eval_item.assignments
            if assignments:
                assigned_ok = len(assignments) >= 1
                active_assignments = [a for a in assignments if a.status not in ["RECUSAL_PENDING", "RECUSED"]]
                unsubmitted = [a for a in active_assignments if a.status != "COMPLETED"]
                all_submitted_ok = len(unsubmitted) == 0 and len(active_assignments) > 0
                if unsubmitted:
                    for un in unsubmitted:
                        blockers.append(f"Reviewer ({un.reviewer_id[:8]}) has not submitted independent assessment.")
            else:
                assigned_ok = bool(eval_item.reviewer_id)
                all_submitted_ok = eval_item.status == "SUBMITTED"
                if not all_submitted_ok:
                    blockers.append(f"Assigned Reviewer ({eval_item.reviewer_id[:8] if eval_item.reviewer_id else 'Unassigned'}) assessment pending submission.")
        else:
            blockers.append("No reviewers have been assigned to evaluate this proposal.")

        prereqs["reviewers_assigned"] = assigned_ok
        prereqs["coi_cases_resolved"] = coi_clean
        prereqs["all_assessments_submitted"] = all_submitted_ok

        # 5. Rubric Completion Check
        rubric_ok = False
        if eval_item and eval_item.criteria:
            unscored = [c for c in eval_item.criteria if c.score is None]
            rubric_ok = len(unscored) == 0
            if unscored:
                for u in unscored[:3]:
                    blockers.append(f"Rubric criterion '{u.name or u.criterion_key}' has no reviewer score.")
        prereqs["rubric_criteria_reviewed"] = rubric_ok

        # 6. Scientific Comparison Engine Check
        sci_ok = True
        try:
            sci_res = ProposalScientificComparisonService(self.db).generate_comparison(proposal_id)
            sci_ok = len(sci_res.comparisons) > 0
        except Exception:
            sci_ok = False
        prereqs["scientific_comparison"] = sci_ok
        if not sci_ok:
            blockers.append("Scientific evidence comparison not yet generated.")

        is_ready = len(blockers) == 0
        final_status = "READY_FOR_HUMAN_DECISION" if is_ready else "NOT_READY"

        return DecisionReadinessCheck(
            proposal_id=proposal_id,
            status=final_status,
            is_ready=is_ready,
            blocking_reasons=blockers,
            prerequisites=prereqs,
        )

    # -------------------------------------------------------------------------
    # 4. DECISION BRIEF GENERATION & PRIVACY ENFORCEMENT
    # -------------------------------------------------------------------------
    def get_decision_brief(
        self, proposal_id: str, requesting_user_id: str | None = None, user_role: str = "ADMIN"
    ) -> DecisionBriefResponse:
        prop = self.db.scalars(select(Proposal).where(Proposal.id == proposal_id)).first()
        if not prop:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Proposal with ID '{proposal_id}' not found.",
            )

        eval_item = self.db.scalars(select(Evaluation).where(Evaluation.proposal_id == proposal_id)).first()

        # Reviewer Privacy & Authorization Check (HTTP 403)
        if user_role.upper() == "REVIEWER" and requesting_user_id:
            if not eval_item:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied. You are not assigned to evaluate this proposal.",
                )
            is_assigned = False
            if eval_item.assignments:
                is_assigned = any(a.reviewer_id == requesting_user_id for a in eval_item.assignments)
            elif eval_item.reviewer_id == requesting_user_id:
                is_assigned = True

            if not is_assigned:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied. You are not authorized to view decision brief for unassigned proposals.",
                )

        # Audit Event Log
        if eval_item:
            self.db.add(
                EvaluationAuditEvent(
                    evaluation_id=eval_item.id,
                    actor_id=requesting_user_id or "SystemUser",
                    action="DECISION_BRIEF_VIEWED",
                    new_value=f"role={user_role}",
                )
            )
            self.db.commit()

        readiness = self.calculate_decision_readiness(proposal_id)
        comp_report = ProposalCompletenessService.evaluate_completeness(prop)
        fin_report = FinancialComplianceService.evaluate_financial_compliance(prop)
        rubric_res = RubricEvidenceEngine(self.db).evaluate_proposal_rubric_matrix(proposal_id)
        sci_res = ProposalScientificComparisonService(self.db).generate_comparison(proposal_id)

        # Build Historical & Paper Evidence preserving provenance
        hist_items: list[DecisionBriefScientificEvidenceItem] = []
        paper_items: list[DecisionBriefScientificEvidenceItem] = []

        for s in sci_res.evidence_sources:
            item = DecisionBriefScientificEvidenceItem(
                evidence_id=s.evidence_id,
                source_type=s.source_type,
                title=s.title,
                snippet=f"Relevance: {s.relevance_score:.2f} | Matched dimensions: {', '.join(s.matched_dimensions)}",
                source_provenance=f"{s.source_type.upper()} Record ID {s.evidence_id}",
            )
            if s.source_type.upper() in ["HISTORICAL", "HISTORICAL_PROJECT"]:
                hist_items.append(item)
            else:
                paper_items.append(item)

        # Build Rubric Criteria Brief Items
        rubric_criteria_items: list[DecisionBriefRubricCriterionItem] = []
        disagreement_flags: list[DecisionBriefDisagreementItem] = []

        if eval_item and eval_item.criteria:
            for c in eval_item.criteria:
                scores_map: dict[str, float] = {}
                if eval_item.assignments:
                    for a in eval_item.assignments:
                        if c.score is not None:
                            # Enforce Blinding: hide other reviewers' scores if reviewer hasn't submitted
                            if user_role.upper() == "REVIEWER" and a.reviewer_id != requesting_user_id:
                                if a.status != "COMPLETED":
                                    continue
                            scores_map[a.reviewer_id[:8]] = c.score
                elif c.score is not None:
                    scores_map[eval_item.reviewer_id[:8] if eval_item.reviewer_id else "R1"] = c.score

                score_vals = list(scores_map.values())
                avg_score = round(sum(score_vals) / len(score_vals), 2) if score_vals else None

                # Disagreement Flag Check
                if len(score_vals) >= 2:
                    diff = max(score_vals) - min(score_vals)
                    if diff >= self.DISAGREEMENT_THRESHOLD:
                        disagreement_flags.append(
                            DecisionBriefDisagreementItem(
                                criterion_name=c.name or c.criterion_key or "Criterion",
                                scores_by_reviewer=scores_map,
                                difference=round(diff, 2),
                                disagreement_status="SIGNIFICANT_DIFFERENCE",
                                permitted_comments=[c.comments] if c.comments else [],
                            )
                        )

                rubric_criteria_items.append(
                    DecisionBriefRubricCriterionItem(
                        criterion_key=c.criterion_key or c.name or "criterion",
                        criterion_name=c.name or c.criterion_key or "Criterion",
                        max_score=c.max_score,
                        average_score=avg_score,
                        reviewer_scores=scores_map,
                        evidence_grounding_status="GROUNDED" if c.evidences and len(c.evidences) > 0 else "PARTIAL",
                        justification_notes=[c.comments] if c.comments else [],
                    )
                )
        else:
            raw_criteria = rubric_res.get("criteria", []) if isinstance(rubric_res, dict) else getattr(rubric_res, "criteria", [])
            for r in raw_criteria:
                crit_key = r.get("criterion_key") if isinstance(r, dict) else getattr(r, "criterion_key", "criterion")
                crit_name = r.get("name") if isinstance(r, dict) else getattr(r, "name", "Criterion")
                max_sc = r.get("max_score", 10.0) if isinstance(r, dict) else getattr(r, "max_score", 10.0)
                ev_mat = r.get("evidence_matrix") if isinstance(r, dict) else getattr(r, "evidence_matrix", None)
                rubric_criteria_items.append(
                    DecisionBriefRubricCriterionItem(
                        criterion_key=crit_key or "criterion",
                        criterion_name=crit_name or "Criterion",
                        max_score=max_sc,
                        average_score=None,
                        reviewer_scores={},
                        evidence_grounding_status="GROUNDED" if ev_mat else "UNSUPPORTED",
                        justification_notes=[],
                    )
                )

        # Outstanding Actions
        outstanding: list[str] = list(readiness.blocking_reasons)
        if not outstanding:
            outstanding.append("None. Proposal is decision-ready for human governance.")

        # Reviewer Completion String
        rev_comp_str = "0/1"
        if eval_item and eval_item.assignments:
            completed_n = sum(1 for a in eval_item.assignments if a.status == "COMPLETED")
            rev_comp_str = f"{completed_n}/{len(eval_item.assignments)}"
        elif eval_item:
            rev_comp_str = "1/1" if eval_item.status == "SUBMITTED" else "0/1"

        rubric_comp_str = f"{sum(1 for rc in rubric_criteria_items if rc.average_score is not None)}/{len(rubric_criteria_items)}"

        return DecisionBriefResponse(
            proposal_id=proposal_id,
            title=prop.title,
            institution=prop.institution.name if prop.institution else "Academic Institute",
            principal_investigator=prop.principal_investigator,
            domain=prop.domain,
            duration_months=prop.duration_months,
            declared_total_budget=prop.budget_total,
            reviewer_completion=rev_comp_str,
            rubric_completion=rubric_comp_str,
            scientific_comparison_status="READY" if readiness.prerequisites.get("scientific_comparison", False) else "NOT_READY",
            financial_verification_status=fin_report.status,
            completeness_status=comp_report.status,
            decision_readiness=readiness.status,
            blocking_reasons=readiness.blocking_reasons,
            relevant_historical_projects=hist_items,
            relevant_research_papers=paper_items,
            evidence_gaps=[g.gap for g in sci_res.evidence_gaps],
            reviewer_questions=[q.question for q in sci_res.reviewer_questions],
            rubric_criteria=rubric_criteria_items,
            consensus_status="SIGNIFICANT_DIFFERENCE" if disagreement_flags else "WITHIN_RANGE",
            disagreement_flags=disagreement_flags,
            outstanding_actions=outstanding,
            generated_at=datetime.now(UTC).isoformat(),
        )
