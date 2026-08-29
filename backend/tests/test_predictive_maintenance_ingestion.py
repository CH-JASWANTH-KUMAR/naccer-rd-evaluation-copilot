from pathlib import Path

from fastapi.testclient import TestClient

FIXTURES_DIR = Path(__file__).parent / "fixtures"
PDF_PATH = FIXTURES_DIR / "synthetic_rd_proposal_predictive_maintenance.pdf"


def test_predictive_maintenance_pdf_ingestion_end_to_end(client: TestClient):
    # 1. Create Institution
    inst_res = client.post(
        "/api/v1/institutions",
        json={"name": "CSIR-CIMFR [DEMO DATA]", "code": "CSIR-CIMFR", "type": "RESEARCH_INSTITUTE", "location": "Dhanbad"},
    )
    assert inst_res.status_code == 201
    inst_id = inst_res.json()["id"]

    # 2. Upload synthetic_rd_proposal_predictive_maintenance.pdf
    with open(PDF_PATH, "rb") as f:
        pdf_bytes = f.read()

    upload_res = client.post(
        "/api/v1/proposals/upload",
        files={"file": ("synthetic_rd_proposal_predictive_maintenance.pdf", pdf_bytes, "application/pdf")},
        data={
            "title": "AI-Assisted Predictive Maintenance Framework for Coal Handling and Mining Equipment",
            "principal_investigator": "Dr. R. K. Verma",  # Administrative PI
            "domain": "Automation & Robotics in Mining",
            "institution_id": inst_id,
            "budget_total": "4850000.0",  # Declared 48.50 Lakhs
        },
    )

    assert upload_res.status_code == 201
    data = upload_res.json()
    proposal_id = data["id"]

    # A. Metadata budget persistence
    assert data["budget_total"] == 4850000.0
    assert data["budget_total"] != 0
    assert data["raw_budget_text"] is not None

    # B. PI Extraction & Discrepancy Preservation
    assert data["principal_investigator"] == "Dr. R. K. Verma"
    assert data["extracted_principal_investigator"] == "Dr. Ananya Rao"
    assert data["extracted_principal_investigator"] != "kumar"

    # C. Completeness Scrutiny Checklist
    comp_res = client.get(f"/api/v1/proposals/{proposal_id}/completeness")
    assert comp_res.status_code == 200
    comp_data = comp_res.json()
    pi_warnings = [f for f in comp_data["findings"] if f["field"] == "principal_investigator"]
    assert len(pi_warnings) > 0
    assert "Dr. R. K. Verma" in pi_warnings[0]["message"]
    assert "Dr. Ananya Rao" in pi_warnings[0]["message"]

    # D. Financial Compliance Scrutiny
    fin_res = client.get(f"/api/v1/proposals/{proposal_id}/compliance")
    assert fin_res.status_code == 200
    fin_data = fin_res.json()

    # Declared = 48.50 Lakhs (4,850,000)
    assert fin_data["declared_total"] == 4850000.0
    # Calculated = 46.50 Lakhs (4,650,000 = 18L + 12L + 6.5L + 7L + 3L)
    assert fin_data["calculated_total"] == 4650000.0
    # Variance = 2.00 Lakhs (200,000)
    assert fin_data["arithmetic_mismatch"] is True
    assert fin_data["difference_amount"] == 200000.0
    # Expected Status = FLAGGED
    assert fin_data["status"] == "FLAGGED"
    assert fin_data["status"] != "COMPLIANT"

    # E. Verify Cost Head Itemized Breakdown
    findings = fin_data["findings"]
    cost_heads = {f["cost_head"]: f["proposed_amount"] for f in findings if f["cost_head"] != "ARITHMETIC_VERIFICATION"}
    assert "Equipment and sensor interfaces" in cost_heads
    assert cost_heads["Equipment and sensor interfaces"] == 1800000.0
    assert "Project personnel" in cost_heads
    assert cost_heads["Project personnel"] == 1200000.0
    assert "Software and computing" in cost_heads
    assert cost_heads["Software and computing"] == 650000.0
    assert "Field trials and travel" in cost_heads
    assert cost_heads["Field trials and travel"] == 700000.0
    assert "Contingency" in cost_heads
    assert cost_heads["Contingency"] == 300000.0

    # F. Page Provenance Verification
    src_res = client.get(f"/api/v1/proposals/{proposal_id}/source")
    assert src_res.status_code == 200
    src_data = src_res.json()
    assert len(src_data["documents"]) > 0
    doc = src_data["documents"][0]
    assert doc["file_size"] > 0
    assert doc["page_count"] >= 1
    assert len(doc["pages"]) >= 1
    assert doc["pages"][0]["page_number"] == 1

    # G. P0.4 Historical Benchmark Search Integration
    sim_res = client.post(f"/api/v1/proposals/{proposal_id}/similar-projects?top_k=3")
    assert sim_res.status_code == 200
    sim_data = sim_res.json()
    assert "results" in sim_data
