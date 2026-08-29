from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.proposals import ProposalRepository
from app.schemas.proposal import ProposalCreate, ProposalRead, ProposalUpdate


class ProposalService:
    def __init__(self, db: Session):
        self.repo = ProposalRepository(db)

    def get_all_proposals(
        self,
        domain: str | None = None,
        status_filter: str | None = None,
        completeness_status: str | None = None,
        compliance_status: str | None = None,
        search: str | None = None,
    ) -> list[ProposalRead]:
        proposals = self.repo.get_all(
            domain=domain,
            status=status_filter,
            completeness_status=completeness_status,
            compliance_status=compliance_status,
            search=search,
        )
        return [ProposalRead.model_validate(p) for p in proposals]

    def get_proposal_by_id(self, proposal_id: str) -> ProposalRead:
        proposal = self.repo.get_by_id(proposal_id)
        if not proposal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Proposal with ID '{proposal_id}' not found.",
            )
        prop_read = ProposalRead.model_validate(proposal)

        if proposal.documents:
            doc = proposal.documents[0]
            if doc.pages:
                pages_text = [(p.page_number, p.text) for p in doc.pages]
                from app.services.proposal_ingestion import ProposalIngestionService
                from app.services.proposal_section_parser import parse_proposal_sections

                parsed_data = parse_proposal_sections(pages_text)
                svc = ProposalIngestionService(self.repo.db)
                prop_read.structured_sections = svc._build_structured_sections(
                    parsed_data["sections"], proposal.document_type or "R&D_PROPOSAL"
                )

        return prop_read

    def create_proposal(self, data: ProposalCreate) -> ProposalRead:
        proposal = self.repo.create(data)
        return ProposalRead.model_validate(proposal)

    def update_proposal(self, proposal_id: str, data: ProposalUpdate) -> ProposalRead:
        proposal = self.repo.get_by_id(proposal_id)
        if not proposal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Proposal with ID '{proposal_id}' not found.",
            )
        updated = self.repo.update(proposal, data)
        return ProposalRead.model_validate(updated)
