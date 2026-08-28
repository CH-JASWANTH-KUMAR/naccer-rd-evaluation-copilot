from pathlib import Path

from fastapi.testclient import TestClient

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
SYNTHETIC_CATALOG_PATH = FIXTURES_DIR / "synthetic_historical_catalog.pdf"


def test_import_historical_pdf_catalog(client: TestClient):
    with open(SYNTHETIC_CATALOG_PATH, "rb") as f:
        response = client.post(
            "/api/v1/historical-projects/import",
            files={"file": ("synthetic_historical_catalog.pdf", f, "application/pdf")},
        )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert data["total_detected"] >= 2
    assert data["imported_count"] >= 2
    assert data["needs_review_count"] >= 0

    batch_id = data["import_batch_id"]

    # Retrieve import batches list
    batches_res = client.get("/api/v1/historical-projects/imports")
    assert batches_res.status_code == 200
    assert len(batches_res.json()) >= 1

    # Retrieve specific import batch detail
    batch_detail = client.get(f"/api/v1/historical-projects/imports/{batch_id}")
    assert batch_detail.status_code == 200
    assert batch_detail.json()["id"] == batch_id


def test_duplicate_pdf_import_prevention(client: TestClient):
    with open(SYNTHETIC_CATALOG_PATH, "rb") as f:
        res1 = client.post(
            "/api/v1/historical-projects/import",
            files={"file": ("synthetic_historical_catalog.pdf", f, "application/pdf")},
        )
    assert res1.status_code == 201

    with open(SYNTHETIC_CATALOG_PATH, "rb") as f:
        res2 = client.post(
            "/api/v1/historical-projects/import",
            files={"file": ("synthetic_historical_catalog.pdf", f, "application/pdf")},
        )
    assert res2.status_code == 201
    assert res2.json()["status"] == "ALREADY_IMPORTED"


def test_historical_project_search_and_filtering(client: TestClient):
    # Import catalog
    with open(SYNTHETIC_CATALOG_PATH, "rb") as f:
        client.post(
            "/api/v1/historical-projects/import",
            files={"file": ("synthetic_historical_catalog.pdf", f, "application/pdf")},
        )

    # Search keyword
    search_res = client.get("/api/v1/projects?search=Methane")
    assert search_res.status_code == 200
    projects = search_res.json()
    assert len(projects) >= 1
    assert "Methane" in projects[0]["title"]

    # Filter by source_type=OFFICIAL
    official_res = client.get("/api/v1/projects?source_type=OFFICIAL")
    assert official_res.status_code == 200
    assert all(p["source_type"] == "OFFICIAL" for p in official_res.json())

    # Filter by verification_status=NEEDS_REVIEW
    review_res = client.get("/api/v1/projects?verification_status=NEEDS_REVIEW")
    assert review_res.status_code == 200
    assert len(review_res.json()) >= 1


def test_manual_verification_workflow(client: TestClient):
    with open(SYNTHETIC_CATALOG_PATH, "rb") as f:
        client.post(
            "/api/v1/historical-projects/import",
            files={"file": ("synthetic_historical_catalog.pdf", f, "application/pdf")},
        )

    projects_res = client.get("/api/v1/projects?source_type=OFFICIAL")
    proj_id = projects_res.json()[0]["id"]

    # Mark as VERIFIED
    patch_res = client.patch(
        f"/api/v1/projects/{proj_id}/verification",
        json={"verification_status": "VERIFIED"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["verification_status"] == "VERIFIED"
    assert patch_res.json()["verification_timestamp"] is not None

    # Retrieve source provenance endpoint
    source_res = client.get(f"/api/v1/projects/{proj_id}/source")
    assert source_res.status_code == 200
    source_data = source_res.json()
    assert source_data["verification_status"] == "VERIFIED"
    assert "source_page_start" in source_data
    assert source_data["raw_record_text"] is not None
