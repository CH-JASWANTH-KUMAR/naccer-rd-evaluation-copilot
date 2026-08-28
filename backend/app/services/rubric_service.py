from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.rubric import EvaluationRubric, RubricCriterion
from app.schemas.rubric import EvaluationRubricRead


class RubricService:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_active_rubric(self) -> EvaluationRubric:
        stmt = (
            select(EvaluationRubric)
            .options(joinedload(EvaluationRubric.criteria))
            .where(EvaluationRubric.is_active == True)  # noqa: E712
            .order_by(EvaluationRubric.created_at.desc())
        )
        rubric = self.db.scalars(stmt).first()
        if rubric and len(rubric.criteria) > 0:
            return rubric

        # Seed default active rubric
        rubric = EvaluationRubric(
            name="NaCCER R&D Standard Technical Evaluation Rubric",
            version="v1.0",
            description="Configurable decision-support rubric for CMPDI R&D proposal scrutiny.",
            is_active=True,
        )
        self.db.add(rubric)
        self.db.commit()
        self.db.refresh(rubric)

        default_criteria = [
            RubricCriterion(
                rubric_id=rubric.id,
                key="TECHNICAL_SOUNDNESS",
                name="Scientific & Technical Soundness",
                description="Clarity of problem formulation, scientific rigor, and technical feasibility.",
                category="TECHNICAL",
                max_score=10.0,
                weight=0.25,
                display_order=1,
                required=True,
                evidence_required=False,
            ),
            RubricCriterion(
                rubric_id=rubric.id,
                key="METHODOLOGY",
                name="Research Methodology & Work Plan",
                description="Appropriateness of technical approach, experimental design, and timeline.",
                category="TECHNICAL",
                max_score=10.0,
                weight=0.20,
                display_order=2,
                required=True,
                evidence_required=False,
            ),
            RubricCriterion(
                rubric_id=rubric.id,
                key="EXPECTED_OUTCOMES",
                name="Expected Deliverables & Impact",
                description="Credibility and industrial applicability of expected R&D outcomes.",
                category="FEASIBILITY",
                max_score=10.0,
                weight=0.20,
                display_order=3,
                required=True,
                evidence_required=False,
            ),
            RubricCriterion(
                rubric_id=rubric.id,
                key="NOVELTY",
                name="Originality & Novelty Assessment",
                description="Uniqueness of proposed solution vs historical CIL/CMPDI benchmark projects.",
                category="NOVELTY",
                max_score=10.0,
                weight=0.15,
                display_order=4,
                required=True,
                evidence_required=True,
            ),
            RubricCriterion(
                rubric_id=rubric.id,
                key="ALIGNMENT",
                name="Strategic R&D Thrust Area Alignment",
                description="Alignment with Coal India R&D priority areas (Safety, Environment, Mining Tech).",
                category="COMPLIANCE",
                max_score=10.0,
                weight=0.10,
                display_order=5,
                required=True,
                evidence_required=False,
            ),
            RubricCriterion(
                rubric_id=rubric.id,
                key="FINANCIAL_REASONABLENESS",
                name="Financial Justification & Budget",
                description="Reasonableness of requested equipment, staff, and consumables budget.",
                category="FINANCIAL",
                max_score=10.0,
                weight=0.10,
                display_order=6,
                required=True,
                evidence_required=False,
            ),
        ]

        for crit in default_criteria:
            self.db.add(crit)

        self.db.commit()
        self.db.refresh(rubric)
        return rubric

    def get_all_rubrics(self) -> list[EvaluationRubricRead]:
        stmt = select(EvaluationRubric).options(joinedload(EvaluationRubric.criteria)).order_by(EvaluationRubric.created_at.desc())
        rubrics = self.db.scalars(stmt).unique().all()
        return [EvaluationRubricRead.model_validate(r) for r in rubrics]
