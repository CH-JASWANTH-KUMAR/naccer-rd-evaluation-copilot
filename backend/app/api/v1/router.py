from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.endpoints import documents, evaluations, health, institutions, projects, proposals, reviewer, rubrics
from app.core.database import get_db
from app.services.seed import seed_demo_data

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(institutions.router, prefix="/institutions", tags=["Institutions"])
api_router.include_router(proposals.router, prefix="/proposals", tags=["Proposals"])
api_router.include_router(evaluations.router, prefix="/evaluations", tags=["Evaluations"])
api_router.include_router(rubrics.router, prefix="/rubrics", tags=["Rubrics"])
api_router.include_router(projects.router, tags=["Historical Projects"])
api_router.include_router(documents.router, tags=["Document Processing"])
api_router.include_router(reviewer.router, tags=["Reviewer Operations"])


@api_router.post("/seed", tags=["Development"], summary="Seed Demo Data")
def trigger_seed_demo_data(db: Session = Depends(get_db)):
    """Development-only seed data generator endpoint."""
    return seed_demo_data(db)
