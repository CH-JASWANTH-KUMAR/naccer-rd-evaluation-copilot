import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.assignment import EvaluationAssignment
from app.models.audit_event import AuditEvent
from app.models.evaluation import Evaluation, EvaluationCriterion
from app.models.evaluation_evidence import EvaluationEvidence
from app.models.historical_project import HistoricalProject
from app.models.institution import Institution
from app.models.proposal import Proposal
from app.models.rubric import EvaluationRubric
from app.repositories.institutions import InstitutionRepository
from app.repositories.projects import HistoricalProjectRepository
from app.repositories.proposals import ProposalRepository
from app.schemas.institution import InstitutionCreate
from app.schemas.project import HistoricalProjectCreate
from app.schemas.proposal import ProposalCreate
from app.services.cil_catalogue_corpus import seed_cil_ongoing_projects_corpus


def seed_demo_data(db: Session) -> dict:
    """Populate database with CIL project catalogue corpus and development demo data."""
    inst_repo = InstitutionRepository(db)
    prop_repo = ProposalRepository(db)
    proj_repo = HistoricalProjectRepository(db)

    # 0. Always seed CIL Ongoing Projects Catalogue Corpus
    corpus_res = seed_cil_ongoing_projects_corpus(db)

    # Check if demo data already exists
    existing_demo = db.scalars(select(Proposal).where(Proposal.is_demo.is_(True))).first()
    if existing_demo:
        return {"message": "CIL corpus and demo data already exist.", "corpus": corpus_res}

    # 1. Create Institutions (DEMO DATA)
    inst1 = db.scalars(select(Institution).where(Institution.code == "IIT-ISM-DEMO")).first()
    if not inst1:
        inst1 = inst_repo.create(
            InstitutionCreate(
                name="IIT (ISM) Dhanbad [DEMO DATA]",
                code="IIT-ISM-DEMO",
                type="ACADEMIC",
                location="Dhanbad, Jharkhand",
            )
        )

    inst2 = db.scalars(select(Institution).where(Institution.code == "CSIR-CIMFR-DEMO")).first()
    if not inst2:
        inst2 = inst_repo.create(
            InstitutionCreate(
                name="CSIR-CIMFR [DEMO DATA]",
                code="CSIR-CIMFR-DEMO",
                type="RESEARCH_INSTITUTE",
                location="Dhanbad, Jharkhand",
            )
        )

    inst3 = db.scalars(select(Institution).where(Institution.code == "NIT-RKL-DEMO")).first()
    if not inst3:
        inst3 = inst_repo.create(
            InstitutionCreate(
                name="NIT Rourkela [DEMO DATA]",
                code="NIT-RKL-DEMO",
                type="ACADEMIC",
                location="Rourkela, Odisha",
            )
        )

    # 2. Create Synthetic Predictive Maintenance Proposal (DEMO DATA)
    pred_prop = Proposal(
        id=str(uuid.uuid4()),
        proposal_reference="PR-2026-PRED-MAINT",
        title="[DEMO DATA] AI-Assisted Predictive Maintenance Framework for Heavy Mining Machinery",
        institution_id=inst1.id,
        principal_investigator="Dr. A. K. Sharma [DEMO]",
        domain="Automation & Machinery Health",
        problem_statement=(
            "Unscheduled breakdowns of heavy earth-moving machinery (HEMM) in Coal India open-cast mines "
            "cause significant operational downtime and safety hazards. Current maintenance relies on fixed intervals "
            "or reactive repair."
        ),
        objectives=(
            "1. Deploy spatial vibration and thermal IoT sensors on shovel-dumper fleets.\n"
            "2. Develop edge AI anomaly detection model for failure prediction.\n"
            "3. Reduce unscheduled fleet downtime by 25% across pilot mines."
        ),
        methodology=(
            "Tri-axial accelerometer and acoustic sensor mesh deployment with edge computing nodes. "
            "LSTM temporal neural network models for predictive failure signatures."
        ),
        expected_outcomes="Real-time machinery health monitoring dashboard and early fault warning alert system.",
        status="UNDER_REVIEW",
        priority="HIGH",
        budget_total=4850000.0,
        completeness_status="INCOMPLETE",
        compliance_status="NEEDS_JUSTIFICATION",
        processing_status="PROCESSED",
        is_demo=True,
    )
    db.add(pred_prop)

    prop2 = prop_repo.create(
        ProposalCreate(
            title="[DEMO DATA] Eco-Friendly Coal Tailings Bio-Leaching Microorganisms",
            institution_id=inst2.id,
            principal_investigator="Dr. S. Mukherjee [DEMO]",
            domain="Mineral Beneficiation",
            problem_statement="Structural demo problem statement for biological mineral recovery.",
            objectives="Demo objective: Microbial leaching of high-purity minerals from tailing dumps.",
            methodology="Lab bio-reactor batch testing.",
            expected_outcomes="Eco-friendly mineral extraction.",
            status="AWAITING_REVIEW",
            priority="MEDIUM",
            budget_total=3200000.0,
        )
    )
    prop2.is_demo = True

    prop3 = prop_repo.create(
        ProposalCreate(
            title="[DEMO DATA] Autonomous Haulage Machinery Fleets in Open-Cast Operations",
            institution_id=inst3.id,
            principal_investigator="Prof. A. Dasgupta [DEMO]",
            domain="Automation & Robotics in Mining",
            problem_statement="Structural demo problem statement for autonomous mine haulers.",
            objectives="Demo objective: LiDAR and V2X wireless collision avoidance.",
            methodology="Scale prototype testing in bench simulator.",
            expected_outcomes="Improved fleet utilization efficiency.",
            status="POTENTIAL_ISSUES",
            priority="HIGH",
            budget_total=8900000.0,
        )
    )
    prop3.is_demo = True

    db.flush()

    # 3. Create Historical Projects (DEMO DATA - SYNTHETIC)
    p1 = db.scalars(select(HistoricalProject).where(HistoricalProject.project_code == "HIST-2024-088-DEMO")).first()
    if not p1:
        proj_repo.create(
            HistoricalProjectCreate(
                project_code="HIST-2024-088-DEMO",
                title="[DEMO DATA] Wireless Mesh Gas Sensors for Underground Mines",
                institution="IIT (ISM) Dhanbad [DEMO DATA]",
                domain="Mine Safety & Ventilation",
                objectives="Completed demo project evaluating ZigBee gas sensors.",
                methodology="Underground field trial.",
                technology="ZigBee Mesh, Electrochemical Sensors",
                status="COMPLETED",
                approved_cost=4100000.0,
                approved_cost_raw="Rs. 41.00 Lakhs",
                source="NaCCER_DEMO_ARCHIVE",
                source_type="SYNTHETIC",
                verification_status="NEEDS_REVIEW",
            )
        )

    p2 = db.scalars(select(HistoricalProject).where(HistoricalProject.project_code == "HIST-2023-041-DEMO")).first()
    if not p2:
        proj_repo.create(
            HistoricalProjectCreate(
                project_code="HIST-2023-041-DEMO",
                title="[DEMO DATA] Microbial Desulfurization of High-Sulfur Indian Coals",
                institution="CSIR-CIMFR [DEMO DATA]",
                domain="Clean Coal Technology",
                objectives="Completed demo project on biological sulfur reduction.",
                methodology="Bioreactor extraction.",
                technology="Acidithiobacillus ferrooxidans",
                status="COMPLETED",
                approved_cost=3500000.0,
                approved_cost_raw="Rs. 35.00 Lakhs",
                source="NaCCER_DEMO_ARCHIVE",
                source_type="SYNTHETIC",
                verification_status="NEEDS_REVIEW",
            )
        )

    # 4. Create Evaluation Rubric v1.0 reference if not present
    rubric = db.scalars(select(EvaluationRubric).where(EvaluationRubric.version == "v1.0")).first()

    # 5. Create Demo Evaluation Record for Predictive Maintenance Proposal
    demo_eval = Evaluation(
        id=str(uuid.uuid4()),
        proposal_id=pred_prop.id,
        reviewer_id="Reviewer A (Technical)",
        rubric_version="v1.0",
        rubric_id=rubric.id if rubric else None,
        status="IN_REVIEW",
        overall_score=7.6,
        reviewer_recommendation="FAVORABLE_WITH_CONDITIONS",
        reviewer_summary="Strong technical architecture grounded by historical project HIST-2024-088. Itemized financial component breakdown requires clarification.",
        is_demo=True,
    )
    db.add(demo_eval)
    db.flush()

    # 6. Seed Realistic Demo Reviewer Tasks (Assignments)
    task1 = EvaluationAssignment(
        evaluation_id=demo_eval.id,
        reviewer_id="Reviewer A (Technical)",
        assigned_by="Chair (Admin)",
        task_title="Review scientific methodology and technical feasibility",
        priority="HIGH",
        status="ASSIGNED",
        is_demo=True,
        notes="Focus on edge IoT sensor deployment and LSTM temporal neural network architecture realism.",
    )

    task2 = EvaluationAssignment(
        evaluation_id=demo_eval.id,
        reviewer_id="Reviewer B (Scientific)",
        assigned_by="Chair (Admin)",
        task_title="Verify scientific evidence, metrics and baseline comparison",
        priority="HIGH",
        status="IN_PROGRESS",
        is_demo=True,
        notes="Check prior art alignment with HIST-2024-088 and published heavy machinery vibration papers.",
    )

    task3 = EvaluationAssignment(
        evaluation_id=demo_eval.id,
        reviewer_id="Reviewer C (Financial)",
        assigned_by="Chair (Admin)",
        task_title="Review budget compliance and implementation feasibility",
        priority="MEDIUM",
        status="ASSIGNED",
        is_demo=True,
        notes="Verify ₹48,50,000 declared budget against hardware procurement cost heads.",
    )

    db.add_all([task1, task2, task3])

    # 7. Seed Human Reviewer Scores for MoC Criteria (DEMO DATA)
    c1 = EvaluationCriterion(
        evaluation_id=demo_eval.id,
        criterion_key="CRIT-MOC-01",
        name="Scientific Relevance & Technical Feasibility",
        score=8.0,
        max_score=10.0,
        comments="Reviewer A: Strong IoT sensor mesh architecture and edge AI model description.",
    )

    c2 = EvaluationCriterion(
        evaluation_id=demo_eval.id,
        criterion_key="CRIT-MOC-02",
        name="Methodology Realism & R&D Work Plan",
        score=7.0,
        max_score=10.0,
        comments="Reviewer A: Clear methodology, but dataset size and baseline model require clarification.",
    )

    c3 = EvaluationCriterion(
        evaluation_id=demo_eval.id,
        criterion_key="CRIT-MOC-03",
        name="Project Objectives Realism",
        score=8.0,
        max_score=10.0,
        comments="Reviewer A: Well-defined objectives for heavy mining machinery breakdown prevention.",
    )

    c4 = EvaluationCriterion(
        evaluation_id=demo_eval.id,
        criterion_key="CRIT-MOC-04",
        name="Scientific Evidence Grounding",
        score=8.5,
        max_score=10.0,
        comments="Reviewer B: Grounded by historical project HIST-2024-088 and paper research literature.",
    )

    c5 = EvaluationCriterion(
        evaluation_id=demo_eval.id,
        criterion_key="CRIT-MOC-05",
        name="Literature Review & R&D Status",
        score=8.0,
        max_score=10.0,
        comments="Reviewer B: Good coverage of prior art in coal mine predictive maintenance.",
    )

    c6 = EvaluationCriterion(
        evaluation_id=demo_eval.id,
        criterion_key="CRIT-MOC-06",
        name="Track Record & Institutional Evidence",
        score=7.5,
        max_score=10.0,
        comments="Reviewer B: Submitting institution has established track record in mining sensors.",
    )

    c7 = EvaluationCriterion(
        evaluation_id=demo_eval.id,
        criterion_key="CRIT-MOC-07",
        name="Budget Compliance & Financial Justification",
        score=6.0,
        max_score=10.0,
        comments="Reviewer C: Declared total budget ₹48,50,000 lacks itemized breakdown per cost head.",
    )

    c8 = EvaluationCriterion(
        evaluation_id=demo_eval.id,
        criterion_key="CRIT-MOC-08",
        name="Equipment & Manpower Realism",
        score=7.0,
        max_score=10.0,
        comments="Reviewer C: Equipment budget is realistic for edge computing hardware.",
    )

    db.add_all([c1, c2, c3, c4, c5, c6, c7, c8])

    # 8. Seed Evaluation Evidence Links
    e1 = EvaluationEvidence(
        evaluation_id=demo_eval.id,
        criterion_id=c1.id,
        evidence_type="HISTORICAL_PROJECT",
        source_type="HISTORICAL_PROJECT",
        source_reference="HIST-2024-088-DEMO",
        evidence_text="ZigBee mesh deployment in underground mines evaluating spatial sensor nodes.",
    )
    e2 = EvaluationEvidence(
        evaluation_id=demo_eval.id,
        criterion_id=c4.id,
        evidence_type="PROPOSAL_SECTION",
        source_type="PROPOSAL",
        source_reference="PROP-METHODOLOGY",
        evidence_text="Tri-axial accelerometer and acoustic sensor mesh deployment with edge computing nodes.",
    )
    db.add_all([e1, e2])

    # 9. Create Audit Events
    import json

    db.add_all([
        AuditEvent(
            proposal_id=pred_prop.id,
            action="REVIEW_TASK_CREATED",
            performed_by="Chair (Admin)",
            details=json.dumps({"task_count": 3, "proposal_id": pred_prop.id, "is_demo": True}),
        ),
        AuditEvent(
            proposal_id=pred_prop.id,
            action="REVIEWER_ASSIGNED",
            performed_by="Chair (Admin)",
            details=json.dumps({"reviewers": ["Reviewer A (Technical)", "Reviewer B (Scientific)", "Reviewer C (Financial)"], "is_demo": True}),
        ),
        AuditEvent(
            proposal_id=pred_prop.id,
            action="RUBRIC_SCORE_ENTERED",
            performed_by="Reviewer A (Technical)",
            details=json.dumps({"criteria_scored": 3, "average_score": 7.67, "is_demo": True}),
        ),
        AuditEvent(
            proposal_id=pred_prop.id,
            action="EVIDENCE_READINESS_CALCULATED",
            performed_by="System Engine",
            details=json.dumps({"evidence_readiness_score": 72, "interpretation": "Moderate evidence coverage", "is_demo": True}),
        ),
    ])

    db.commit()

    return {"message": "CIL corpus and realistic demo evaluation data successfully created.", "demo_proposal_id": pred_prop.id}
