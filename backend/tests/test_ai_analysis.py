from pathlib import Path

from fastapi.testclient import TestClient

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
PROPOSAL_COMPLETE_PATH = FIXTURES_DIR / "synthetic_proposal_complete.pdf"


def test_ai_analysis_end_to_end_and_caching(client: TestClient):
    # 1. Upload Proposal
    with open(PROPOSAL_COMPLETE_PATH, "rb") as f:
        p_res = client.post(
            "/api/v1/proposals/upload",
            files={"file": ("synthetic_proposal_complete.pdf", f, "application/pdf")},
        )
    assert p_res.status_code == 201
    prop_id = p_res.json()["id"]

    # 2. Create Evaluation
    eval_res = client.post("/api/v1/evaluations", json={"proposal_id": prop_id, "reviewer_id": "Dr. AI Reviewer"})
    assert eval_res.status_code == 201
    eval_id = eval_res.json()["id"]

    # 3. Generate AI Analysis Snapshot
    ai_res1 = client.post(f"/api/v1/evaluations/{eval_id}/ai-analysis")
    assert ai_res1.status_code == 200
    data1 = ai_res1.json()
    snapshot_id1 = data1["id"]
    assert data1["provider"] == "deterministic-grounded-v2"
    assert data1["prompt_version"] == "evidence-analysis-v2"
    assert len(data1["input_hash"]) == 64

    res_body = data1["analysis_result"]
    assert "overall_observation" in res_body
    assert len(res_body["criterion_analysis"]) >= 5
    assert len(res_body["reviewer_questions"]) >= 1
    assert "disclaimer" in res_body

    # Safety checks: Verify score separation & absence of autonomous decision strings
    assert "AUTONOMOUS_APPROVAL" not in res_body["overall_observation"]

    # 4. Input Hash Caching: Re-request should return identical snapshot
    ai_res2 = client.post(f"/api/v1/evaluations/{eval_id}/ai-analysis")
    assert ai_res2.status_code == 200
    assert ai_res2.json()["id"] == snapshot_id1

    # 5. Explicit Refresh: Force regeneration
    ref_res = client.post(f"/api/v1/evaluations/{eval_id}/ai-analysis/refresh")
    assert ref_res.status_code == 200
    snapshot_id2 = ref_res.json()["id"]
    assert snapshot_id2 != snapshot_id1
