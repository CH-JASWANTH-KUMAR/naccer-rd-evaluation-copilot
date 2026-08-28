from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.rubric import EvaluationRubricRead
from app.services.rubric_service import RubricService

router = APIRouter()


@router.get("", response_model=list[EvaluationRubricRead], summary="List evaluation rubrics")
def list_rubrics(db: Session = Depends(get_db)):
    """Retrieve list of configurable evaluation rubrics."""
    service = RubricService(db)
    return service.get_all_rubrics()


@router.get("/active", response_model=EvaluationRubricRead, summary="Get active evaluation rubric")
def get_active_rubric(db: Session = Depends(get_db)):
    """Retrieve the currently active default evaluation rubric."""
    service = RubricService(db)
    rubric = service.get_or_create_active_rubric()
    return EvaluationRubricRead.model_validate(rubric)
