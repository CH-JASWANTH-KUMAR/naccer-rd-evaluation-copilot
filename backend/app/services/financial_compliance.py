import re

from app.models.proposal import Proposal
from app.schemas.proposal import FinancialComplianceReportRead


class FinancialComplianceService:
    @staticmethod
    def evaluate_financial_compliance(proposal: Proposal) -> FinancialComplianceReportRead:
        findings: list[dict] = []
        declared_total = float(proposal.budget_total)

        # 1. Inspect existing financial check records or raw document pages for component breakdown
        component_sum = 0.0
        has_components = False

        if proposal.financial_checks:
            has_components = True
            component_sum = sum(fc.actual_value or fc.expected_value or 0.0 for fc in proposal.financial_checks)
            for fc in proposal.financial_checks:
                findings.append({
                    "cost_head": fc.check_type,
                    "proposed_amount": fc.actual_value or fc.expected_value or 0.0,
                    "compliance_status": fc.status,
                    "notes": fc.notes,
                })
        else:
            # Fallback: scan document text for budget lines (e.g. Equipment: Rs 5,00,000, Personnel: Rs 2,00,000)
            extracted_heads = FinancialComplianceService._extract_budget_heads_from_documents(proposal)
            if extracted_heads:
                has_components = True
                component_sum = sum(item["amount"] for item in extracted_heads)
                for item in extracted_heads:
                    findings.append({
                        "cost_head": item["cost_head"],
                        "proposed_amount": item["amount"],
                        "compliance_status": "COMPLIANT",
                        "notes": "Extracted from proposal document budget section.",
                    })

        # 2. Perform Rule-Based Arithmetic Verification
        arithmetic_mismatch = False
        difference_amount = 0.0

        if has_components and declared_total > 0:
            diff = abs(declared_total - component_sum)
            if diff > 100.0:  # Tolerance threshold for rounding
                arithmetic_mismatch = True
                difference_amount = diff
                findings.append({
                    "cost_head": "ARITHMETIC_VERIFICATION",
                    "proposed_amount": declared_total,
                    "compliance_status": "FLAGGED",
                    "notes": f"Arithmetic Mismatch Error: Declared budget (Rs. {declared_total:,.2f}) does not match component breakdown sum (Rs. {component_sum:,.2f}). Difference: Rs. {diff:,.2f}.",
                })

        # Determine Compliance Status
        if arithmetic_mismatch:
            status = "FLAGGED"
        elif not has_components:
            status = "NEEDS_JUSTIFICATION"
            findings.append({
                "cost_head": "COMPONENT_BREAKDOWN",
                "proposed_amount": declared_total,
                "compliance_status": "NEEDS_JUSTIFICATION",
                "notes": "Component-wise budget breakdown (Personnel, Equipment, Consumables) was not identified.",
            })
        else:
            status = "COMPLIANT"

        return FinancialComplianceReportRead(
            proposal_id=proposal.id,
            status=status,
            declared_total=declared_total,
            calculated_total=component_sum if has_components else declared_total,
            arithmetic_mismatch=arithmetic_mismatch,
            difference_amount=difference_amount,
            findings=findings,
        )

    @staticmethod
    def _extract_budget_heads_from_documents(proposal: Proposal) -> list[dict]:
        heads: list[dict] = []
        if not proposal.documents:
            return heads

        for doc in proposal.documents:
            for page in doc.pages:
                txt = page.text or ""
                # Look for budget patterns: Head: Rs. Amount
                matches = re.findall(
                    r"(Personnel|Staff|Equipment|Consumables|Travel|Contingency|Overheads)\s*:?\s*(?:Rs\.?|INR)?\s*([\d\.\,]+\s*(?:Lakhs?|Crores?)?)",
                    txt,
                    re.IGNORECASE,
                )
                for head_name, raw_amt in matches:
                    val = FinancialComplianceService._parse_currency(raw_amt)
                    if val > 0:
                        heads.append({"cost_head": head_name.capitalize(), "amount": val})

        return heads

    @staticmethod
    def _parse_currency(raw_val: str) -> float:
        if not raw_val:
            return 0.0
        nums = re.findall(r"\d+(?:\.\d+)?", raw_val.replace(",", ""))
        if not nums:
            return 0.0
        val = float(nums[0])
        if "lakh" in raw_val.lower():
            val *= 100000.0
        elif "crore" in raw_val.lower():
            val *= 10000000.0
        return val
