from sqlalchemy.orm import Session

from app.repositories.institutions import InstitutionRepository
from app.repositories.projects import HistoricalProjectRepository
from app.repositories.proposals import ProposalRepository
from app.schemas.institution import InstitutionCreate
from app.schemas.project import HistoricalProjectCreate
from app.schemas.proposal import ProposalCreate


def seed_demo_data(db: Session) -> dict:
    """Populate database with clearly marked development-only DEMO DATA."""
    inst_repo = InstitutionRepository(db)
    prop_repo = ProposalRepository(db)
    proj_repo = HistoricalProjectRepository(db)

    # Check if data already exists
    if len(inst_repo.get_all()) > 0:
        return {"message": "Database already contains data. Seed skipped."}

    # 1. Create Institutions (DEMO DATA)
    inst1 = inst_repo.create(
        InstitutionCreate(
            name="IIT (ISM) Dhanbad [DEMO DATA]",
            code="IIT-ISM-DEMO",
            type="ACADEMIC",
            location="Dhanbad, Jharkhand",
        )
    )
    inst2 = inst_repo.create(
        InstitutionCreate(
            name="CSIR-CIMFR [DEMO DATA]",
            code="CSIR-CIMFR-DEMO",
            type="RESEARCH_INSTITUTE",
            location="Dhanbad, Jharkhand",
        )
    )
    inst3 = inst_repo.create(
        InstitutionCreate(
            name="NIT Rourkela [DEMO DATA]",
            code="NIT-RKL-DEMO",
            type="ACADEMIC",
            location="Rourkela, Odisha",
        )
    )

    # 2. Create Proposals (DEMO DATA)
    prop_repo.create(
        ProposalCreate(
            title="[DEMO DATA] AI-Driven Real-Time Methane Leakage Detection System",
            institution_id=inst1.id,
            principal_investigator="Dr. R. K. Verma [DEMO]",
            domain="Mine Safety & Ventilation",
            problem_statement="Structural demo problem statement for methane detection in underground mines.",
            objectives="Demo objective 1: Spatial IoT sensor deployment. Demo objective 2: Edge ventilation control.",
            methodology="Demo methodology utilizing spatial mesh sensor nodes.",
            expected_outcomes="Demo outcome: Reduced venting latency.",
            status="UNDER_REVIEW",
            priority="HIGH",
            budget_total=4850000.0,
        )
    )

    prop_repo.create(
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

    prop_repo.create(
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

    # 3. Create Historical Projects (DEMO DATA - SYNTHETIC)
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

    proj_repo.create(
        HistoricalProjectCreate(
            project_code="HIST-2023-019-DEMO",
            title="[DEMO DATA] Real-Time Rock Mass Rating System using Computer Vision",
            institution="NIT Rourkela [DEMO DATA]",
            domain="Geotechnical Engineering & Rock Mechanics",
            objectives="Completed demo project for rock face classification.",
            methodology="Edge photogrammetry.",
            technology="OpenCV, Edge Computing",
            status="COMPLETED",
            approved_cost=2900000.0,
            approved_cost_raw="Rs. 29.00 Lakhs",
            source="NaCCER_DEMO_ARCHIVE",
            source_type="SYNTHETIC",
            verification_status="NEEDS_REVIEW",
        )
    )

    return {"message": "Demo seed data successfully created."}
