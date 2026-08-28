from pathlib import Path

from fastapi.testclient import TestClient

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
PROPOSAL_COMPLETE_PATH = FIXTURES_DIR / "synthetic_proposal_complete.pdf"
PROPOSAL_INCOMPLETE_PATH = FIXTURES_DIR / "synthetic_proposal_incomplete.pdf"


def test_proposal_intake_complete_pdf(client: TestClient):
    with open(PROPOSAL_COMPLETE_PATH, "rb") as f:
        res = client.post(
            "/api/v1/proposals/upload",
            files={"file": ("synthetic_proposal_complete.pdf", f, "application/pdf")},
        )
    assert res.status_code == 201
    data = res.json()
    assert data["proposal_reference"].startswith("PR-2026-")
    assert "Methane" in data["title"]
    assert data["completeness_status"] == "COMPLETE"
    assert data["compliance_status"] == "COMPLIANT"
    assert data["processing_status"] == "READY_FOR_REVIEW"
    assert data["budget_total"] > 0

    prop_id = data["id"]

    # 1. Test Source Page Provenance Endpoint
    src_res = client.get(f"/api/v1/proposals/{prop_id}/source")
    assert src_res.status_code == 200
    src_data = src_res.json()
    assert len(src_data["documents"]) >= 1
    assert src_data["documents"][0]["page_count"] >= 1

    # 2. Test Completeness Report Endpoint
    comp_res = client.get(f"/api/v1/proposals/{prop_id}/completeness")
    assert comp_res.status_code == 200
    assert comp_res.json()["status"] == "COMPLETE"

    # 3. Test Financial Compliance Report Endpoint
    fin_res = client.get(f"/api/v1/proposals/{prop_id}/compliance")
    assert fin_res.status_code == 200
    assert fin_res.json()["status"] == "COMPLIANT"

    # 4. Test Integration with P0.4 Similarity Engine Endpoint!
    sim_res = client.post(f"/api/v1/proposals/{prop_id}/similar-projects?top_k=3")
    assert sim_res.status_code == 200
    sim_data = sim_res.json()
    assert "disclaimer" in sim_data
    assert isinstance(sim_data["total_candidates_evaluated"], int)


def test_proposal_intake_incomplete_pdf_and_financial_mismatch(client: TestClient):
    with open(PROPOSAL_INCOMPLETE_PATH, "rb") as f:
        res = client.post(
            "/api/v1/proposals/upload",
            files={"file": ("synthetic_proposal_incomplete.pdf", f, "application/pdf")},
        )
    assert res.status_code == 201
    data = res.json()
    assert data["completeness_status"] == "INCOMPLETE"
    assert data["compliance_status"] == "FLAGGED"
    assert data["processing_status"] == "INCOMPLETE"

    prop_id = data["id"]

    # Test Completeness Findings
    comp_res = client.get(f"/api/v1/proposals/{prop_id}/completeness")
    assert comp_res.status_code == 200
    comp_data = comp_res.json()
    assert comp_data["status"] == "INCOMPLETE"
    assert "methodology" in comp_data["missing_fields"]

    # Test Financial Compliance Findings (Arithmetic Mismatch)
    fin_res = client.get(f"/api/v1/proposals/{prop_id}/compliance")
    assert fin_res.status_code == 200
    fin_data = fin_res.json()
    assert fin_data["status"] == "FLAGGED"
    assert fin_data["arithmetic_mismatch"] is True


def test_proposal_reprocess_endpoint(client: TestClient):
    with open(PROPOSAL_COMPLETE_PATH, "rb") as f:
        res = client.post(
            "/api/v1/proposals/upload",
            files={"file": ("synthetic_proposal_complete.pdf", f, "application/pdf")},
        )
    prop_id = res.json()["id"]

    reprocess_res = client.post(f"/api/v1/proposals/{prop_id}/reprocess")
    assert reprocess_res.status_code == 200
    assert reprocess_res.json()["completeness_status"] == "COMPLETE"
