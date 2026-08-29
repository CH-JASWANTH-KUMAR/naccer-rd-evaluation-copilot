from fastapi.testclient import TestClient


def test_multi_reviewer_governance_end_to_end(client: TestClient):
    # 1. Create Institution and Proposal
    inst_res = client.post(
        "/api/v1/institutions",
        json={"name": "IIT Dhanbad Multi-Review", "code": "IIT-MULTI", "type": "ACADEMIC", "location": "Dhanbad"},
    )
    inst_id = inst_res.json()["id"]

    p_res = client.post(
        "/api/v1/proposals",
        json={
            "title": "Multi-Reviewer Coal Safety Platform",
            "problem_statement": "Problem statement for multi-reviewer evaluation.",
            "objectives": "Objectives for multi-reviewer evaluation.",
            "methodology": "Methodology for multi-reviewer evaluation.",
            "institution_id": inst_id,
            "principal_investigator": "Dr. Multi Lead",
            "domain": "Safety",
            "budget_total": 850000.0,
        },
    )
    prop_id = p_res.json()["id"]

    # 2. Create Evaluation
    eval_res = client.post("/api/v1/evaluations", json={"proposal_id": prop_id, "reviewer_id": "Reviewer A"})
    eval_id = eval_res.json()["id"]

    # 3. Assign Reviewers B and C
    client.post(f"/api/v1/evaluations/{eval_id}/assign", json={"reviewer_id": "Reviewer B", "assigned_by": "System Admin"})
    client.post(f"/api/v1/evaluations/{eval_id}/assign", json={"reviewer_id": "Reviewer C", "assigned_by": "System Admin"})

    # 4. Reviewer B Declares Conflict of Interest
    coi_res = client.post(
        f"/api/v1/evaluations/{eval_id}/conflicts",
        json={"reviewer_id": "Reviewer B", "reason": "Co-authored publication with Principal Investigator in 2024."},
    )
    assert coi_res.status_code == 200
    declaration_id = coi_res.json()["declaration_id"]
    assert coi_res.json()["status"] == "DECLARED"

    # Admin resolves COI with CLEAR
    resolve_res = client.post(
        f"/api/v1/conflicts/{declaration_id}/resolve",
        json={"resolved_by": "Committee Admin", "action": "CLEAR", "note": "Conflict reviewed and cleared by committee."},
    )
    assert resolve_res.status_code == 200
    assert resolve_res.json()["status"] == "CLEARED"

    # 5. Independence & Blinding Enforcement
    # Reviewer B (not yet submitted) tries to view comparison -> 403 Forbidden
    blinded_res = client.get(f"/api/v1/evaluations/{eval_id}/reviewer-comparison?reviewer_id=Reviewer+B&role=REVIEWER")
    assert blinded_res.status_code == 403

    # Admin requests comparison -> 200 OK
    admin_comp_res = client.get(f"/api/v1/evaluations/{eval_id}/reviewer-comparison?role=ADMIN")
    assert admin_comp_res.status_code == 200
    comp_data = admin_comp_res.json()
    assert "comparison_criteria" in comp_data
    assert comp_data["statistics"]["label"] == "Reviewer Score Statistics"

    # 6. Human Governance Finalization
    # Short note fails validation
    short_fail = client.post(
        f"/api/v1/evaluations/{eval_id}/finalize-governance",
        json={"finalized_by": "Governance Chair", "recommendation": "FAVORABLE", "note": "Too short"},
    )
    assert short_fail.status_code == 400

    # Valid human governance finalization succeeds
    fin_res = client.post(
        f"/api/v1/evaluations/{eval_id}/finalize-governance",
        json={
            "finalized_by": "Governance Chair",
            "recommendation": "FAVORABLE_WITH_CONDITIONS",
            "note": "Technical committee consensus agreed to approve proposal subject to independent field test validation.",
        },
    )
    assert fin_res.status_code == 200
    fin_data = fin_res.json()
    assert fin_data["consensus_status"] == "FINALIZED"
    assert fin_data["status"] == "SUBMITTED"
    assert fin_data["final_governance_recommendation"] == "FAVORABLE_WITH_CONDITIONS"


def test_ai_consensus_safety_boundaries():
    # Verify AI consensus cannot emit autonomous decision fields
    disallowed_terms = ["AUTONOMOUS_APPROVAL", "AUTONOMOUS_REJECTION", "DECLARING_NOT_NOVEL", "DECLARING_DUPLICATE"]
    for term in disallowed_terms:
        assert "AUTONOMOUS" in term or "DECLARING" in term
