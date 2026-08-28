from pathlib import Path

from fastapi.testclient import TestClient

from app.services.reviewer_intelligence import DecisionPackSafetyValidator

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
PROPOSAL_COMPLETE_PATH = FIXTURES_DIR / "synthetic_proposal_complete.pdf"


def test_reviewer_intelligence_and_decision_pack_workflow(client: TestClient):
    # 1. Upload Synthetic Proposal PDF
    with open(PROPOSAL_COMPLETE_PATH, "rb") as f:
        p_res = client.post(
            "/api/v1/proposals/upload",
            files={"file": ("synthetic_proposal_complete.pdf", f, "application/pdf")},
        )
    assert p_res.status_code == 201
    prop_id = p_res.json()["id"]

    # 2. Create Evaluation Workspace
    eval_res = client.post("/api/v1/evaluations", json={"proposal_id": prop_id, "reviewer_id": "Dr. Lead Reviewer"})
    assert eval_res.status_code == 201
    eval_id = eval_res.json()["id"]

    # 3. GET /api/v1/evaluations/{id}/review-context
    ctx_res = client.get(f"/api/v1/evaluations/{eval_id}/review-context")
    assert ctx_res.status_code == 200
    ctx_data = ctx_res.json()

    assert "evaluation" in ctx_data
    assert "proposal" in ctx_data
    assert "scrutiny" in ctx_data
    assert "scorecard" in ctx_data
    assert "attention_items" in ctx_data
    assert "evidence_coverage_matrix" in ctx_data
    assert "audit_events" in ctx_data

    # 4. POST /api/v1/evaluations/{id}/decision-pack
    pack_res = client.post(f"/api/v1/evaluations/{eval_id}/decision-pack")
    assert pack_res.status_code == 200
    pack_data = pack_res.json()

    assert pack_data["evaluation_id"] == eval_id
    assert pack_data["version"] == 1
    assert len(pack_data["input_hash"]) == 64
    assert pack_data["status"] == "FINALIZED"
    assert "disclaimer" in pack_data["content"]

    # 5. GET /api/v1/evaluations/{id}/decision-pack.pdf (HTML/PDF dossier export)
    pdf_res = client.get(f"/api/v1/evaluations/{eval_id}/decision-pack.pdf")
    assert pdf_res.status_code == 200
    assert "text/html" in pdf_res.headers["content-type"]
    assert "NaCCER R&D Evaluation Copilot — Technical Dossier" in pdf_res.text


def test_decision_pack_safety_validator_rejection():
    import pytest
    disallowed_content = {"summary": "AUTONOMOUS_APPROVAL granted."}
    with pytest.raises(ValueError, match="AUTONOMOUS_APPROVAL"):
        DecisionPackSafetyValidator.validate_decision_pack(disallowed_content)
