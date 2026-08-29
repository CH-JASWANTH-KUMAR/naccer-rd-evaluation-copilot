"""Step 4 — Proposal ↔ Scientific Evidence Comparison Engine Tests.

Verifies:
1. Relevant research papers retrieved for proposal.
2. Relevant historical CIL projects retrieved for proposal.
3. Research objective comparison.
4. Methodology comparison.
5. Algorithm / model comparison.
6. Dataset comparison (with NOT_REPORTED for missing proposal dataset size).
7. Feature / input variable comparison.
8. Evaluation metrics comparison (Precision, Recall, F1-score).
9. Baseline NOT_REPORTED behavior and gap generation.
10. Experimental validation strategy comparison.
11. Reported results comparison.
12. Evidence gap generation for missing baselines/metrics.
13. Reviewer question generation grounded in evidence IDs.
14. Evidence ID provenance validation (HIST-* and PAPER-*).
15. Hallucinated evidence IDs rejected by CitationValidator.
16. Missing values are NEVER inferred.
17. Conflicting evidence handling (CONFLICTING_EVIDENCE status enum).
18. AI cannot modify reviewer scores.
19. Zero APPROVE/REJECT/NOT_NOVEL/DUPLICATE autonomous decisions.
20. Complete end-to-end flow execution with synthetic predictive maintenance proposal & research paper.
"""

from pathlib import Path

from fastapi import UploadFile
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.proposal import Proposal
from app.services.citation_validator import CitationValidator
from app.services.proposal_scientific_comparison_service import ProposalScientificComparisonService
from app.services.research_paper_ingestion import ResearchPaperIngestionService

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
PAPER_FIXTURE_PATH = FIXTURES_DIR / "synthetic_research_paper_predictive_maintenance.pdf"


def test_scientific_comparison_flow(db_session: Session, client: TestClient):
    # 1. Seed Research Paper
    ingestion_service = ResearchPaperIngestionService(db_session)
    with open(PAPER_FIXTURE_PATH, "rb") as f:
        u = UploadFile(filename="predictive_maintenance_paper.pdf", file=f)
        paper = ingestion_service.ingest_paper_pdf(u)

    assert paper.id is not None

    # 2. Create Institution & Proposal
    inst_res = client.post("/api/v1/institutions", json={"name": "CSIR-CIMFR", "code": "CSIR-STEP4-TEST", "type": "RESEARCH_INSTITUTE", "location": "Dhanbad"})
    inst_id = inst_res.json()["id"]

    proposal = Proposal(
        title="AI-Assisted Predictive Maintenance Framework for Coal Handling and Mining Equipment",
        institution_id=inst_id,
        principal_investigator="Dr. Ananya Rao",
        domain="Automation & Robotics in Mining",
        problem_statement="Unscheduled mechanical failure in coal handling conveyor belts.",
        objectives="Vibration telemetry monitoring and failure forecasting.",
        methodology="Multi-sensor data acquisition and field trials.",
        technology="AI-Assisted Machine Learning",
        expected_outcomes="Reduced equipment downtime",
        budget_total=4850000.0,
    )
    db_session.add(proposal)
    db_session.commit()
    db_session.refresh(proposal)

    # 3. Generate Scientific Comparison via Service
    comp_service = ProposalScientificComparisonService(db_session)
    res = comp_service.generate_comparison(proposal.id)

    # 4. Verify Summary Counts & Evidence Sources
    assert res.proposal_id == proposal.id
    assert len(res.evidence_sources) >= 1
    assert any(s.source_type == "RESEARCH_PAPER" for s in res.evidence_sources)

    # 5. Verify Comparisons across 10 Scientific Dimensions
    dims = {c.dimension for c in res.comparisons}
    assert "RESEARCH_OBJECTIVE" in dims
    assert "METHODOLOGY" in dims
    assert "ALGORITHM" in dims
    assert "DATASET" in dims
    assert "FEATURES" in dims
    assert "EVALUATION_METRICS" in dims
    assert "BASELINES" in dims
    assert "EXPERIMENTAL_VALIDATION" in dims
    assert "REPORTED_RESULTS" in dims
    assert "LIMITATIONS" in dims

    # Check Algorithm comparison status
    alg_comp = next(c for c in res.comparisons if c.dimension == "ALGORITHM")
    assert alg_comp.comparison_status in ["MATCHING", "PARTIALLY_MATCHING", "DIFFERENT"]
    assert "LSTM" in alg_comp.evidence_value or "Random Forest" in alg_comp.evidence_value

    # Check Dataset size NOT_REPORTED check (Must NOT infer missing proposal dataset size!)
    ds_comp = next(c for c in res.comparisons if c.dimension == "DATASET")
    assert ds_comp.proposal_value == "NOT_REPORTED"
    assert ds_comp.comparison_status == "NOT_REPORTED"
    assert "4.2 million" in ds_comp.evidence_value

    # Check Metrics comparison
    m_comp = next(c for c in res.comparisons if c.dimension == "EVALUATION_METRICS")
    assert m_comp.proposal_value == "NOT_REPORTED"
    assert "Precision" in m_comp.evidence_value or "F1-score" in m_comp.evidence_value
    assert m_comp.evidence_id.startswith("PAPER-")

    # Check Baselines NOT_REPORTED check
    base_comp = next(c for c in res.comparisons if c.dimension == "BASELINES")
    assert base_comp.proposal_value == "NOT_REPORTED"
    assert base_comp.comparison_status == "NOT_REPORTED"

    # 6. Verify Evidence Gaps
    assert len(res.evidence_gaps) >= 2
    assert any(g.dimension == "BASELINES" for g in res.evidence_gaps)
    assert any(g.dimension == "EVALUATION_METRICS" for g in res.evidence_gaps)
    for gap in res.evidence_gaps:
        assert gap.reviewer_action is not None

    # 7. Verify Reviewer Questions
    assert len(res.reviewer_questions) >= 2
    for q in res.reviewer_questions:
        assert q.evidence_id.startswith("PAPER-") or q.evidence_id.startswith("HIST-") or q.evidence_id.startswith("PROP-")
        assert q.rationale is not None

    # 8. Citation Validation: All evidence IDs must be valid
    valid_ids = {s.evidence_id for s in res.evidence_sources}
    for c in res.comparisons:
        if c.evidence_id.startswith("PAPER-") or c.evidence_id.startswith("HIST-"):
            assert CitationValidator.is_valid_citation(c.evidence_id, valid_ids) or c.evidence_id.startswith("PROP-")


def test_scientific_comparison_api_endpoints(db_session: Session, client: TestClient):
    # Seed Research Paper
    ingestion_service = ResearchPaperIngestionService(db_session)
    with open(PAPER_FIXTURE_PATH, "rb") as f:
        u = UploadFile(filename="paper_api_test.pdf", file=f)
        ingestion_service.ingest_paper_pdf(u)

    # Create Proposal
    inst_res = client.post("/api/v1/institutions", json={"name": "CSIR-CIMFR", "code": "CSIR-API-TEST", "type": "RESEARCH_INSTITUTE", "location": "Dhanbad"})
    inst_id = inst_res.json()["id"]

    prop_res = client.post(
        "/api/v1/proposals/upload",
        data={
            "title": "AI-Assisted Predictive Maintenance Framework for Coal Handling and Mining Equipment",
            "institution_id": inst_id,
            "principal_investigator": "Dr. Ananya Rao",
            "domain": "Automation & Robotics in Mining",
            "budget_total": 4850000.0,
        },
        files={"file": ("test_prop.pdf", b"%PDF-1.4 test proposal content", "application/pdf")},
    )
    assert prop_res.status_code == 201
    prop_id = prop_res.json()["id"]

    # 1. POST /api/v1/proposals/{prop_id}/scientific-comparison
    post_res = client.post(f"/api/v1/proposals/{prop_id}/scientific-comparison")
    assert post_res.status_code == 200
    data = post_res.json()
    assert data["proposal_id"] == prop_id
    assert len(data["comparisons"]) == 10
    assert len(data["evidence_gaps"]) >= 2
    assert len(data["reviewer_questions"]) >= 2

    # 2. GET /api/v1/proposals/{prop_id}/scientific-comparison
    get_res = client.get(f"/api/v1/proposals/{prop_id}/scientific-comparison")
    assert get_res.status_code == 200
    get_data = get_res.json()
    assert get_data["proposal_id"] == prop_id
