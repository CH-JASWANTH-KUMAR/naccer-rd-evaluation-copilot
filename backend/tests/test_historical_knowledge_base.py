"""Step 1 — Historical Project Knowledge Base & Retrieval Tests.

Verifies:
1. Ingestion of official 20 CIL ongoing R&D projects catalogue (31.03.2026).
2. Field preservation: project_code, title, implementing agencies, dates, outlays, source document, source pages.
3. Deterministic Evidence ID generation (HIST-001, HIST-002, etc.).
4. Multi-dimensional technical retrieval for predictive maintenance proposal.
5. Explainable matched dimensions and evidence provenance.
6. Integration with RAGContextBuilder and CitationValidator.
"""

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.evaluation import Evaluation
from app.models.historical_project import HistoricalProject
from app.models.proposal import Proposal
from app.schemas.search import SimilaritySearchRequest
from app.services.cil_catalogue_corpus import seed_cil_ongoing_projects_corpus
from app.services.historical_search_service import HistoricalProjectSearchService
from app.services.rag_context_builder import RAGContextBuilder


def test_cil_catalogue_corpus_ingestion_and_field_preservation(db_session: Session):
    # 1. Execute CIL Corpus Seeding
    res = seed_cil_ongoing_projects_corpus(db_session)
    assert res["total_projects"] == 20

    # 2. Query all Historical Projects
    projects = db_session.scalars(select(HistoricalProject).order_by(HistoricalProject.project_code.asc())).all()
    assert len(projects) >= 20

    # 3. Verify Specific Known Projects
    # Project 11: IoT Longwall Shield Monitoring
    proj_11 = db_session.scalar(select(HistoricalProject).where(HistoricalProject.project_code == "CIL/R&D/01/84/2025"))
    assert proj_11 is not None
    assert "Longwall Shield Pressures" in proj_11.title
    assert "NaCCER" in proj_11.institution
    assert proj_11.source_page_start == 6
    assert proj_11.source_document_name == "31_03_2026_RD ongoing projects.pdf"
    assert proj_11.start_date is not None
    assert proj_11.completion_date is not None

    # Project 1: CO2 Conversion
    proj_1 = db_session.scalar(select(HistoricalProject).where(HistoricalProject.project_code == "CIL/R&D/04/14/2021"))
    assert proj_1 is not None
    assert "methanol" in proj_1.title.lower()
    assert proj_1.source_page_start == 1

    # Project 4: 5G Opencast Network
    proj_4 = db_session.scalar(select(HistoricalProject).where(HistoricalProject.project_code == "CIL/R&D/05/03/2024"))
    assert proj_4 is not None
    assert "5G Captive" in proj_4.title
    assert proj_4.source_page_start == 2

    # Project 13: 4G LTE/5G Underground Mines
    proj_13 = db_session.scalar(select(HistoricalProject).where(HistoricalProject.project_code == "CIL/R&D/05/04/2025"))
    assert proj_13 is not None
    assert "Jhanjhra" in proj_13.title
    assert proj_13.source_page_start == 7

    # Project 15: AI Fire Detection
    proj_15 = db_session.scalar(select(HistoricalProject).where(HistoricalProject.project_code == "CIL/R&D/01/86/2025"))
    assert proj_15 is not None
    assert "AI-Enabled Fire Detection" in proj_15.title
    assert proj_15.source_page_start == 8

    # Project 20: Hydrokinetic Pumped Storage
    proj_20 = db_session.scalar(select(HistoricalProject).where(HistoricalProject.project_code == "CIL/R&D/05/05/2026"))
    assert proj_20 is not None
    assert "Hydrokinetic" in proj_20.title
    assert proj_20.source_page_start == 12


def test_predictive_maintenance_proposal_historical_retrieval(db_session: Session):
    # Ensure corpus is populated
    seed_cil_ongoing_projects_corpus(db_session)

    search_service = HistoricalProjectSearchService(db_session)

    # Search query simulating predictive maintenance proposal
    req = SimilaritySearchRequest(
        title="AI-Assisted Predictive Maintenance Framework for Coal Handling and Mining Equipment",
        objectives="Deploy IoT telemetry sensors, train edge AI models for failure forecasting, automated alert dashboard",
        problem_statement="Mechanical failure of coal handling equipment causes downtime and safety hazards in underground and opencast mines",
        methodology="Multi-sensor data acquisition, feature extraction, continuous anomaly detection",
        technology="IoT sensors, vibration telemetry, edge computing, PyTorch AI inference models",
        domain="Automation & Robotics in Mining",
        top_k=5,
    )

    response = search_service.search_similar_projects(req)

    assert response.results_count > 0
    results = response.results

    # Verify deterministic Evidence IDs (HIST-001, HIST-002, etc.)
    for idx, r in enumerate(results, start=1):
        assert r.evidence_id == f"HIST-{idx:03d}"
        assert r.project_code is not None
        assert r.provenance.source_document_name == "31_03_2026_RD ongoing projects.pdf"
        assert r.provenance.source_page_start is not None
        assert len(r.matched_dimensions) > 0

    # Verify technically relevant mining projects retrieved
    retrieved_codes = [r.project_code for r in results]
    # Project 11 (IoT Longwall Shield Monitoring/Predictive Maintenance), Project 13 (Mine Electronics Automation & IoT), Project 15 (AI Fire Detection)
    relevant_target_codes = {"CIL/R&D/01/84/2025", "CIL/R&D/05/04/2025", "CIL/R&D/01/86/2025", "CIL/R&D/05/03/2024", "CIL/R&D/01/88/2026"}
    assert len(set(retrieved_codes).intersection(relevant_target_codes)) > 0


def test_rag_integration_with_historical_evidence_ids(db_session: Session, client: TestClient):
    seed_cil_ongoing_projects_corpus(db_session)

    # 1. Create Institution & Proposal
    inst_res = client.post(
        "/api/v1/institutions",
        json={"name": "CSIR-CIMFR", "code": "CSIR-CIMFR-RAG", "type": "RESEARCH_INSTITUTE", "location": "Dhanbad"},
    )
    inst_id = inst_res.json()["id"]

    prop = Proposal(
        title="AI-Assisted Predictive Maintenance Framework for Coal Handling and Mining Equipment",
        institution_id=inst_id,
        principal_investigator="Dr. Ananya Rao",
        domain="Automation & Robotics in Mining",
        problem_statement="Equipment failure downtime in coal mines.",
        objectives="IoT telemetry sensors and edge AI models.",
        methodology="Multi-sensor data acquisition.",
        budget_total=4850000.0,
    )
    db_session.add(prop)
    db_session.commit()
    db_session.refresh(prop)

    # 2. Retrieve Historical Similarity Results
    search_service = HistoricalProjectSearchService(db_session)
    search_res = search_service.search_similar_projects(
        SimilaritySearchRequest(
            title=prop.title,
            objectives=prop.objectives,
            technology=prop.technology,
            domain=prop.domain,
            top_k=5,
        )
    )

    # 3. Create Evaluation & RAGEvidencePackage
    eval_res = client.post("/api/v1/evaluations", json={"proposal_id": prop.id, "reviewer_id": "rev_test_01", "reviewer_name": "Dr. Reviewer"})
    assert eval_res.status_code == 201
    eval_id = eval_res.json()["id"]

    eval_obj = db_session.query(Evaluation).filter(Evaluation.id == eval_id).first()
    assert eval_obj is not None

    rag_package = RAGContextBuilder.build_context_package(
        evaluation=eval_obj,
        proposal=prop,
        completeness={"status": "COMPLETE", "missing_fields": []},
        financial={"status": "FLAGGED", "declared_total": 4850000.0, "arithmetic_mismatch": True},
        historical_results=search_res.results,
    )

    # 4. Verify valid_evidence_ids contains HIST-* IDs
    hist_ids = [eid for eid in rag_package.valid_evidence_ids if eid.startswith("HIST-")]
    assert len(hist_ids) > 0
    assert "HIST-001" in rag_package.valid_evidence_ids

    # 5. Verify Evidence ID Map contains exact source provenance
    h1 = rag_package.evidence_id_map["HIST-001"]
    assert h1["source_type"] == "HISTORICAL_PROJECT"
    assert "Project Code:" in h1["source_reference"]
    assert h1["page_start"] is not None
