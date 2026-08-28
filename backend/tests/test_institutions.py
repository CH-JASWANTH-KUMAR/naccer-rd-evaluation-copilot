from fastapi.testclient import TestClient


def test_create_and_get_institution(client: TestClient):
    payload = {"name": "IIT Dhanbad", "code": "IIT-ISM-TEST", "type": "ACADEMIC", "location": "Dhanbad, Jharkhand"}
    response = client.post("/api/v1/institutions", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "IIT Dhanbad"
    assert data["code"] == "IIT-ISM-TEST"
    assert "id" in data

    inst_id = data["id"]
    get_res = client.get(f"/api/v1/institutions/{inst_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == inst_id


def test_create_duplicate_institution_code(client: TestClient):
    payload = {"name": "CSIR CIMFR", "code": "CSIR-CIMFR-TEST", "type": "RESEARCH_INSTITUTE", "location": "Dhanbad"}
    res1 = client.post("/api/v1/institutions", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/v1/institutions", json=payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]


def test_get_nonexistent_institution(client: TestClient):
    res = client.get("/api/v1/institutions/non-existent-id")
    assert res.status_code == 404
