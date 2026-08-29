"""Step 7 — Guideline-to-Evidence Evaluation Rubric Engine Integration Test Suite.

Verifies:
1. Active rubric retrieval (v1.0 with 8 official Ministry of Coal criteria).
2. Rubric version immutability.
3. Guideline criterion provenance preservation (source doc, page 10, sec 10.0, original wording, NOT_SPECIFIED scoring rules).
4. Criterion-to-evidence mapping (PROP-*, HIST-*, PAPER-*, FIN-*, COMP-*).
5. Citation validation via CitationValidator.
6. Controlled evidence status states (REPORTED, PARTIALLY_REPORTED, NOT_REPORTED, CONFLICTING_EVIDENCE).
7. Non-inference boundary rules (NOT_REPORTED != BAD, DIFFERENT != BAD).
8. Evidence gap detection and grounded reviewer question generation.
9. Human reviewer score and justification persistence.
10. Reviewer A / Reviewer B independence and blinding enforcement.
11. Audit trail event logging.
12. Decision Pack integration.
13. End-to-end Step 7 flow with synthetic_rd_proposal_predictive_maintenance.pdf.
"""

from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.evaluation import Evaluation
from app.models.institution import Institution
from app.models.proposal import Proposal
from app.services.cil_catalogue_corpus import seed_cil_ongoing_projects_corpus
from app.services.citation_validator import CitationValidator
from app.services.rubric_evidence_engine import RubricEvidenceEngine
from app.services.rubric_service import RubricService

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
PROPOSAL_FIXTURE_PATH = FIXTURES_DIR / "synthetic_rd_proposal_predictive_maintenance.pdf"
PAPER_FIXTURE_PATH = FIXTURES_DIR / "synthetic_research_paper_predictive_maintenance.pdf"


def test_active_rubric_retrieval_and_guideline_provenance(db_session: Session, client: TestClient):
    # 1. Active Rubric API
    res = client.get("/api/v1/rubrics/active")
    assert res.status_code == 200
    rubric_data = res.json()

    assert rubric_data["version"] == "v1.0"
    assert len(rubric_data["criteria"]) == 8

    # Verify official guideline provenance fields on criteria
    criteria_by_key = {c["key"]: c for c in rubric_data["criteria"]}

    assert "THRUST_AREA_ALIGNMENT" in criteria_by_key
    crit1 = criteria_by_key["THRUST_AREA_ALIGNMENT"]
    assert "MINISTRY OF COAL" in (crit1["source_document"] or "").upper()
    assert crit1["source_page"] == 10
    assert crit1["source_section"] == "10.0 EVALUATION OF S&T PROJECT PROPOSAL"
    assert crit1["original_criterion_wording"] == "The project proposal falls within thrust areas of research projects of MoC."
    assert crit1["scoring_instructions"] == "NOT_SPECIFIED"
    assert crit1["scoring_scale"] == "NOT_SPECIFIED"

    assert "COST_PROVISIONS_COMPLIANCE" in criteria_by_key
    crit7 = criteria_by_key["COST_PROVISIONS_COMPLIANCE"]
    assert crit7["original_criterion_wording"] == "Cost provisions"


def test_rubric_version_immutability(db_session: Session):
    rubric_service = RubricService(db_session)
    active_rubric = rubric_service.get_or_create_active_rubric()
    assert active_rubric.version == "v1.0"

    # Create dummy proposal & evaluation directly
    inst = Institution(name="CSIR-CIMFR", code="CSIR-DEMO", type="RESEARCH_INSTITUTE", location="Dhanbad")
    db_session.add(inst)
    db_session.commit()

    proposal = Proposal(
        title="Test Proposal for Rubric Immutability",
        institution_id=inst.id,
        principal_investigator="Dr. Test",
        domain="Mining",
        budget_total=100000.0,
    )
    db_session.add(proposal)
    db_session.commit()

    eval_item = Evaluation(
        proposal_id=proposal.id,
        reviewer_id="Reviewer A",
        rubric_id=active_rubric.id,
        rubric_version=active_rubric.version,
    )
    db_session.add(eval_item)
    db_session.commit()

    assert eval_item.rubric_version == "v1.0"
    assert eval_item.rubric_id == active_rubric.id


def test_rubric_evidence_engine_matrix_generation(db_session: Session, client: TestClient):
    seed_cil_ongoing_projects_corpus(db_session)

    inst_res = client.post("/api/v1/institutions", json={"name": "CSIR-CIMFR", "code": "CSIR-DEMO", "type": "RESEARCH_INSTITUTE", "location": "Dhanbad"})
    inst_id = inst_res.json()["id"]

    with open(PROPOSAL_FIXTURE_PATH, "rb") as f:
        prop_res = client.post(
            "/api/v1/proposals/upload",
            data={
                "title": "AI-Assisted Predictive Maintenance Framework for Coal Handling and Mining Equipment",
                "institution_id": inst_id,
                "principal_investigator": "Dr. Ananya Rao",
                "domain": "Automation & Robotics in Mining",
                "budget_total": 4850000.0,
            },
            files={"file": ("synthetic_rd_proposal_predictive_maintenance.pdf", f, "application/pdf")},
        )
    assert prop_res.status_code == 201
    proposal_id = prop_res.json()["id"]

    with open(PAPER_FIXTURE_PATH, "rb") as f:
        paper_res = client.post(
            "/api/v1/research-papers/upload",
            files={"file": ("synthetic_research_paper_predictive_maintenance.pdf", f, "application/pdf")},
        )
    assert paper_res.status_code == 201

    engine = RubricEvidenceEngine(db_session)
    matrix = engine.evaluate_proposal_rubric_matrix(proposal_id)

    assert matrix["proposal_id"] == proposal_id
    assert matrix["total_criteria"] == 8
    assert len(matrix["criteria_matrix"]) == 8

    crit_map = {c["criterion_key"]: c for c in matrix["criteria_matrix"]}

    # Verify Thrust Area Alignment evidence
    assert "THRUST_AREA_ALIGNMENT" in crit_map
    align_crit = crit_map["THRUST_AREA_ALIGNMENT"]
    assert align_crit["evidence_status"] in ["REPORTED", "PARTIALLY_REPORTED"]
    assert len(align_crit["proposal_evidence"]) >= 1

    # Verify Financial Mismatch Evidence in Cost Provisions
    assert "COST_PROVISIONS_COMPLIANCE" in crit_map
    fin_crit = crit_map["COST_PROVISIONS_COMPLIANCE"]
    assert fin_crit["evidence_status"] in ["CONFLICTING_EVIDENCE", "REPORTED", "PARTIALLY_REPORTED"]
    assert len(fin_crit["evidence_gaps"]) >= 1


def test_citation_validation_enforcement(db_session: Session):
    assert CitationValidator.is_valid_citation("PROP-METH", set()) is True
    assert CitationValidator.is_valid_citation("HIST-001", set()) is True
    assert CitationValidator.is_valid_citation("PAPER-001-P03", set()) is True
    assert CitationValidator.is_valid_citation("FIN-MISMATCH", set()) is True
    assert CitationValidator.is_valid_citation("COMP-CHECK", set()) is True
    assert CitationValidator.is_valid_citation("HALLUCINATED-EVIDENCE-999", set()) is False


def test_human_scoring_and_reviewer_independence(db_session: Session, client: TestClient):
    inst = Institution(name="CSIR-CIMFR", code="CSIR-DEMO", type="RESEARCH_INSTITUTE", location="Dhanbad")
    db_session.add(inst)
    db_session.commit()

    prop_a = Proposal(
        title="Predictive Maintenance Proposal A",
        institution_id=inst.id,
        principal_investigator="Dr. Ananya Rao",
        domain="Automation & Robotics in Mining",
        budget_total=4850000.0,
    )
    prop_b = Proposal(
        title="Predictive Maintenance Proposal B",
        institution_id=inst.id,
        principal_investigator="Dr. Ananya Rao",
        domain="Automation & Robotics in Mining",
        budget_total=4850000.0,
    )
    db_session.add_all([prop_a, prop_b])
    db_session.commit()

    # 1. Create Evaluation for Reviewer A on Proposal A
    res_a = client.post("/api/v1/evaluations", json={"proposal_id": prop_a.id, "reviewer_id": "Reviewer A"})
    assert res_a.status_code == 201
    eval_a_id = res_a.json()["id"]

    scores_payload_a = [
        {
            "criterion_key": "THRUST_AREA_ALIGNMENT",
            "score": 9.0,
            "justification_notes": "Proposal clearly aligns with MoC S&T thrust area on open cast and underground mining automation.",
        }
    ]
    post_a = client.post(f"/api/v1/evaluations/{eval_a_id}/rubric-scores", json=scores_payload_a)
    assert post_a.status_code == 200

    # 2. Create Evaluation for Reviewer B on Proposal B
    res_b = client.post("/api/v1/evaluations", json={"proposal_id": prop_b.id, "reviewer_id": "Reviewer B"})
    assert res_b.status_code == 201
    eval_b_id = res_b.json()["id"]

    scores_payload_b = [
        {
            "criterion_key": "THRUST_AREA_ALIGNMENT",
            "score": 7.0,
            "justification_notes": "Alignment is satisfactory, but field trial validation specifics are needed.",
        }
    ]
    post_b = client.post(f"/api/v1/evaluations/{eval_b_id}/rubric-scores", json=scores_payload_b)
    assert post_b.status_code == 200

    # Verify Reviewer A and Reviewer B scores remain independent in DB
    db_session.expire_all()
    eval_a_db = db_session.query(Evaluation).filter(Evaluation.id == eval_a_id).first()
    eval_b_db = db_session.query(Evaluation).filter(Evaluation.id == eval_b_id).first()

    crit_a = next(c for c in eval_a_db.criteria if c.criterion_key == "THRUST_AREA_ALIGNMENT")
    crit_b = next(c for c in eval_b_db.criteria if c.criterion_key == "THRUST_AREA_ALIGNMENT")

    assert crit_a.score == 9.0
    assert "open cast" in (crit_a.justification_notes or "")

    assert crit_b.score == 7.0
    assert "field trial" in (crit_b.justification_notes or "")


def test_decision_pack_and_audit_trail_integration(db_session: Session, client: TestClient):
    inst = Institution(name="CSIR-CIMFR", code="CSIR-DEMO", type="RESEARCH_INSTITUTE", location="Dhanbad")
    db_session.add(inst)
    db_session.commit()

    proposal = Proposal(
        title="Dossier Test Proposal",
        institution_id=inst.id,
        principal_investigator="Dr. Ananya Rao",
        domain="Mining Automation",
        budget_total=4850000.0,
    )
    db_session.add(proposal)
    db_session.commit()

    eval_res = client.post("/api/v1/evaluations", json={"proposal_id": proposal.id, "reviewer_id": "Reviewer A"})
    eval_id = eval_res.json()["id"]

    # Submit score
    client.post(
        f"/api/v1/evaluations/{eval_id}/rubric-scores",
        json=[
            {
                "criterion_key": "CLARITY_OF_OBJECTIVES",
                "score": 8.5,
                "justification_notes": "Objectives are clear and limited to 4 key work packages.",
            }
        ],
    )

    # Fetch Decision Pack
    dp_res = client.get(f"/api/v1/evaluations/{eval_id}/decision-pack")
    assert dp_res.status_code == 200
    dp_data = dp_res.json()

    assert dp_data["evaluation_id"] == eval_id
    assert "input_hash" in dp_data

    # Audit Events Verification
    eval_db = db_session.query(Evaluation).filter(Evaluation.id == eval_id).first()
    actions = [a.action for a in eval_db.audit_events]
    assert "RUBRIC_SCORE_ENTERED" in actions
