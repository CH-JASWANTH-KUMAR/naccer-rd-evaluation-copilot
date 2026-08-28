from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.institutions import InstitutionRepository
from app.repositories.proposals import ProposalRepository
from app.schemas.proposal import ProposalCreate, ProposalRead, ProposalUpdate


class ProposalService:
    def __init__(self, db: Session):
        self.repo = ProposalRepository(db)
        self.inst_repo = InstitutionRepository(db)

    def get_all(self, domain: str | None = None, status_filter: str | None = None) -> list[ProposalRead]:
        proposals = self.repo.get_all(domain=domain, status=status_filter)
        return [ProposalRead.model_validate(p) for p in proposals]

    def get_by_id(self, proposal_id: str) -> ProposalRead:
        proposal = self.repo.get_by_id(proposal_id)
        if not proposal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Proposal with id '{proposal_id}' not found"
            )
        return ProposalRead.model_validate(proposal)

    def create(self, data: ProposalCreate) -> ProposalRead:
        # Validate Institution existence
        institution = self.inst_repo.get_by_id(data.institution_id)
        if not institution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Institution with id '{data.institution_id}' does not exist",
            )

        if data.budget_total < 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Proposal budget cannot be negative"
            )

        proposal = self.repo.create(data)
        # Fetch fresh with institution loaded
        proposal_loaded = self.repo.get_by_id(proposal.id)
        return ProposalRead.model_validate(proposal_loaded)

    def update(self, proposal_id: str, data: ProposalUpdate) -> ProposalRead:
        proposal = self.repo.get_by_id(proposal_id)
        if not proposal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Proposal with id '{proposal_id}' not found"
            )
        updated = self.repo.update(proposal, data)
        return ProposalRead.model_validate(updated)

    def delete(self, proposal_id: str) -> None:
        proposal = self.repo.get_by_id(proposal_id)
        if not proposal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Proposal with id '{proposal_id}' not found"
            )
        self.repo.delete(proposal)
