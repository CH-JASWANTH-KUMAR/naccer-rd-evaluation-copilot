from fastapi.testclient import TestClient


def test_proposal_crud_and_validation(client: TestClient):
    # 1. Create institution
    inst_res = client.post(
        "/api/v1/institutions",
        json={"name": "NIT Rourkela", "code": "NIT-RKL-TEST", "type": "ACADEMIC", "location": "Rourkela"},
    )
    assert inst_res.status_code == 201
    inst_id = inst_res.json()["id"]

    # 2. Create proposal
    prop_payload = {
        "title": "Methane Leakage Detection System",
        "institution_id": inst_id,
        "principal_investigator": "Dr. R. K. Verma",
        "domain": "Mine Safety & Ventilation",
        "budget_total": 4500000.0,
        "status": "UNDER_REVIEW",
        "priority": "HIGH",
    }
    create_res = client.post("/api/v1/proposals", json=prop_payload)
    assert create_res.status_code == 201
    prop_data = create_res.json()
    assert prop_data["title"] == "Methane Leakage Detection System"
    assert prop_data["institution"]["code"] == "NIT-RKL-TEST"
    prop_id = prop_data["id"]

    # 3. Get proposal by ID
    get_res = client.get(f"/api/v1/proposals/{prop_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == prop_id

    # 4. List proposals
    list_res = client.get("/api/v1/proposals")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # 5. Patch proposal
    patch_res = client.patch(f"/api/v1/proposals/{prop_id}", json={"status": "COMPLETED"})
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "COMPLETED"

    # 6. Delete proposal
    del_res = client.delete(f"/api/v1/proposals/{prop_id}")
    assert del_res.status_code == 204

    # 7. Verify 404
    get_after_del = client.get(f"/api/v1/proposals/{prop_id}")
    assert get_after_del.status_code == 404


def test_create_proposal_invalid_institution(client: TestClient):
    payload = {
        "title": "Invalid Institution Test Proposal",
        "institution_id": "non-existent-inst-id",
        "principal_investigator": "Dr. Test",
        "domain": "Mine Safety",
        "budget_total": 100000.0,
    }
    res = client.post("/api/v1/proposals", json=payload)
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_create_proposal_negative_budget(client: TestClient):
    # First create institution
    inst_res = client.post(
        "/api/v1/institutions",
        json={"name": "IIT Kharagpur", "code": "IIT-KGP-TEST", "type": "ACADEMIC", "location": "Kharagpur"},
    )
    inst_id = inst_res.json()["id"]

    payload = {
        "title": "Negative Budget Proposal",
        "institution_id": inst_id,
        "principal_investigator": "Dr. Test",
        "domain": "Mine Safety",
        "budget_total": -500.0,
    }
    res = client.post("/api/v1/proposals", json=payload)
    assert res.status_code == 422
