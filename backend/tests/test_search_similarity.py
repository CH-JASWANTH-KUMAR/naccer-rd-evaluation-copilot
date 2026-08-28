from pathlib import Path

from fastapi.testclient import TestClient

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
SYNTHETIC_CATALOG_PATH = FIXTURES_DIR / "synthetic_historical_catalog.pdf"


def test_similarity_search_with_evidence_and_provenance(client: TestClient):
    # 1. Import synthetic catalogue
    with open(SYNTHETIC_CATALOG_PATH, "rb") as f:
        client.post(
            "/api/v1/historical-projects/import",
            files={"file": ("synthetic_historical_catalog.pdf", f, "application/pdf")},
        )

    # 2. Perform similarity search query
    query_payload = {
        "title": "Real-Time Methane Monitoring Using IoT Mesh Nodes",
        "objectives": "Deploy wireless gas detection sensor network in underground coal mines for CH4 safety monitoring.",
        "technology": "IoT Sensors, Gas Detection Mesh",
        "domain": "Mining & Safety R&D",
        "top_k": 5,
    }

    res = client.post("/api/v1/projects/search/similar", json=query_payload)
    assert res.status_code == 200

    data = res.json()
    assert "disclaimer" in data
    assert "Similarity results are evidence for reviewer assessment" in data["disclaimer"]
    assert data["results_count"] >= 1

    top_item = data["results"][0]
    assert top_item["similarity_score"] > 0.0
    assert top_item["relationship"] in ["POTENTIALLY_RELATED", "CONCEPTUAL_OVERLAP", "WEAK_RELATIONSHIP"]
    assert len(top_item["evidence"]) >= 1
    assert "provenance" in top_item
    assert "source_type" in top_item["provenance"]
    assert top_item["provenance"]["verification_status"] is not None


def test_similarity_search_empty_query(client: TestClient):
    res = client.post("/api/v1/projects/search/similar", json={})
    assert res.status_code == 200
    data = res.json()
    assert data["results_count"] == 0
    assert "disclaimer" in data


def test_index_project_embeddings_endpoint(client: TestClient):
    res = client.post("/api/v1/projects/embeddings/index")
    assert res.status_code == 200
    data = res.json()
    assert "indexed embeddings" in data["message"]
