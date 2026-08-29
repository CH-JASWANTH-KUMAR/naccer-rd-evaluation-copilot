from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.rubric import EvaluationRubric, RubricCriterion
from app.schemas.rubric import EvaluationRubricRead

OFFICIAL_MOC_SOURCE_DOC = "GUIDELINES FOR RESEARCH PROJECTS OF MINISTRY OF COAL (FEBRUARY 2021)"
OFFICIAL_MOC_SECTION = "10.0 EVALUATION OF S&T PROJECT PROPOSAL"


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
        if rubric and len(rubric.criteria) >= 8:
            return rubric

        # If a rubric exists but has old default criteria (< 8), update or re-seed
        if not rubric:
            rubric = EvaluationRubric(
                name="NaCCER Official Ministry of Coal Research Proposal Evaluation Rubric",
                version="v1.0",
                description="Structured evaluation rubric derived directly from Section 10.0 of Guidelines for Research Projects of Ministry of Coal (February 2021).",
                is_active=True,
            )
            self.db.add(rubric)
            self.db.commit()
            self.db.refresh(rubric)
        else:
            # Delete outdated pre-Step 7 default criteria if any
            for existing in rubric.criteria:
                self.db.delete(existing)
            self.db.commit()

        official_criteria = [
            RubricCriterion(
                rubric_id=rubric.id,
                key="THRUST_AREA_ALIGNMENT",
                name="Thrust Area Alignment",
                description="Verification that the proposed research falls directly within identified Ministry of Coal thrust areas (Underground/Opencast Productivity, Safety/Health/Environment, Waste to Wealth, Alternative Coal Use, Beneficiation, Exploration, Innovation & Indigenization under Make-in-India).",
                category="ALIGNMENT",
                max_score=10.0,
                weight=1.0,
                display_order=1,
                required=True,
                evidence_required=True,
                source_document=OFFICIAL_MOC_SOURCE_DOC,
                source_page=10,
                source_section=OFFICIAL_MOC_SECTION,
                original_criterion_wording="The project proposal falls within thrust areas of research projects of MoC.",
                scoring_instructions="NOT_SPECIFIED",
                scoring_scale="NOT_SPECIFIED",
                evidence_requirements={"required_fields": ["domain", "technology"], "evidence_types": ["PROP-DOMAIN", "PROP-TECH", "HIST-DOMAIN"]},
            ),
            RubricCriterion(
                rubric_id=rubric.id,
                key="TRACK_RECORD_EXPERTISE",
                name="Track Record & Agency Expertise",
                description="Assessment of past performance, research expertise, CVs of Principal Investigators (PIs), and institutional infrastructure of Principal and Sub-implementing Agencies.",
                category="CAPABILITY",
                max_score=10.0,
                weight=1.0,
                display_order=2,
                required=True,
                evidence_required=True,
                source_document=OFFICIAL_MOC_SOURCE_DOC,
                source_page=10,
                source_section=OFFICIAL_MOC_SECTION,
                original_criterion_wording="Past track record and expertise available with the agency concerned for carrying out the research work.",
                scoring_instructions="NOT_SPECIFIED",
                scoring_scale="NOT_SPECIFIED",
                evidence_requirements={"required_fields": ["principal_investigator", "institution"], "evidence_types": ["PROP-PI", "PROP-INST", "HIST-AGENCY"]},
            ),
            RubricCriterion(
                rubric_id=rubric.id,
                key="PROGRESSIVE_RD_LITERATURE",
                name="Progressive R&D & Literature Status",
                description="Evaluation of progressive R&D content, critical gap identification, and national/international state-of-the-art literature review comparing proposed work against historical CIL projects and research papers.",
                category="NOVELTY",
                max_score=10.0,
                weight=1.0,
                display_order=3,
                required=True,
                evidence_required=True,
                source_document=OFFICIAL_MOC_SOURCE_DOC,
                source_page=10,
                source_section=OFFICIAL_MOC_SECTION,
                original_criterion_wording="Progressive R&D input vis-à-vis earlier projects undertaken and similar R&D work carried out within the country and abroad.",
                scoring_instructions="NOT_SPECIFIED",
                scoring_scale="NOT_SPECIFIED",
                evidence_requirements={"required_fields": ["methodology", "literature_review"], "evidence_types": ["PROP-METH", "PROP-TECH", "HIST-MATCH", "PAPER-MATCH", "PAPER-METRIC"]},
            ),
            RubricCriterion(
                rubric_id=rubric.id,
                key="CLARITY_OF_OBJECTIVES",
                name="Clarity & Definition of Objectives",
                description="Verification that project objectives are clear, pointed (max 4-5 objectives), precise, and confined to specific problem aspects achievable within the scheduled duration.",
                category="TECHNICAL",
                max_score=10.0,
                weight=1.0,
                display_order=4,
                required=True,
                evidence_required=True,
                source_document=OFFICIAL_MOC_SOURCE_DOC,
                source_page=10,
                source_section=OFFICIAL_MOC_SECTION,
                original_criterion_wording="The objectives to be clear and well defined.",
                scoring_instructions="NOT_SPECIFIED",
                scoring_scale="NOT_SPECIFIED",
                evidence_requirements={"required_fields": ["objectives", "problem_statement"], "evidence_types": ["PROP-OBJ", "PROP-PROB"]},
            ),
            RubricCriterion(
                rubric_id=rubric.id,
                key="WORK_PROGRAMME_TIMELINE",
                name="Work Programme & PERT Milestones",
                description="Scrutiny of detailed work elements, Bar chart / PERT network schedule, activity breakdown, and milestone phasing over project duration (preferably 1-2 years, max 3 years).",
                category="FEASIBILITY",
                max_score=10.0,
                weight=1.0,
                display_order=5,
                required=True,
                evidence_required=True,
                source_document=OFFICIAL_MOC_SOURCE_DOC,
                source_page=10,
                source_section=OFFICIAL_MOC_SECTION,
                original_criterion_wording="Details work programme with time frame of each activity spelt out.",
                scoring_instructions="NOT_SPECIFIED",
                scoring_scale="NOT_SPECIFIED",
                evidence_requirements={"required_fields": ["timeline", "duration_months"], "evidence_types": ["PROP-TIMELINE", "PROP-DURATION"]},
            ),
            RubricCriterion(
                rubric_id=rubric.id,
                key="EQUIPMENT_MANPOWER_REALISM",
                name="Equipment & Manpower Realism",
                description="Verification of lead time for equipment procurement, non-duplication of existing infrastructure, JRF/SRF/RA technical manpower engagement, and DGMS field trial clearance requirements.",
                category="FEASIBILITY",
                max_score=10.0,
                weight=1.0,
                display_order=6,
                required=True,
                evidence_required=True,
                source_document=OFFICIAL_MOC_SOURCE_DOC,
                source_page=10,
                source_section=OFFICIAL_MOC_SECTION,
                original_criterion_wording="Realistic time frame for purchase of equipment and recruitment of manpower.",
                scoring_instructions="NOT_SPECIFIED",
                scoring_scale="NOT_SPECIFIED",
                evidence_requirements={"required_fields": ["budget_total"], "evidence_types": ["FIN-EQUIPMENT", "FIN-MANPOWER", "COMP-DGMS"]},
            ),
            RubricCriterion(
                rubric_id=rubric.id,
                key="COST_PROVISIONS_COMPLIANCE",
                name="Cost Provisions & Budgetary Compliance",
                description="Financial audit of budget breakdown under Capital and Revenue heads, contingency ceiling (max 5%), travel limits (max Rs 3.0 Lakhs/inst), overhead caps, and non-admissible items.",
                category="FINANCIAL",
                max_score=10.0,
                weight=1.0,
                display_order=7,
                required=True,
                evidence_required=True,
                source_document=OFFICIAL_MOC_SOURCE_DOC,
                source_page=10,
                source_section=OFFICIAL_MOC_SECTION,
                original_criterion_wording="Cost provisions",
                scoring_instructions="NOT_SPECIFIED",
                scoring_scale="NOT_SPECIFIED",
                evidence_requirements={"required_fields": ["budget_total", "raw_budget_text"], "evidence_types": ["FIN-TOTAL", "FIN-HEADS", "FIN-MISMATCH"]},
            ),
            RubricCriterion(
                rubric_id=rubric.id,
                key="INDUSTRY_BENEFITS_OUTCOMES",
                name="Industry Benefits & Outcome Replication",
                description="Assessment of direct commercial exploitation, tangible industry benefits, operational safety/productivity improvements, and replicability across CIL subsidiaries.",
                category="IMPACT",
                max_score=10.0,
                weight=1.0,
                display_order=8,
                required=True,
                evidence_required=True,
                source_document=OFFICIAL_MOC_SOURCE_DOC,
                source_page=10,
                source_section=OFFICIAL_MOC_SECTION,
                original_criterion_wording="Benefits to be accrued to the industry through the proposed research work.",
                scoring_instructions="NOT_SPECIFIED",
                scoring_scale="NOT_SPECIFIED",
                evidence_requirements={"required_fields": ["expected_outcomes"], "evidence_types": ["PROP-OUTCOMES", "PAPER-RESULTS"]},
            ),
        ]

        for crit in official_criteria:
            self.db.add(crit)

        self.db.commit()
        self.db.refresh(rubric)
        return rubric

    def get_all_rubrics(self) -> list[EvaluationRubricRead]:
        stmt = select(EvaluationRubric).options(joinedload(EvaluationRubric.criteria)).order_by(EvaluationRubric.created_at.desc())
        rubrics = self.db.scalars(stmt).unique().all()
        return [EvaluationRubricRead.model_validate(r) for r in rubrics]
