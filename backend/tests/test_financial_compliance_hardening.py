"""Financial Compliance Hardening & Data Provenance Regression Tests.

Tests the 5 explicit financial evaluation scenarios:
A. Mismatch Breakdown (Declared != Component Sum) -> MISMATCH
B. Exact Breakdown (Declared == Component Sum) -> MATCH
C. No Itemized Components -> NOT_VERIFIABLE (calculated_total is None)
D. Partial Breakdown -> PARTIAL_BREAKDOWN (do not assume missing components are 0)
E. Data Provenance & Page Traceability
"""

from unittest.mock import MagicMock

from app.models.financial_check import FinancialCheck
from app.models.proposal import Proposal
from app.services.financial_compliance import FinancialComplianceService


def test_financial_compliance_scenario_a_mismatch():
    """Scenario A: Declared Rs. 48,50,000, Components sum to Rs. 46,50,000 -> MISMATCH."""
    prop = Proposal(
        id="prop-mismatch-test",
        title="Test Proposal",
        budget_total=4850000.0,
        financial_checks=[
            FinancialCheck(check_type="Equipment", actual_value=2500000.0, status="COMPLIANT"),
            FinancialCheck(check_type="Personnel", actual_value=1500000.0, status="COMPLIANT"),
            FinancialCheck(check_type="Consumables", actual_value=650000.0, status="COMPLIANT"),
        ],
    )

    report = FinancialComplianceService.evaluate_financial_compliance(prop)

    assert report.declared_total == 4850000.0
    assert report.calculated_total == 4650000.0
    assert report.variance_amount == 200000.0
    assert report.arithmetic_status == "MISMATCH"
    assert report.status == "FLAGGED"
    assert report.arithmetic_mismatch is True
    assert report.difference_amount == 200000.0
    assert "differs from declared total" in report.explanation


def test_financial_compliance_scenario_b_exact_match():
    """Scenario B: Declared Rs. 35,00,000, Components sum to Rs. 35,00,000 -> MATCH."""
    prop = Proposal(
        id="prop-match-test",
        title="Test Proposal Match",
        budget_total=3500000.0,
        financial_checks=[
            FinancialCheck(check_type="Equipment", actual_value=1800000.0, status="COMPLIANT"),
            FinancialCheck(check_type="Personnel", actual_value=1200000.0, status="COMPLIANT"),
            FinancialCheck(check_type="Consumables", actual_value=500000.0, status="COMPLIANT"),
        ],
    )

    report = FinancialComplianceService.evaluate_financial_compliance(prop)

    assert report.declared_total == 3500000.0
    assert report.calculated_total == 3500000.0
    assert report.variance_amount == 0.0
    assert report.arithmetic_status == "MATCH"
    assert report.status == "COMPLIANT"
    assert report.arithmetic_mismatch is False
    assert report.difference_amount == 0.0
    assert "matches the declared total budget" in report.explanation


def test_financial_compliance_scenario_c_no_components():
    """Scenario C: Declared Rs. 35,00,000, No components -> NOT_VERIFIABLE (calculated_total is None)."""
    prop = Proposal(
        id="prop-no-comp-test",
        title="Test Proposal No Components",
        budget_total=3500000.0,
        financial_checks=[],
        documents=[],
    )

    report = FinancialComplianceService.evaluate_financial_compliance(prop)

    assert report.declared_total == 3500000.0
    assert report.calculated_total is None
    assert report.variance_amount is None
    assert report.arithmetic_status == "NOT_VERIFIABLE"
    assert report.extraction_summary_status == "MISSING_BREAKDOWN"
    assert report.status == "NEEDS_JUSTIFICATION"
    assert len(report.findings) == 0
    assert "no reliable cost-head amounts were extracted" in report.explanation


def test_financial_compliance_scenario_d_partial_breakdown():
    """Scenario D: Declared Rs. 35,00,000, Only 1 component extracted -> PARTIAL_BREAKDOWN (do not assume missing components are 0)."""
    prop = Proposal(
        id="prop-partial-test",
        title="Test Proposal Partial",
        budget_total=3500000.0,
        financial_checks=[
            FinancialCheck(check_type="Equipment", actual_value=1800000.0, status="COMPLIANT"),
        ],
    )

    report = FinancialComplianceService.evaluate_financial_compliance(prop)

    assert report.declared_total == 3500000.0
    assert report.calculated_total == 1800000.0
    assert report.variance_amount == 1700000.0
    assert report.extraction_summary_status == "PARTIAL_BREAKDOWN"
    assert report.arithmetic_status == "MISMATCH"
    assert report.status == "FLAGGED"
    assert "Partial budget breakdown extracted" in report.explanation
    assert "not assumed to be zero" not in report.explanation or "may not have been reported" in report.explanation


def test_financial_compliance_scenario_e_data_provenance():
    """Scenario E: Data provenance - Every extracted component retains source_page, raw_amount_string, and extraction_status."""
    dummy_doc = MagicMock()
    dummy_doc.pages = [
        MagicMock(page_number=3, text="Equipment: Rs. 18.00 Lakhs\nPersonnel: Rs. 12.00 Lakhs"),
        MagicMock(page_number=4, text="Field trials: Rs. 5.00 Lakhs"),
    ]

    prop = Proposal(
        id="prop-provenance-test",
        title="Test Proposal Provenance",
        budget_total=3500000.0,
        financial_checks=[],
        documents=[dummy_doc],
    )

    report = FinancialComplianceService.evaluate_financial_compliance(prop)

    assert len(report.findings) == 3
    assert report.calculated_total == 3500000.0
    assert report.arithmetic_status == "MATCH"

    eq_finding = next(f for f in report.findings if f.cost_head == "Equipment")
    assert eq_finding.source_page == 3
    assert eq_finding.proposed_amount == 1800000.0
    assert eq_finding.raw_amount_string == "Rs. 18.00 Lakhs"
    assert eq_finding.extraction_status == "EXTRACTED"
