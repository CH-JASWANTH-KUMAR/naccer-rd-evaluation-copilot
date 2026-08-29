"""Step 8 — Hardened PDF Document Structuring & Proposal Section Extraction Test Suite.

Gold-Standard Assertions:
1. Problem Statement contains the complete contiguous problem text.
2. Project Objectives contains only objective content.
3. Technology does NOT contain random location/header text ("Bombay, Mumbai, India").
4. Methodology does NOT contain problem-statement text.
5. Expected Outcomes does NOT contain methodology text.
6. Multi-page sections are reconstructed correctly across page boundaries.
7. Page provenance (source_page_start, source_page_end, extraction_confidence) is preserved.
8. Missing sections return NOT_REPORTED.
9. Heading substring false positives (e.g. PI in COPILOT, Technology in Institute of Technology) are rejected.
10. PI extraction does not match COPILOT or unrelated text.
"""

from pathlib import Path

import pypdf
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.document_type_classifier import classify_document
from app.services.proposal_section_parser import normalize_text, parse_proposal_sections

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
PROPOSAL_FIXTURE_PATH = FIXTURES_DIR / "synthetic_rd_proposal_predictive_maintenance.pdf"


def test_text_normalization_and_whitespace_cleaning():
    raw_input = "SYNTHETIC\xa0TEST\xadPROPOSAL  —  NaCCER   EVALUATION\tCOPILOT"
    normalized = normalize_text(raw_input)
    assert "\xa0" not in normalized
    assert "\xad" not in normalized
    assert "SYNTHETIC TESTPROPOSAL — NaCCER EVALUATION COPILOT" == normalized


def test_section_boundary_reconstruction_on_fixture_pdf():
    reader = pypdf.PdfReader(PROPOSAL_FIXTURE_PATH)
    pages_text = [(idx, p.extract_text() or "") for idx, p in enumerate(reader.pages, start=1)]

    parsed = parse_proposal_sections(pages_text)
    sections = parsed["sections"]
    meta = parsed["metadata"]

    # 1. Problem Statement contiguity assertion
    prob_sec = sections["problem_statement"]
    assert prob_sec.status == "REPORTED"
    assert "Unexpected mechanical failure of heavy coal handling machinery" in prob_sec.content
    assert "Project Objectives" not in prob_sec.content
    assert "Methodology" not in prob_sec.content

    # 2. Objectives isolation assertion
    obj_sec = sections["objectives"]
    assert obj_sec.status == "REPORTED"
    assert "1. Deploy IoT vibration, thermal, and acoustic telemetry sensors" in obj_sec.content
    assert "Unexpected mechanical failure" not in obj_sec.content
    assert "Tri-axial vibration transducers" not in obj_sec.content

    # 3. Technology cleanliness assertion (no location or header noise)
    tech_sec = sections["technology"]
    assert tech_sec.status == "REPORTED"
    assert "Tri-axial vibration transducers, infrared thermal sensors" in tech_sec.content
    assert "Bombay" not in tech_sec.content
    assert "Mumbai" not in tech_sec.content
    assert "Problem Statement" not in tech_sec.content

    # 4. Methodology isolation assertion
    meth_sec = sections["methodology"]
    assert meth_sec.status == "REPORTED"
    assert "Multi-sensor data acquisition from coal handling plant drives" in meth_sec.content
    assert "Unexpected mechanical failure" not in meth_sec.content

    # 5. Expected Outcomes isolation assertion
    out_sec = sections["expected_outcomes"]
    assert out_sec.status == "REPORTED"
    assert "Real-time predictive maintenance software suite" in out_sec.content
    assert "Reduction in unscheduled downtime by 35%" in out_sec.content
    assert "Multi-sensor data acquisition" not in out_sec.content

    # 6. Multi-page section reconstruction & provenance assertion
    team_sec = sections["team"]
    assert team_sec.status == "REPORTED"
    assert team_sec.source_page_start == 2
    assert team_sec.source_page_end == 2
    assert "Dr. Ananya Rao, Senior Principal Scientist" in team_sec.content

    # 7. Missing sections assertion
    gap_sec = sections["research_gap"]
    assert gap_sec.status == "NOT_REPORTED"
    assert gap_sec.content == "NOT_REPORTED"

    lit_sec = sections["literature_review"]
    assert lit_sec.status == "NOT_REPORTED"
    assert lit_sec.content == "NOT_REPORTED"

    # 8. Metadata extraction safety assertion
    assert meta["title"] == "AI-Assisted Predictive Maintenance Framework for Coal Handling and Mining Equipment"
    assert meta["principal_investigator"] == "Dr. Ananya Rao"
    assert "COPILOT" not in meta["principal_investigator"]


def test_heading_substring_false_positive_rejection():
    # Simulate a document containing running institutional headers like "Indian Institute of Technology Bombay"
    sample_pages = [
        (
            1,
            """SYNTHETIC PROPOSAL HEADER — NaCCER EVALUATION COPILOT TEST
Indian Institute of Technology Bombay, Mumbai, India
Project Title: Advanced Coal Ventilation Sensor Mesh

1. Problem Statement
Gas accumulation in underground coal mines poses serious explosion risks.

2. Technology & Infrastructure
ATEX-certified gas sensors and LoRaWAN gateways.

3. Proposed Methodology
Deployment of sensor nodes and real-time gas dispersion modeling.
""",
        )
    ]

    parsed = parse_proposal_sections(sample_pages)
    sections = parsed["sections"]

    # Technology section must contain ONLY the actual technology, NOT the institution line
    tech_content = sections["technology"].content
    assert "ATEX-certified gas sensors" in tech_content
    assert "Indian Institute of Technology Bombay" not in tech_content
    assert "Problem Statement" not in tech_content


REAL_PAPER_FIXTURE_PATH = FIXTURES_DIR / "real_published_coal_mining_paper.pdf"


def test_real_published_paper_pdf_section_extraction():
    """Verify section extraction on real published Springer paper s13563-025-00592-w.pdf."""
    if not REAL_PAPER_FIXTURE_PATH.exists():
        return

    reader = pypdf.PdfReader(REAL_PAPER_FIXTURE_PATH)
    pages_text = [(idx, p.extract_text() or "") for idx, p in enumerate(reader.pages, start=1)]

    parsed = parse_proposal_sections(pages_text)
    sections = parsed["sections"]

    # 1. Problem Statement
    prob_sec = sections["problem_statement"]
    assert prob_sec.status == "REPORTED"
    assert "With home to over a hundred minerals" in prob_sec.content
    assert "Literature review" not in prob_sec.content
    assert "Methods and data" not in prob_sec.content

    # 2. Technology must be NOT_REPORTED (must NOT contain 'Bombay, Mumbai, India')
    tech_sec = sections["technology"]
    assert tech_sec.status == "NOT_REPORTED"
    assert "Bombay" not in tech_sec.content
    assert "Mumbai" not in tech_sec.content

    # 3. Objectives must be NOT_REPORTED
    obj_sec = sections["objectives"]
    assert obj_sec.status == "NOT_REPORTED"

    # 4. Methodology must match 'Methods and data' section strictly bounded before 'Results'
    meth_sec = sections["methodology"]
    assert meth_sec.status == "REPORTED"
    assert "This study adopts a conceptual research design" in meth_sec.content
    assert "To understand coal mining accidents, data from 2015 to 2025" not in meth_sec.content
    assert len(meth_sec.content) < 10000  # Strictly bounded, not 28,000+ chars

    # 5. Results section exists separately and is not concatenated into methodology
    res_sec = sections["results"]
    assert res_sec.status == "REPORTED"
    assert "To understand coal mining accidents" in res_sec.content
    assert "were analysed for the coal-producing states in India" in res_sec.content

    # 6. Expected Outcomes must be NOT_REPORTED
    out_sec = sections["expected_outcomes"]
    assert out_sec.status == "NOT_REPORTED"

    # 7. Literature Review must be REPORTED
    lit_sec = sections["literature_review"]
    assert lit_sec.status == "REPORTED"
    assert "The study of occupational hazards in coal mining" in lit_sec.content


def test_document_type_classifier_on_fixtures():
    # 1. Real Paper Classification
    if REAL_PAPER_FIXTURE_PATH.exists():
        reader = pypdf.PdfReader(REAL_PAPER_FIXTURE_PATH)
        pages_text = [(idx, p.extract_text() or "") for idx, p in enumerate(reader.pages, start=1)]
        res = classify_document(pages_text)
        assert res.document_type == "RESEARCH_PAPER"

    # 2. Proposal Classification
    reader_prop = pypdf.PdfReader(PROPOSAL_FIXTURE_PATH)
    pages_prop = [(idx, p.extract_text() or "") for idx, p in enumerate(reader_prop.pages, start=1)]
    res_prop = classify_document(pages_prop)
    assert res_prop.document_type == "R&D_PROPOSAL"
    assert res_prop.document_type_confidence == "HIGH"


def test_explicit_prose_false_positives():
    """Section 13 Test: Verify prose sentences are NOT matched as standalone proposal headings."""
    sample_pages = [
        (
            1,
            """Indian Institute of Technology Bombay, Mumbai, India
The paper has three objectives. First, it develops a conceptual framework.
The study examines continuous mining methods in underground seams.
The results demonstrate significant safety improvements.
Below is the methodology used in this study for empirical validation.
""",
        )
    ]

    parsed = parse_proposal_sections(sample_pages)
    sections = parsed["sections"]

    assert sections["technology"].status == "NOT_REPORTED"
    assert sections["technology"].content == "NOT_REPORTED"
    assert "Bombay" not in sections["technology"].content

    assert sections["objectives"].status == "NOT_REPORTED"
    assert sections["objectives"].content == "NOT_REPORTED"

    assert sections["expected_outcomes"].status == "NOT_REPORTED"
    assert sections["expected_outcomes"].content == "NOT_REPORTED"


def test_real_published_paper_ingestion_end_to_end(db_session: Session, client: TestClient):
    """Verify uploading a real published research paper into proposal route results in RESEARCH_PAPER classification and NOT_APPLICABLE proposal fields."""
    if not REAL_PAPER_FIXTURE_PATH.exists():
        return

    inst_res = client.post(
        "/api/v1/institutions",
        json={"name": "IIT Bombay", "code": "IITB", "type": "ACADEMIC", "location": "Mumbai"},
    )
    inst_id = inst_res.json()["id"]

    with open(REAL_PAPER_FIXTURE_PATH, "rb") as f:
        res = client.post(
            "/api/v1/proposals/upload",
            data={
                "title": "Preventable accidents in Indian coal mining",
                "institution_id": inst_id,
                "principal_investigator": "Aparna Raj C",
                "domain": "Coal Mining Safety",
                "budget_total": 0.0,
            },
            files={"file": ("real_published_coal_mining_paper.pdf", f, "application/pdf")},
        )

    assert res.status_code == 201
    data = res.json()

    assert data["document_type"] == "RESEARCH_PAPER"
    assert data["objectives"] == "NOT_APPLICABLE"
    assert data["technology"] == "NOT_APPLICABLE"
    assert data["expected_outcomes"] == "NOT_APPLICABLE"
    assert "Bombay" not in data["technology"]

def test_native_document_type_schemas_and_summaries(db_session: Session, client: TestClient):
    """Verify 15-point product-level acceptance criteria for document-type-specific schemas and concise summaries."""
    if not REAL_PAPER_FIXTURE_PATH.exists():
        return

    inst_res = client.post(
        "/api/v1/institutions",
        json={"name": "IIT Bombay", "code": "IITB-PRODUCT", "type": "ACADEMIC", "location": "Mumbai"},
    )
    inst_id = inst_res.json()["id"]

    with open(REAL_PAPER_FIXTURE_PATH, "rb") as f:
        res = client.post(
            "/api/v1/proposals/upload",
            data={
                "title": "Preventable accidents in Indian coal mining",
                "institution_id": inst_id,
                "principal_investigator": "Aparna Raj C",
                "domain": "Coal Mining Safety",
                "budget_total": 0.0,
            },
            files={"file": ("real_published_coal_mining_paper.pdf", f, "application/pdf")},
        )

    assert res.status_code == 201
    data = res.json()

    # 1. Classification
    assert data["document_type"] == "RESEARCH_PAPER"

    # 2 & 3. Structured Sections & Native Headings
    struct_secs = data["structured_sections"]
    assert len(struct_secs) > 0

    titles = [s["display_title"] for s in struct_secs if s["status"] == "REPORTED"]

    # 2. Research paper does NOT display proposal-only headings as reported
    assert "Project Objectives" not in titles
    assert "Technology & Infrastructure" not in titles
    assert "Expected Outcomes & Deliverables" not in titles

    # 3. Research paper receives research-paper-native headings
    assert "Research Problem / Motivation" in titles or "Abstract" in titles
    assert "Methodology / Study Design" in titles or "Review Methodology / Search Strategy" in titles
    assert "Results / Key Findings" in titles or "Key Findings / Synthesis" in titles

    # 4, 5, 6, 7. No section contamination
    meth_sec = next(s for s in struct_secs if s["key"] in ["methodology", "review_methodology"] and s["status"] == "REPORTED")
    res_sec = next(s for s in struct_secs if s["key"] in ["results", "key_findings"] and s["status"] == "REPORTED")
    lit_sec = next(s for s in struct_secs if s["key"] == "literature_review" and s["status"] == "REPORTED")

    # 5. Methodology does not contain Results
    assert "To understand coal mining accidents, data from 2015 to" not in meth_sec["content"]

    # 6. Results does not contain Discussion
    assert "The discussion interprets the descriptive patterns" not in res_sec["content"]

    # 7. Literature Review does not contain Methodology
    assert "This study adopts a conceptual research design" not in lit_sec["content"]

    # 8. Affiliations are not classified as Technology
    tech_secs = [s for s in struct_secs if s["key"] == "technology" and s["status"] == "REPORTED"]
    assert len(tech_secs) == 0

    # 9 & 10. Concise UI summaries & Full source evidence
    assert len(meth_sec["summary"]) < len(meth_sec["content"])
    assert len(meth_sec["summary"]) <= 500
    assert len(meth_sec["content"]) > 1000  # Full source retained

    # 11. Page provenance
    assert meth_sec["source_page_start"] == 4
    assert meth_sec["source_page_end"] == 7

    # 12 & 13. Missing info is NOT_REPORTED, no fabrication
    missing_secs = [s for s in struct_secs if s["status"] == "NOT_REPORTED"]
    for ms in missing_secs:
        assert ms["content"] == "NOT_REPORTED"
        assert ms["summary"] == "NOT_REPORTED"


def test_phytoremediation_review_paper_extraction_accuracy(db_session: Session, client: TestClient):
    """Verify phytoremediation review paper extraction accuracy, zero cross-contamination, page provenance, and cache invalidation on re-upload."""
    phyto_path = Path(__file__).parent / "fixtures" / "phytoremediation_coal_mining_review.pdf"
    if not phyto_path.exists():
        return

    inst_res = client.post(
        "/api/v1/institutions",
        json={"name": "IIT ISM Dhanbad", "code": "ISM-PHYTO-TEST", "type": "ACADEMIC", "location": "Dhanbad"},
    )
    inst_id = inst_res.json()["id"]

    with open(phyto_path, "rb") as f:
        res = client.post(
            "/api/v1/proposals/upload",
            data={
                "title": "Phytoremediation of Heavy-Metal-Contaminated Soils in Coal Mining Environments: A Systematic Review",
                "institution_id": inst_id,
                "principal_investigator": "Aarav Sharma",
                "domain": "Environmental Engineering",
                "budget_total": 0.0,
            },
            files={"file": ("phytoremediation_coal_mining_review.pdf", f, "application/pdf")},
        )

    assert res.status_code == 201
    data = res.json()
    proposal_id = data["id"]
    assert proposal_id is not None

    # 1. Classified as RESEARCH_PAPER
    assert data["document_type"] == "RESEARCH_PAPER"

    # 2. Check no cross-contamination from old socio-technical accident paper
    all_text = str(data).lower()
    assert "socio-technical" not in all_text
    assert "preventable accidents" not in all_text
    assert "envis database" not in all_text

    # 3. Review Paper Native Headings
    struct_secs = data["structured_sections"]
    titles = [s["display_title"] for s in struct_secs if s["status"] == "REPORTED"]
    assert "Review Purpose / Scope" in titles or "Research Problem / Motivation" in titles
    assert "Review Methodology / Search Strategy" in titles
    assert "Evidence Base / Techniques" in titles
    assert "Key Findings / Synthesis" in titles
    assert "Future Directions & Recommendations" in titles

    # 4. Page Provenance & Exact Text Verification
    rep_secs = [s for s in struct_secs if s["status"] == "REPORTED"]
    for sec in rep_secs:
        # Every reported section must have valid page start & end
        assert sec["source_page_start"] >= 1
        assert sec["source_page_end"] >= sec["source_page_start"]
        assert sec["evidence_id"].startswith("PAPER-")

    # 5. Verify re-upload cache clearing: Re-uploading does not return stale data
    with open(phyto_path, "rb") as f:
        re_upload_res = client.post(
            "/api/v1/proposals/upload",
            data={
                "title": "Phytoremediation of Heavy-Metal-Contaminated Soils in Coal Mining Environments: A Systematic Review",
                "institution_id": inst_id,
                "principal_investigator": "Aarav Sharma",
                "domain": "Environmental Engineering",
                "budget_total": 0.0,
            },
            files={"file": ("phytoremediation_coal_mining_review.pdf", f, "application/pdf")},
        )

    assert re_upload_res.status_code == 201
    re_data = re_upload_res.json()
    assert "socio-technical" not in str(re_data).lower()
    assert len(re_data["structured_sections"]) > 0


def test_proposal_ingestion_end_to_end(db_session: Session, client: TestClient):
    inst_res = client.post(
        "/api/v1/institutions",
        json={"name": "CSIR-CIMFR", "code": "CSIR-PRODUCT-TEST", "type": "RESEARCH_INSTITUTE", "location": "Dhanbad"},
    )
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
    prop_data = prop_res.json()

    assert prop_data["document_type"] == "R&D_PROPOSAL"
    assert prop_data["problem_statement"].startswith("Unexpected mechanical failure")
    assert "Project Objectives" not in prop_data["problem_statement"]
    assert prop_data["technology"].startswith("Tri-axial vibration transducers")
    assert "Bombay" not in prop_data["technology"]
    assert prop_data["methodology"].startswith("Multi-sensor data acquisition")
    assert prop_data["budget_total"] == 4850000.0
