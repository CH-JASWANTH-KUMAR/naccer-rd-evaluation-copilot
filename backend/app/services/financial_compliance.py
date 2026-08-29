import re

from app.models.proposal import Proposal
from app.schemas.proposal import FinancialComplianceReportRead, FinancialHeadBreakdownRead


class FinancialComplianceService:
    @staticmethod
    def evaluate_financial_compliance(proposal: Proposal) -> FinancialComplianceReportRead:
        findings: list[FinancialHeadBreakdownRead] = []
        declared_total = float(proposal.budget_total) if proposal.budget_total is not None else 0.0

        # 1. Inspect existing financial check records or raw document pages for component breakdown
        component_sum = 0.0
        has_components = False

        if proposal.financial_checks:
            has_components = True
            component_sum = sum(fc.actual_value or fc.expected_value or 0.0 for fc in proposal.financial_checks)
            for fc in proposal.financial_checks:
                val = fc.actual_value or fc.expected_value or 0.0
                findings.append(
                    FinancialHeadBreakdownRead(
                        cost_head=fc.check_type,
                        proposed_amount=val,
                        raw_amount_string=f"Rs. {val:,.2f}",
                        compliance_status=fc.status,
                        notes=fc.notes,
                    )
                )
        else:
            # Fallback: scan document text for budget lines & table rows
            extracted_heads = FinancialComplianceService._extract_budget_heads_from_documents(proposal)
            if extracted_heads:
                has_components = True
                component_sum = sum(item["amount"] for item in extracted_heads)
                for item in extracted_heads:
                    findings.append(
                        FinancialHeadBreakdownRead(
                            cost_head=item["cost_head"],
                            proposed_amount=item["amount"],
                            raw_amount_string=item["raw_string"],
                            compliance_status="COMPLIANT",
                            source_page=item["source_page"],
                            notes=f"Extracted from proposal document Page {item['source_page']}.",
                        )
                    )

        # 2. Perform Rule-Based Arithmetic Verification
        arithmetic_mismatch = False
        difference_amount = 0.0

        if has_components and declared_total > 0:
            diff = abs(declared_total - component_sum)
            if diff > 100.0:  # Tolerance threshold for rounding
                arithmetic_mismatch = True
                difference_amount = diff
                findings.append(
                    FinancialHeadBreakdownRead(
                        cost_head="ARITHMETIC_VERIFICATION",
                        proposed_amount=declared_total,
                        raw_amount_string=f"Declared: Rs. {declared_total:,.2f} | Component Sum: Rs. {component_sum:,.2f}",
                        compliance_status="FLAGGED",
                        notes=f"Arithmetic Mismatch Error: Declared budget (Rs. {declared_total:,.2f}) does not match component sum (Rs. {component_sum:,.2f}). Difference: Rs. {diff:,.2f}.",
                    )
                )

        # Determine Compliance Status
        if arithmetic_mismatch:
            status = "FLAGGED"
        elif not has_components:
            status = "NEEDS_JUSTIFICATION"
            findings.append(
                FinancialHeadBreakdownRead(
                    cost_head="COMPONENT_BREAKDOWN",
                    proposed_amount=declared_total,
                    raw_amount_string=f"Rs. {declared_total:,.2f}",
                    compliance_status="NEEDS_JUSTIFICATION",
                    notes="Component-wise budget breakdown (Personnel, Equipment, Consumables) was not identified.",
                )
            )
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

        # Specific itemized cost head patterns matching Indian research proposals
        patterns = [
            r"(Equipment(?:\s+and\s+sensor\s+interfaces)?|Facilities|Infrastructure)\s*[:=\-–]?\s*(?:Rs\.?|INR)?\s*([\d\.\,]+\s*(?:Lakhs?|Crores?)?)",
            r"(Project\s+personnel|Personnel|Manpower|Staff)\s*[:=\-–]?\s*(?:Rs\.?|INR)?\s*([\d\.\,]+\s*(?:Lakhs?|Crores?)?)",
            r"(Software(?:\s+and\s+computing)?|Computing)\s*[:=\-–]?\s*(?:Rs\.?|INR)?\s*([\d\.\,]+\s*(?:Lakhs?|Crores?)?)",
            r"(Field\s+trials(?:\s+and\s+travel)?|Travel)\s*[:=\-–]?\s*(?:Rs\.?|INR)?\s*([\d\.\,]+\s*(?:Lakhs?|Crores?)?)",
            r"(Contingency)\s*[:=\-–]?\s*(?:Rs\.?|INR)?\s*([\d\.\,]+\s*(?:Lakhs?|Crores?)?)",
            r"(Consumables)\s*[:=\-–]?\s*(?:Rs\.?|INR)?\s*([\d\.\,]+\s*(?:Lakhs?|Crores?)?)",
            r"(Overheads?)\s*[:=\-–]?\s*(?:Rs\.?|INR)?\s*([\d\.\,]+\s*(?:Lakhs?|Crores?)?)",
        ]

        seen_heads: set[str] = set()

        for doc in proposal.documents:
            for page in doc.pages:
                txt = page.text or ""
                for pat in patterns:
                    matches = re.findall(pat, txt, re.IGNORECASE)
                    for head_name, raw_amt in matches:
                        clean_head = head_name.strip()
                        key = clean_head.lower()
                        if key in seen_heads:
                            continue
                        val = FinancialComplianceService._parse_currency(raw_amt)
                        if val > 0:
                            seen_heads.add(key)
                            raw_str = f"Rs. {raw_amt.strip()}" if not raw_amt.strip().lower().startswith("rs") else raw_amt.strip()
                            heads.append({
                                "cost_head": clean_head,
                                "amount": val,
                                "raw_string": raw_str,
                                "source_page": page.page_number,
                            })

        return heads

    @staticmethod
    def _parse_currency(raw_val: str) -> float:
        if not raw_val:
            return 0.0
        clean = raw_val.replace(",", "").strip()
        nums = re.findall(r"\d+(?:\.\d+)?", clean)
        if not nums:
            return 0.0
        val = float(nums[0])
        low = clean.lower()
        if "lakh" in low:
            val *= 100000.0
        elif "crore" in low:
            val *= 10000000.0
        return val
