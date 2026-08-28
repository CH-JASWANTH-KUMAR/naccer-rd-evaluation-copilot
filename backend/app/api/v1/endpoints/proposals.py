from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.proposal import ProposalCreate, ProposalRead, ProposalUpdate
from app.services.proposals import ProposalService

router = APIRouter()


@router.get("", response_model=list[ProposalRead], summary="List all proposals")
def list_proposals(
    domain: str | None = Query(None, description="Filter by research domain"),
    status: str | None = Query(None, description="Filter by proposal status"),
    db: Session = Depends(get_db),
):
    """Retrieve proposals list with optional domain or status filter."""
    service = ProposalService(db)
    return service.get_all(domain=domain, status_filter=status)


@router.post("", response_model=ProposalRead, status_code=status.HTTP_201_CREATED, summary="Create proposal")
def create_proposal(data: ProposalCreate, db: Session = Depends(get_db)):
    """Create and register a new R&D proposal."""
    service = ProposalService(db)
    return service.create(data)


@router.get("/{proposal_id}", response_model=ProposalRead, summary="Get proposal by ID")
def get_proposal(proposal_id: str, db: Session = Depends(get_db)):
    """Retrieve detailed proposal view by ID."""
    service = ProposalService(db)
    return service.get_by_id(proposal_id)


@router.patch("/{proposal_id}", response_model=ProposalRead, summary="Update proposal")
def update_proposal(proposal_id: str, data: ProposalUpdate, db: Session = Depends(get_db)):
    """Update proposal fields."""
    service = ProposalService(db)
    return service.update(proposal_id, data)


@router.delete("/{proposal_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete proposal")
def delete_proposal(proposal_id: str, db: Session = Depends(get_db)):
    """Delete proposal record."""
    service = ProposalService(db)
    service.delete(proposal_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
