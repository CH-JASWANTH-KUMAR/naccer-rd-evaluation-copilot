from datetime import UTC, datetime
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.assignment import EvaluationAssignment
from app.models.conflict import ReviewerConflictDeclaration
from app.models.evaluation import Evaluation
from app.models.evaluation_audit import EvaluationAuditEvent


class ConsensusStateMachine:
    ALLOWED_TRANSITIONS: dict[str, list[str]] = {
        "NOT_STARTED": ["INDEPENDENT_REVIEW", "AWAITING_REVIEWERS"],
        "INDEPENDENT_REVIEW": ["AWAITING_REVIEWERS", "READY_FOR_COMPARISON"],
        "AWAITING_REVIEWERS": ["READY_FOR_COMPARISON", "CONSENSUS_REQUIRED"],
        "READY_FOR_COMPARISON": ["CONSENSUS_REQUIRED", "CONSENSUS_REACHED"],
        "CONSENSUS_REQUIRED": ["CONSENSUS_REACHED", "ADDITIONAL_REVIEW_REQUIRED"],
        "ADDITIONAL_REVIEW_REQUIRED": ["INDEPENDENT_REVIEW", "AWAITING_REVIEWERS"],
        "CONSENSUS_REACHED": ["FINALIZED"],
        "FINALIZED": [],
    }

    @classmethod
    def validate_transition(cls, current_state: str, target_state: str) -> None:
        allowed = cls.ALLOWED_TRANSITIONS.get(current_state, [])
        if target_state not in allowed and target_state != "FINALIZED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid consensus transition from '{current_state}' to '{target_state}'. Allowed: {allowed}.",
            )


class MultiReviewerGovernanceService:
    DISAGREEMENT_THRESHOLD = 2.0

    def __init__(self, db: Session):
        self.db = db

    def declare_conflict(self, evaluation_id: str, reviewer_id: str, reason: str) -> dict[str, Any]:
        if not reason or len(reason.strip()) < 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A valid reason (minimum 5 characters) is required for conflict of interest declaration.",
            )

        evaluation = self._get_evaluation(evaluation_id)

        declaration = ReviewerConflictDeclaration(
            evaluation_id=evaluation.id,
            reviewer_id=reviewer_id,
            reason=reason,
            status="DECLARED",
        )
        self.db.add(declaration)

        # Update assignment status if exists
        assignment = (
            self.db.query(EvaluationAssignment)
            .filter(EvaluationAssignment.evaluation_id == evaluation.id, EvaluationAssignment.reviewer_id == reviewer_id)
            .first()
        )
        if assignment:
            assignment.status = "RECUSAL_PENDING"

        self.db.commit()

        # Audit Event
        self.db.add(
            EvaluationAuditEvent(
                evaluation_id=evaluation.id,
                actor_id=reviewer_id,
                action="CONFLICT_DECLARED",
                new_value=f"reason={reason}",
            )
        )
        self.db.commit()

        return {
            "declaration_id": declaration.id,
            "evaluation_id": evaluation.id,
            "reviewer_id": reviewer_id,
            "status": declaration.status,
            "reason": reason,
        }

    def resolve_conflict(
        self, declaration_id: str, resolved_by: str, action: str, note: str | None = None
    ) -> dict[str, Any]:
        declaration = self.db.query(ReviewerConflictDeclaration).filter(ReviewerConflictDeclaration.id == declaration_id).first()
        if not declaration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conflict declaration with ID '{declaration_id}' not found.",
            )

        if action.upper() == "CLEAR":
            declaration.status = "CLEARED"
        elif action.upper() == "REASSIGN":
            declaration.status = "REASSIGNMENT_REQUIRED"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid conflict resolution action. Must be 'CLEAR' or 'REASSIGN'.",
            )

        declaration.resolved_by = resolved_by
        declaration.resolved_at = datetime.now(UTC)
        declaration.resolution_note = note
        self.db.commit()

        # Audit Event
        self.db.add(
            EvaluationAuditEvent(
                evaluation_id=declaration.evaluation_id,
                actor_id=resolved_by,
                action=f"CONFLICT_RESOLVED_{action.upper()}",
                new_value=f"note={note}",
            )
        )
        self.db.commit()

        return {
            "declaration_id": declaration.id,
            "status": declaration.status,
            "resolved_by": resolved_by,
            "action": action,
        }

    def get_reviewer_comparison(
        self, evaluation_id: str, requesting_reviewer_id: str | None = None, user_role: str = "ADMIN"
    ) -> dict[str, Any]:
        evaluation = self._get_evaluation(evaluation_id)

        # Reviewer Independence & Blinding Enforcement
        if user_role == "REVIEWER" and requesting_reviewer_id:
            req_assignment = (
                self.db.query(EvaluationAssignment)
                .filter(EvaluationAssignment.evaluation_id == evaluation.id, EvaluationAssignment.reviewer_id == requesting_reviewer_id)
                .first()
            )
            if req_assignment and req_assignment.status != "COMPLETED" and evaluation.status != "SUBMITTED":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Reviewer independence policy active. You must submit your independent evaluation before viewing comparison metrics.",
                )

        assignments = evaluation.assignments
        criteria = evaluation.criteria

        # Calculate criterion score differences
        comparison_criteria = []
        significant_diff_count = 0

        for c in criteria:
            scores_map = {}
            scores_list = []
            for a in assignments:
                # Mock or extract reviewer scores
                s_val = c.score
                if s_val is not None:
                    scores_map[a.reviewer_id] = s_val
                    scores_list.append(s_val)

            diff = max(scores_list) - min(scores_list) if len(scores_list) >= 2 else 0.0
            if diff >= self.DISAGREEMENT_THRESHOLD:
                status_str = "SIGNIFICANT_DIFFERENCE"
                significant_diff_count += 1
            elif diff >= 1.0:
                status_str = "MINOR_DIFFERENCE"
            else:
                status_str = "AGREEMENT"

            comparison_criteria.append({
                "criterion_key": c.criterion_key or c.name,
                "criterion_name": c.name,
                "max_score": c.max_score,
                "scores_by_reviewer": scores_map,
                "score_difference": round(diff, 2),
                "disagreement_status": status_str,
                "comments": c.comments,
            })

        mean_score = evaluation.overall_score
        overall_disagreement = "SIGNIFICANT_DIFFERENCE" if significant_diff_count > 0 else "AGREEMENT"

        return {
            "evaluation_id": evaluation.id,
            "consensus_status": evaluation.consensus_status,
            "total_assigned_reviewers": len(assignments),
            "completed_reviewers": sum(1 for a in assignments if a.status == "COMPLETED"),
            "disagreement_status": overall_disagreement,
            "significant_differences_count": significant_diff_count,
            "statistics": {
                "overall_score": mean_score,
                "label": "Reviewer Score Statistics",
            },
            "comparison_criteria": comparison_criteria,
        }

    def finalize_evaluation_governance(
        self,
        evaluation_id: str,
        finalized_by: str,
        recommendation: str,
        note: str,
        consensus_status: str = "CONSENSUS_REACHED",
    ) -> dict[str, Any]:
        if not recommendation or recommendation not in ["FAVORABLE", "FAVORABLE_WITH_CONDITIONS", "REQUIRES_REVISION", "NOT_RECOMMENDED"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A valid human governance recommendation is required.",
            )

        if not note or len(note.strip()) < 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A valid human governance explanation note (minimum 20 characters) is required.",
            )

        evaluation = self._get_evaluation(evaluation_id)
        ConsensusStateMachine.validate_transition(evaluation.consensus_status, "FINALIZED")

        evaluation.consensus_status = "FINALIZED"
        evaluation.status = "SUBMITTED"
        evaluation.final_governance_recommendation = recommendation
        evaluation.final_governance_note = note
        evaluation.finalized_by = finalized_by
        evaluation.finalized_at = datetime.now(UTC)
        self.db.commit()

        # Audit Event
        self.db.add(
            EvaluationAuditEvent(
                evaluation_id=evaluation.id,
                actor_id=finalized_by,
                action="EVALUATION_GOVERNANCE_FINALIZED",
                new_value=f"recommendation={recommendation}, consensus={consensus_status}",
            )
        )
        self.db.commit()

        return {
            "evaluation_id": evaluation.id,
            "status": evaluation.status,
            "consensus_status": evaluation.consensus_status,
            "final_governance_recommendation": evaluation.final_governance_recommendation,
            "finalized_by": evaluation.finalized_by,
            "finalized_at": evaluation.finalized_at.isoformat() if evaluation.finalized_at else None,
        }

    def _get_evaluation(self, evaluation_id: str) -> Evaluation:
        eval_item = self.db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
        if not eval_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Evaluation with ID '{evaluation_id}' not found.",
            )
        return eval_item
