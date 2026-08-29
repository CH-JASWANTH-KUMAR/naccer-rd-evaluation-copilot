from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.models.rubric import EvaluationRubric, RubricCriterion
from app.schemas.rubric import EvaluationRubricRead, RubricCriterionRead
from app.services.rubric_service import RubricService

router = APIRouter()


@router.get("", response_model=list[EvaluationRubricRead], summary="List evaluation rubrics")
def list_rubrics(db: Session = Depends(get_db)):
    """Retrieve list of configurable evaluation rubrics."""
    service = RubricService(db)
    return service.get_all_rubrics()


@router.get("/active", response_model=EvaluationRubricRead, summary="Get active evaluation rubric")
def get_active_rubric(db: Session = Depends(get_db)):
    """Retrieve the currently active default evaluation rubric (Ministry of Coal 2021 guidelines)."""
    service = RubricService(db)
    rubric = service.get_or_create_active_rubric()
    return EvaluationRubricRead.model_validate(rubric)


@router.get("/{rubric_id}", response_model=EvaluationRubricRead, summary="Get evaluation rubric by ID")
def get_rubric_by_id(rubric_id: str, db: Session = Depends(get_db)):
    """Retrieve specific evaluation rubric version by ID."""
    stmt = select(EvaluationRubric).options(joinedload(EvaluationRubric.criteria)).where(EvaluationRubric.id == rubric_id)
    rubric = db.scalars(stmt).first()
    if not rubric:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Rubric with ID '{rubric_id}' not found.")
    return EvaluationRubricRead.model_validate(rubric)


@router.get("/{rubric_id}/criteria", response_model=list[RubricCriterionRead], summary="Get criteria for rubric")
def get_rubric_criteria(rubric_id: str, db: Session = Depends(get_db)):
    """Retrieve criteria list for a specific rubric version."""
    stmt = select(RubricCriterion).where(RubricCriterion.rubric_id == rubric_id).order_by(RubricCriterion.display_order)
    criteria = db.scalars(stmt).all()
    return [RubricCriterionRead.model_validate(c) for c in criteria]
