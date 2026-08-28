import pytest
from fastapi.testclient import TestClient

from app.services.reviewer_operations import ProposalStateMachine


def test_proposal_state_machine_validation():
    # Valid transitions
    ProposalStateMachine.validate_transition("UPLOADED", "PROCESSING")
    ProposalStateMachine.validate_transition("PROCESSING", "READY_FOR_REVIEW")
    ProposalStateMachine.validate_transition("READY_FOR_REVIEW", "ASSIGNED")
    ProposalStateMachine.validate_transition("ASSIGNED", "UNDER_REVIEW")
    ProposalStateMachine.validate_transition("UNDER_REVIEW", "SUBMITTED")
    ProposalStateMachine.validate_transition("SUBMITTED", "RETURNED_FOR_REVISION")

    # Invalid transitions
    from fastapi import HTTPException
    with pytest.raises(HTTPException):
        ProposalStateMachine.validate_transition("UPLOADED", "SUBMITTED")
    with pytest.raises(HTTPException):
        ProposalStateMachine.validate_transition("ARCHIVED", "UNDER_REVIEW")


def test_reviewer_operations_and_queue(client: TestClient):
    # 1. Create Proposal
    inst_res = client.post(
        "/api/v1/institutions",
        json={"name": "ISM Dhanbad Ops", "code": "ISM-OPS", "type": "ACADEMIC", "location": "Dhanbad"},
    )
    inst_id = inst_res.json()["id"]

    p_res = client.post(
        "/api/v1/proposals",
        json={
            "title": "Mine Safety Operations Platform",
            "problem_statement": "Operations problem statement.",
            "objectives": "Operations objectives.",
            "methodology": "Operations methodology.",
            "institution_id": inst_id,
            "principal_investigator": "Dr. Operational Lead",
            "domain": "Safety",
            "budget_total": 450000.0,
        },
    )
    prop_id = p_res.json()["id"]

    # 2. Create Evaluation
    eval_res = client.post("/api/v1/evaluations", json={"proposal_id": prop_id, "reviewer_id": "Dr. Unassigned"})
    eval_id = eval_res.json()["id"]

    # 3. Admin assigns evaluation to Dr. Queue Reviewer
    assign_res = client.post(
        f"/api/v1/evaluations/{eval_id}/assign",
        json={"reviewer_id": "Dr. Queue Reviewer", "assigned_by": "System Admin"},
    )
    assert assign_res.status_code == 200
    assert assign_res.json()["status"] == "ASSIGNED"

    # 4. GET /api/v1/reviewer/queue
    q_res = client.get("/api/v1/reviewer/queue?reviewer_id=Dr.+Queue+Reviewer")
    assert q_res.status_code == 200
    q_data = q_res.json()
    assert len(q_data) >= 1
    assert q_data[0]["evaluation_id"] == eval_id

    # 5. Transition to UNDER_REVIEW by submitting draft updates
    client.patch(
        f"/api/v1/evaluations/{eval_id}",
        json={
            "status": "UNDER_REVIEW",
            "criteria": [
                {"criterion_key": "TECHNICAL_SOUNDNESS", "score": 8.0, "comments": "Good approach", "justification_notes": "Valid"}
            ],
        },
    )

    # 6. Return for Revision requiring human-entered reason
    # Short reason should fail
    fail_ret = client.post(f"/api/v1/evaluations/{eval_id}/return", json={"returned_by": "Committee Chair", "reason": "No"})
    assert fail_ret.status_code == 400

    # Valid return reason succeeds
    ret_res = client.post(
        f"/api/v1/evaluations/{eval_id}/return",
        json={"returned_by": "Committee Chair", "reason": "Independent testing dataset required in methodology section."},
    )
    assert ret_res.status_code == 200
    assert ret_res.json()["status"] == "RETURNED_FOR_REVISION"


def test_system_readiness_and_csv_export(client: TestClient):
    # 1. GET /api/v1/health/readiness
    r_res = client.get("/api/v1/health/readiness")
    assert r_res.status_code == 200
    r_data = r_res.json()
    assert r_data["status"] == "healthy"
    assert r_data["readiness"] == "READY"
    assert "subsystems" in r_data

    # 2. GET /api/v1/reports/export.csv
    csv_res = client.get("/api/v1/reports/export.csv")
    assert csv_res.status_code == 200
    assert "text/csv" in csv_res.headers["content-type"]
    assert "Evaluation ID,Proposal Reference,Proposal Title" in csv_res.text
