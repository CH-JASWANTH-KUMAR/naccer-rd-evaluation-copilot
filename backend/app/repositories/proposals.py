from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.proposal import Proposal
from app.schemas.proposal import ProposalCreate, ProposalUpdate


class ProposalRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, domain: str | None = None, status: str | None = None) -> list[Proposal]:
        stmt = select(Proposal).options(joinedload(Proposal.institution)).order_by(Proposal.created_at.desc())
        if domain:
            stmt = stmt.where(Proposal.domain == domain)
        if status:
            stmt = stmt.where(Proposal.status == status)
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, proposal_id: str) -> Proposal | None:
        stmt = select(Proposal).options(joinedload(Proposal.institution)).where(Proposal.id == proposal_id)
        return self.db.scalars(stmt).first()

    def create(self, data: ProposalCreate) -> Proposal:
        proposal = Proposal(
            title=data.title,
            institution_id=data.institution_id,
            principal_investigator=data.principal_investigator,
            domain=data.domain,
            problem_statement=data.problem_statement,
            objectives=data.objectives,
            methodology=data.methodology,
            literature_review=data.literature_review,
            expected_outcomes=data.expected_outcomes,
            timeline=data.timeline,
            status=data.status,
            priority=data.priority,
            budget_total=data.budget_total,
        )
        self.db.add(proposal)
        self.db.commit()
        self.db.refresh(proposal)
        return proposal

    def update(self, proposal: Proposal, data: ProposalUpdate) -> Proposal:
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(proposal, key, value)
        self.db.commit()
        self.db.refresh(proposal)
        return proposal

    def delete(self, proposal: Proposal) -> None:
        self.db.delete(proposal)
        self.db.commit()
