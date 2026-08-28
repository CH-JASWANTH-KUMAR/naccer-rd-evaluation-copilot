from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.document_page import DocumentPage

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
SYNTHETIC_PDF_PATH = FIXTURES_DIR / "synthetic_proposal.pdf"
SCANNED_PDF_PATH = FIXTURES_DIR / "scanned_proposal.pdf"


def _create_test_proposal(client: TestClient) -> str:
    inst_res = client.post(
        "/api/v1/institutions",
        json={"name": "IIT ISM Dhanbad", "code": "IIT-ISM-DOC-TEST", "type": "ACADEMIC", "location": "Dhanbad"},
    )
    inst_id = inst_res.json()["id"]

    prop_res = client.post(
        "/api/v1/proposals",
        json={
            "title": "Synthetic Document Test Proposal",
            "institution_id": inst_id,
            "principal_investigator": "Dr. Document Tester",
            "domain": "Mine Safety",
            "budget_total": 4500000.0,
        },
    )
    return prop_res.json()["id"]


def test_upload_valid_pdf_and_extraction(client: TestClient):
    prop_id = _create_test_proposal(client)

    with open(SYNTHETIC_PDF_PATH, "rb") as f:
        response = client.post(
            f"/api/v1/proposals/{prop_id}/documents",
            files={"file": ("synthetic_proposal.pdf", f, "application/pdf")},
        )

    assert response.status_code == 201
    data = response.json()
    assert data["proposal_id"] == prop_id
    assert data["filename"] == "synthetic_proposal.pdf"
    assert data["processing_status"] == "PROCESSED"
    assert data["pages_count"] == 5
    assert data["sections_count"] >= 4
    doc_id = data["id"]

    # Retrieve document pages
    pages_res = client.get(f"/api/v1/documents/{doc_id}/pages")
    assert pages_res.status_code == 200
    pages = pages_res.json()
    assert len(pages) == 5
    assert pages[0]["page_number"] == 1
    assert "AI-Driven Gas Detection System" in pages[0]["text"]
    assert pages[1]["page_number"] == 2
    assert "Problem Statement" in pages[1]["text"]

    # Retrieve document sections
    sec_res = client.get(f"/api/v1/documents/{doc_id}/sections")
    assert sec_res.status_code == 200
    sections = sec_res.json()
    sec_types = [s["section_type"] for s in sections]
    assert "OBJECTIVES" in sec_types
    assert "METHODOLOGY" in sec_types
    assert "EXPECTED_OUTCOMES" in sec_types
    assert "BUDGET" in sec_types

    # Retrieve proposal documents
    prop_docs_res = client.get(f"/api/v1/proposals/{prop_id}/documents")
    assert prop_docs_res.status_code == 200
    assert len(prop_docs_res.json()) == 1


def test_reject_non_pdf_upload(client: TestClient):
    prop_id = _create_test_proposal(client)
    response = client.post(
        f"/api/v1/proposals/{prop_id}/documents",
        files={"file": ("test.txt", b"plain text content", "text/plain")},
    )
    assert response.status_code == 400
    assert "Only PDF documents" in response.json()["detail"]


def test_reject_empty_upload(client: TestClient):
    prop_id = _create_test_proposal(client)
    response = client.post(
        f"/api/v1/proposals/{prop_id}/documents",
        files={"file": ("empty.pdf", b"", "application/pdf")},
    )
    assert response.status_code == 400
    assert "0 bytes" in response.json()["detail"]


def test_scanned_pdf_failure_handling(client: TestClient):
    prop_id = _create_test_proposal(client)

    with open(SCANNED_PDF_PATH, "rb") as f:
        response = client.post(
            f"/api/v1/proposals/{prop_id}/documents",
            files={"file": ("scanned_proposal.pdf", f, "application/pdf")},
        )

    assert response.status_code == 201
    data = response.json()
    assert data["processing_status"] == "FAILED"
    assert "OCR" in data["processing_error"]


def test_unique_document_page_number_constraint(client: TestClient, db_session: Session):
    prop_id = _create_test_proposal(client)
    with open(SYNTHETIC_PDF_PATH, "rb") as f:
        response = client.post(
            f"/api/v1/proposals/{prop_id}/documents",
            files={"file": ("synthetic_proposal.pdf", f, "application/pdf")},
        )
    doc_id = response.json()["id"]

    # Try inserting duplicate page 1 for document_id
    duplicate_page = DocumentPage(document_id=doc_id, page_number=1, text="Duplicate text")
    db_session.add(duplicate_page)
    with pytest.raises(IntegrityError):
        db_session.commit()
