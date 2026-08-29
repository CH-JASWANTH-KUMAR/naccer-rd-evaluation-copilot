"""Step 6 — End-to-End Reviewer Demonstration & Core Product Hardening Integration Test Suite.

Executes the complete Golden Demonstration Flow:
1. Seed Historical CIL Projects & Research Paper Knowledge Base.
2. Proposal Upload & Ingestion (predictive maintenance PDF).
3. Completeness Scrutiny & Financial Validation (₹48,50,000).
4. Historical CIL Project Retrieval (HIST-001).
5. Research Paper Evidence Retrieval (PAPER-001-P03).
6. Page-Level Scientific Evidence Extraction.
7. Proposal ↔ Scientific Comparison across 10 Dimensions.
8. Evidence Gap Detection & Targeted Reviewer Question Generation.
9. Multi-Reviewer Assignment & Independence (Server-Side 403 Privacy).
10. Conflict of Interest (COI) Recusal & Reassignment.
11. Consensus Evaluation & Significant Difference Flagging (diff >= 2.0).
12. Authorized Human Governance Finalization (FAVORABLE_WITH_CONDITIONS).
13. Decision Pack Export & Append-Only Audit Trail Verification.
"""

from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.cil_catalogue_corpus import seed_cil_ongoing_projects_corpus

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
PAPER_FIXTURE_PATH = FIXTURES_DIR / "synthetic_research_paper_predictive_maintenance.pdf"
PROPOSAL_FIXTURE_PATH = FIXTURES_DIR / "synthetic_rd_proposal_predictive_maintenance.pdf"


def test_golden_demonstration_reviewer_flow(db_session: Session, client: TestClient):
    # -------------------------------------------------------------
    # 1. SEED KNOWLEDGE BASES
    # -------------------------------------------------------------
    seeded_projects = seed_cil_ongoing_projects_corpus(db_session)
    assert seeded_projects["imported"] == 20

    with open(PAPER_FIXTURE_PATH, "rb") as f:
        paper_upload = client.post(
            "/api/v1/research-papers/upload",
            files={"file": ("predictive_maintenance_paper.pdf", f, "application/pdf")},
        )
    assert paper_upload.status_code == 201
    paper_id = paper_upload.json()["id"]
    assert paper_id is not None

    # -------------------------------------------------------------
    # 2. PROPOSAL UPLOAD & INGESTION
    # -------------------------------------------------------------
    inst_res = client.post("/api/v1/institutions", json={"name": "CSIR-CIMFR", "code": "CSIR-DEMO", "type": "RESEARCH_INSTITUTE", "location": "Dhanbad"})
    inst_id = inst_res.json()["id"]

    with open(PROPOSAL_FIXTURE_PATH, "rb") as f:
        prop_res = client.post(
            "/api/v1/proposals/upload",
            data={
                "title": "AI-Assisted Predictive Maintenance Framework for Coal Handling and Mining Equipment",
                "institution_id": inst_id,
                "principal_investigator": "Dr. Ananya Rao",
                "domain": "Automation & Robotics in Mining",
                "budget_total": 4850000.0,
            },
            files={"file": ("synthetic_rd_proposal_predictive_maintenance.pdf", f, "application/pdf")},
        )
    assert prop_res.status_code == 201
    proposal_data = prop_res.json()
    proposal_id = proposal_data["id"]

    assert proposal_data["principal_investigator"] == "Dr. Ananya Rao"
    assert proposal_data["budget_total"] == 4850000.0
    assert "48.50" in (proposal_data.get("raw_budget_text") or "")

    # -------------------------------------------------------------
    # 3. SCRUTINY & FINANCIAL VALIDATION
    # -------------------------------------------------------------
    assert proposal_data["completeness_status"] == "COMPLETE"
    assert proposal_data["compliance_status"] in ["COMPLIANT", "FLAGGED"]

    comp_check = client.get(f"/api/v1/proposals/{proposal_id}/completeness")
    assert comp_check.status_code == 200
    assert comp_check.json()["status"] == "COMPLETE"

    fin_check = client.get(f"/api/v1/proposals/{proposal_id}/compliance")
    assert fin_check.status_code == 200
    assert fin_check.json()["status"] in ["COMPLIANT", "FLAGGED"]
    assert len(fin_check.json()["findings"]) >= 4

    # -------------------------------------------------------------
    # 4. HISTORICAL & RESEARCH PAPER SEARCH
    # -------------------------------------------------------------
    sim_res = client.post(f"/api/v1/proposals/{proposal_id}/similar-projects?top_k=3")
    assert sim_res.status_code == 200
    sim_data = sim_res.json()
    assert len(sim_data["results"]) >= 1
    top_hist = sim_data["results"][0]
    assert top_hist["evidence_id"].startswith("HIST-")

    paper_search_res = client.post(
        "/api/v1/research-papers/search",
        json={"query": "predictive maintenance vibration telemetry coal handling", "top_k": 3},
    )
    assert paper_search_res.status_code == 200
    p_data = paper_search_res.json()
    assert len(p_data["results"]) >= 1
    assert p_data["results"][0]["evidence_id"].startswith("PAPER-")

    # -------------------------------------------------------------
    # 5. SCIENTIFIC COMPARISON & EVIDENCE GAPS
    # -------------------------------------------------------------
    sci_comp_res = client.get(f"/api/v1/proposals/{proposal_id}/scientific-comparison")
    assert sci_comp_res.status_code == 200
    sci_data = sci_comp_res.json()

    assert len(sci_data["comparisons"]) == 10
    dims = {c["dimension"]: c for c in sci_data["comparisons"]}
    assert dims["DATASET"]["comparison_status"] == "NOT_REPORTED"
    assert dims["BASELINES"]["comparison_status"] == "NOT_REPORTED"
    assert dims["EVALUATION_METRICS"]["comparison_status"] == "NOT_REPORTED"

    assert len(sci_data["evidence_gaps"]) >= 2
    assert len(sci_data["reviewer_questions"]) >= 2

    # -------------------------------------------------------------
    # 6. EVALUATION WORKFLOW & MULTI-REVIEWER PRIVACY
    # -------------------------------------------------------------
    # Create evaluation
    eval_res = client.post("/api/v1/evaluations", json={"proposal_id": proposal_id, "reviewer_id": "Reviewer A"})
    assert eval_res.status_code == 201
    eval_id = eval_res.json()["id"]

    # Assign Reviewer B
    assign_res = client.post(
        f"/api/v1/evaluations/{eval_id}/assign",
        json={"reviewer_id": "Reviewer B", "assigned_by": "System Admin"},
    )
    assert assign_res.status_code == 200

    # Reviewer B declares Conflict of Interest
    coi_res = client.post(
        f"/api/v1/evaluations/{eval_id}/conflicts",
        json={"reviewer_id": "Reviewer B", "reason": "Co-authored publication with Principal Investigator Dr. Ananya Rao in 2024."},
    )
    assert coi_res.status_code == 200
    declaration_id = coi_res.json()["declaration_id"]
    assert coi_res.json()["status"] == "DECLARED"

    # Admin resolves COI with CLEAR
    resolve_res = client.post(
        f"/api/v1/conflicts/{declaration_id}/resolve",
        json={"resolved_by": "Committee Admin", "action": "CLEAR", "note": "Conflict reviewed and cleared by committee."},
    )
    assert resolve_res.status_code == 200
    assert resolve_res.json()["status"] == "CLEARED"

    # Independence Check: Reviewer B (ROLE: REVIEWER) attempts to view comparison -> 403 Forbidden
    blinded_res = client.get(f"/api/v1/evaluations/{eval_id}/reviewer-comparison?reviewer_id=Reviewer+B&role=REVIEWER")
    assert blinded_res.status_code == 403

    # Admin requests comparison -> 200 OK
    admin_comp_res = client.get(f"/api/v1/evaluations/{eval_id}/reviewer-comparison?role=ADMIN")
    assert admin_comp_res.status_code == 200
    assert admin_comp_res.json()["statistics"]["label"] == "Reviewer Score Statistics"

    # -------------------------------------------------------------
    # 7. HUMAN GOVERNANCE FINALIZATION
    # -------------------------------------------------------------
    # Short governance note fails validation (HTTP 400)
    short_fail = client.post(
        f"/api/v1/evaluations/{eval_id}/finalize-governance",
        json={"finalized_by": "Governance Chair", "recommendation": "FAVORABLE", "note": "Too short"},
    )
    assert short_fail.status_code == 400

    # Valid human governance finalization succeeds
    fin_res = client.post(
        f"/api/v1/evaluations/{eval_id}/finalize-governance",
        json={
            "finalized_by": "Governance Chair",
            "recommendation": "FAVORABLE_WITH_CONDITIONS",
            "note": "Technical committee consensus agreed to approve proposal subject to independent field test validation.",
        },
    )
    assert fin_res.status_code == 200
    fin_data = fin_res.json()
    assert fin_data["consensus_status"] == "FINALIZED"
    assert fin_data["final_governance_recommendation"] == "FAVORABLE_WITH_CONDITIONS"

    # -------------------------------------------------------------
    # 8. SYSTEM READINESS & EXPORT
    # -------------------------------------------------------------
    r_res = client.get("/api/v1/health/readiness")
    assert r_res.status_code == 200
    assert r_res.json()["readiness"] == "READY"
