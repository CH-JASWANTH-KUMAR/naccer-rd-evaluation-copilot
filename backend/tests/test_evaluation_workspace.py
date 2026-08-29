from pathlib import Path

from fastapi.testclient import TestClient

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
PROPOSAL_COMPLETE_PATH = FIXTURES_DIR / "synthetic_proposal_complete.pdf"


def test_active_rubric_seeding(client: TestClient):
    res = client.get("/api/v1/rubrics/active")
    assert res.status_code == 200
    data = res.json()
    assert data["version"] == "v1.0"
    assert len(data["criteria"]) == 8
    assert any(c["key"] == "THRUST_AREA_ALIGNMENT" for c in data["criteria"])


def test_evaluation_workflow_end_to_end(client: TestClient):
    # 1. Intake Synthetic Proposal A
    with open(PROPOSAL_COMPLETE_PATH, "rb") as f:
        p_res = client.post(
            "/api/v1/proposals/upload",
            files={"file": ("synthetic_proposal_complete.pdf", f, "application/pdf")},
        )
    assert p_res.status_code == 201
    prop_id = p_res.json()["id"]

    # 2. Create Evaluation Workspace
    eval_res = client.post("/api/v1/evaluations", json={"proposal_id": prop_id, "reviewer_id": "Dr. S. K. Singh"})
    assert eval_res.status_code == 201
    eval_data = eval_res.json()
    eval_id = eval_data["id"]
    assert eval_data["status"] == "DRAFT"
    assert len(eval_data["criteria"]) == 8
    assert len(eval_data["evidences"]) >= 2

    # 3. Update Evaluation Draft Scores & Comments
    criteria_updates = []
    for c in eval_data["criteria"]:
        if c["criterion_key"] == "NOVELTY":
            criteria_updates.append(
                {
                    "id": c["id"],
                    "score": 4.5,
                    "comments": "Historical overlap detected with methane sensor benchmark projects.",
                    "justification_notes": "Overlap exists in sensor node mesh placement, but edge ML methodology provides distinct value.",
                }
            )
        else:
            criteria_updates.append(
                {
                    "id": c["id"],
                    "score": 8.5,
                    "comments": "Methodology and objectives are technically sound.",
                }
            )

    update_res = client.patch(
        f"/api/v1/evaluations/{eval_id}",
        json={
            "reviewer_summary": "Strong proposal with manageable historical overlap.",
            "reviewer_recommendation": "FAVORABLE_WITH_CONDITIONS",
            "criteria": criteria_updates,
        },
    )
    assert update_res.status_code == 200
    updated_data = update_res.json()
    assert updated_data["overall_score"] is not None
    assert updated_data["overall_score"] > 7.0

    # 4. Add Reviewer Evidence Item
    ev_res = client.post(
        f"/api/v1/evaluations/{eval_id}/evidence",
        json={
            "evidence_type": "REVIEWER_NOTE",
            "source_type": "REVIEWER",
            "evidence_text": "Reviewer verified sensor network layout against CIL mine safety standard CMPDI-2025.",
        },
    )
    assert ev_res.status_code == 201

    # 5. Generate Draft Evaluation Summary
    sum_res = client.post(f"/api/v1/evaluations/{eval_id}/summary")
    assert sum_res.status_code == 200
    assert "EVALUATION SUMMARY DRAFT" in sum_res.json()["draft_summary"]

    # 6. Submit Evaluation
    submit_res = client.post(f"/api/v1/evaluations/{eval_id}/submit")
    assert submit_res.status_code == 200
    assert submit_res.json()["status"] == "SUBMITTED"


def test_submit_evaluation_validation_checks(client: TestClient):
    # Create institution
    inst_res = client.post(
        "/api/v1/institutions",
        json={"name": "IIT Dhanbad", "code": "IIT-ISM-TEST", "type": "ACADEMIC", "location": "Dhanbad"},
    )
    inst_id = inst_res.json()["id"]

    # Create proposal and evaluation
    p_res = client.post(
        "/api/v1/proposals",
        json={
            "title": "Unscored Proposal Test",
            "institution_id": inst_id,
            "principal_investigator": "Dr. Test",
            "domain": "Safety",
            "budget_total": 100000.0,
        },
    )
    prop_id = p_res.json()["id"]

    eval_res = client.post("/api/v1/evaluations", json={"proposal_id": prop_id, "reviewer_id": "Rev-02"})
    eval_id = eval_res.json()["id"]

    # Submit without scoring criteria -> Expect 422
    submit_fail = client.post(f"/api/v1/evaluations/{eval_id}/submit")
    assert submit_fail.status_code == 422
    assert "missing scores" in submit_fail.json()["detail"]
