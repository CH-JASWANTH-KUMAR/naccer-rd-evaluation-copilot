from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient

FIXTURES_DIR = Path(__file__).parent / "fixtures"
PDF_PATH = FIXTURES_DIR / "synthetic_proposal_complete.pdf"


def test_upload_proposal_pdf_contract_and_clean_title(client: TestClient):
    # 1. Create Institution
    inst_res = client.post(
        "/api/v1/institutions",
        json={"name": "CSIR-CIMFR Upload Test", "code": "CIMFR-UP", "type": "RESEARCH_INSTITUTE", "location": "Dhanbad"},
    )
    inst_id = inst_res.json()["id"]

    # 2. Upload actual synthetic proposal PDF
    with open(PDF_PATH, "rb") as f:
        pdf_bytes = f.read()

    upload_res = client.post(
        "/api/v1/proposals/upload",
        files={"file": ("synthetic_rd_proposal_predictive_maintenance.pdf", pdf_bytes, "application/pdf")},
        data={
            "title": "AI-Assisted Predictive Maintenance Framework for Coal Handling and Mining Equipment",
            "principal_investigator": "Dr. Predictive Maintenance PI",
            "domain": "Automation & Robotics",
            "institution_id": inst_id,
            "budget_total": "4500000.0",
        },
    )

    assert upload_res.status_code == 201
    data = upload_res.json()
    assert data["id"] is not None
    # Crucial Title Verification: Filename must NEVER be appended to Full Project Title
    assert data["title"] == "AI-Assisted Predictive Maintenance Framework for Coal Handling and Mining Equipment"
    assert "synthetic_rd_proposal_predictive_maintenance" not in data["title"]
    assert data["principal_investigator"] == "Dr. Predictive Maintenance PI"
    assert data["domain"] == "Automation & Robotics"
    assert data["budget_total"] == 4500000.0


def test_upload_proposal_invalid_file_type(client: TestClient):
    txt_bytes = b"This is a text file, not a PDF."
    upload_res = client.post(
        "/api/v1/proposals/upload",
        files={"file": ("invalid_document.txt", BytesIO(txt_bytes), "text/plain")},
        data={"title": "Invalid Document Test"},
    )
    assert upload_res.status_code == 400
    assert "Only PDF documents (.pdf) are supported" in upload_res.json()["detail"]


def test_upload_proposal_missing_file(client: TestClient):
    upload_res = client.post(
        "/api/v1/proposals/upload",
        data={"title": "Missing File Test"},
    )
    assert upload_res.status_code == 422
