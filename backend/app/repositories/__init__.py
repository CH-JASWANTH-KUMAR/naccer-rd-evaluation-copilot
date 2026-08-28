from app.repositories.documents import DocumentRepository
from app.repositories.institutions import InstitutionRepository
from app.repositories.projects import HistoricalProjectRepository
from app.repositories.proposals import ProposalRepository

__all__ = [
    "InstitutionRepository",
    "ProposalRepository",
    "HistoricalProjectRepository",
    "DocumentRepository",
]
