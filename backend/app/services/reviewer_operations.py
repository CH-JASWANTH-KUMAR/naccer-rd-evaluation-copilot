import csv
import io
from datetime import datetime
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.assignment import EvaluationAssignment
from app.models.evaluation import Evaluation
from app.models.evaluation_audit import EvaluationAuditEvent
from app.services.ai_analysis_provider import AIProviderFactory


class ProposalStateMachine:
    ALLOWED_TRANSITIONS: dict[str, list[str]] = {
        "UPLOADED": ["PROCESSING", "FAILED"],
        "PROCESSING": ["READY_FOR_REVIEW", "FAILED"],
        "READY_FOR_REVIEW": ["ASSIGNED", "UNDER_REVIEW"],
        "DRAFT": ["ASSIGNED", "UNDER_REVIEW", "SUBMITTED"],
        "ASSIGNED": ["UNDER_REVIEW", "SUBMITTED", "RETURNED_FOR_REVISION", "REASSIGNED", "DRAFT"],
        "UNDER_REVIEW": ["SUBMITTED", "RETURNED_FOR_REVISION", "DRAFT"],
        "RETURNED_FOR_REVISION": ["UNDER_REVIEW", "DRAFT"],
        "SUBMITTED": ["RETURNED_FOR_REVISION", "ARCHIVED"],
        "ARCHIVED": [],
    }

    @classmethod
    def validate_transition(cls, current_state: str, target_state: str) -> None:
        allowed = cls.ALLOWED_TRANSITIONS.get(current_state, [])
        if target_state not in allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid state transition from '{current_state}' to '{target_state}'. Allowed: {allowed}.",
            )


class ReviewerOperationsService:
    def __init__(self, db: Session):
        self.db = db

    def get_reviewer_queue(self, reviewer_id: str, status_filter: str | None = None) -> list[dict[str, Any]]:
        stmt = (
            select(Evaluation)
            .where(Evaluation.reviewer_id == reviewer_id)
            .order_by(Evaluation.created_at.desc())
        )
        if status_filter:
            stmt = stmt.where(Evaluation.status == status_filter)

        evals = self.db.scalars(stmt).all()
        queue_items = []

        for ev in evals:
            total_criteria = len(ev.criteria)
            scored_criteria = sum(1 for c in ev.criteria if c.score is not None)
            progress_pct = round((scored_criteria / total_criteria * 100.0), 1) if total_criteria > 0 else 0.0

            queue_items.append({
                "evaluation_id": ev.id,
                "proposal_id": ev.proposal_id,
                "proposal_reference": ev.proposal.proposal_reference if ev.proposal else None,
                "proposal_title": ev.proposal.title if ev.proposal else "R&D Proposal",
                "institution": ev.proposal.institution.name if ev.proposal and ev.proposal.institution else None,
                "reviewer_id": ev.reviewer_id,
                "status": ev.status,
                "overall_score": ev.overall_score,
                "progress_percentage": progress_pct,
                "criteria_scored": scored_criteria,
                "criteria_total": total_criteria,
                "created_at": ev.created_at.isoformat() if ev.created_at else None,
            })

        return queue_items

    def assign_reviewer(
        self, evaluation_id: str, reviewer_id: str, assigned_by: str = "Admin", due_at: datetime | None = None
    ) -> dict[str, Any]:
        evaluation = self._get_evaluation(evaluation_id)
        ProposalStateMachine.validate_transition(evaluation.status, "ASSIGNED")

        assignment = EvaluationAssignment(
            evaluation_id=evaluation.id,
            reviewer_id=reviewer_id,
            assigned_by=assigned_by,
            due_at=due_at,
            status="ASSIGNED",
        )
        self.db.add(assignment)

        evaluation.reviewer_id = reviewer_id
        evaluation.status = "ASSIGNED"
        self.db.commit()

        # Audit Event
        self.db.add(
            EvaluationAuditEvent(
                evaluation_id=evaluation.id,
                actor_id=assigned_by,
                action="REVIEWER_ASSIGNED",
                new_value=f"reviewer={reviewer_id}",
            )
        )
        self.db.commit()

        return {
            "evaluation_id": evaluation.id,
            "reviewer_id": reviewer_id,
            "status": evaluation.status,
            "assigned_at": assignment.assigned_at.isoformat(),
        }

    def return_for_revision(
        self, evaluation_id: str, returned_by: str, reason: str
    ) -> dict[str, Any]:
        if not reason or len(reason.strip()) < 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A valid human-entered return reason (minimum 5 characters) is required.",
            )

        evaluation = self._get_evaluation(evaluation_id)
        ProposalStateMachine.validate_transition(evaluation.status, "RETURNED_FOR_REVISION")

        evaluation.status = "RETURNED_FOR_REVISION"
        self.db.commit()

        # Audit Event
        self.db.add(
            EvaluationAuditEvent(
                evaluation_id=evaluation.id,
                actor_id=returned_by,
                action="RETURNED_FOR_REVISION",
                new_value=f"reason={reason}",
            )
        )
        self.db.commit()

        return {
            "evaluation_id": evaluation.id,
            "status": evaluation.status,
            "returned_by": returned_by,
            "reason": reason,
        }

    @classmethod
    def get_system_readiness(cls) -> dict[str, Any]:
        provider = AIProviderFactory.get_provider()
        return {
            "status": "healthy",
            "readiness": "READY",
            "subsystems": {
                "database": "READY",
                "document_processing": "READY",
                "historical_search": "READY",
                "ai_provider": {
                    "provider": provider.provider_name,
                    "model": provider.model_name,
                    "status": "READY" if not provider.provider_name.startswith("deterministic") else "DEGRADED_FALLBACK",
                },
            },
        }

    def export_operational_csv(self) -> str:
        evals = self.db.scalars(select(Evaluation)).all()
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow([
            "Evaluation ID",
            "Proposal Reference",
            "Proposal Title",
            "Reviewer ID",
            "Status",
            "Overall Score",
            "Recommendation",
            "Rubric Version",
            "Created At",
        ])

        for ev in evals:
            writer.writerow([
                ev.id,
                ev.proposal.proposal_reference if ev.proposal else "",
                ev.proposal.title if ev.proposal else "",
                ev.reviewer_id,
                ev.status,
                ev.overall_score if ev.overall_score is not None else "",
                ev.reviewer_recommendation,
                ev.rubric_version,
                ev.created_at.isoformat() if ev.created_at else "",
            ])

        return output.getvalue()

    def _get_evaluation(self, evaluation_id: str) -> Evaluation:
        eval_item = self.db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
        if not eval_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Evaluation with ID '{evaluation_id}' not found.",
            )
        return eval_item
