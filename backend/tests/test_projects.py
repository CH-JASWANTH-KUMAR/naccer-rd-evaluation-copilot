from fastapi.testclient import TestClient


def test_historical_project_crud(client: TestClient):
    payload = {
        "project_code": "HIST-TEST-001",
        "title": "Microbial Desulfurization Project",
        "institution": "CSIR CIMFR",
        "domain": "Clean Coal Technology",
        "approved_cost": 3500000.0,
        "status": "COMPLETED",
    }
    create_res = client.post("/api/v1/projects", json=payload)
    assert create_res.status_code == 201
    proj_data = create_res.json()
    assert proj_data["project_code"] == "HIST-TEST-001"
    proj_id = proj_data["id"]

    get_res = client.get(f"/api/v1/projects/{proj_id}")
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Microbial Desulfurization Project"

    list_res = client.get("/api/v1/projects")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1


def test_seed_endpoint(client: TestClient):
    seed_res = client.post("/api/v1/seed")
    assert seed_res.status_code == 200
    assert "message" in seed_res.json()

    proposals_res = client.get("/api/v1/proposals")
    assert proposals_res.status_code == 200
    assert len(proposals_res.json()) >= 3
