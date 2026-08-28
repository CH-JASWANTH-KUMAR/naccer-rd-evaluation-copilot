from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.endpoints import documents, health, institutions, projects, proposals
from app.core.database import get_db
from app.services.seed import seed_demo_data

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(institutions.router, prefix="/institutions", tags=["Institutions"])
api_router.include_router(proposals.router, prefix="/proposals", tags=["Proposals"])
api_router.include_router(projects.router, tags=["Historical Projects"])
api_router.include_router(documents.router, tags=["Document Processing"])


@api_router.post("/seed", tags=["Development"], summary="Seed Demo Data")
def trigger_seed_demo_data(db: Session = Depends(get_db)):
    """Development-only seed data generator endpoint."""
    return seed_demo_data(db)
