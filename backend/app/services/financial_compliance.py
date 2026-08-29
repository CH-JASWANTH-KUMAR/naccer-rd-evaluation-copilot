import re

from app.models.proposal import Proposal
from app.schemas.proposal import FinancialComplianceReportRead, FinancialHeadBreakdownRead


class FinancialComplianceService:
    @staticmethod
    def evaluate_financial_compliance(proposal: Proposal) -> FinancialComplianceReportRead:
        findings: list[FinancialHeadBreakdownRead] = []
        declared_total = float(proposal.budget_total) if proposal.budget_total is not None else 0.0

        # 1. Inspect existing financial check records or raw document pages for component breakdown
        if proposal.financial_checks:
            for fc in proposal.financial_checks:
                val = fc.actual_value or fc.expected_value or 0.0
                findings.append(
                    FinancialHeadBreakdownRead(
                        cost_head=fc.check_type,
                        proposed_amount=val,
                        normalized_amount=val,
                        raw_amount_string=f"Rs. {val:,.2f}",
                        compliance_status=fc.status,
                        extraction_status="EXTRACTED",
                        notes=fc.notes,
                    )
                )
        else:
            extracted_heads = FinancialComplianceService._extract_budget_heads_from_documents(proposal)
            for item in extracted_heads:
                findings.append(
                    FinancialHeadBreakdownRead(
                        cost_head=item["cost_head"],
                        proposed_amount=item["amount"],
                        normalized_amount=item["amount"],
                        raw_amount_string=item["raw_string"],
                        compliance_status="COMPLIANT",
                        source_page=item["source_page"],
                        extraction_status="EXTRACTED",
                        notes=f"Extracted from proposal document Page {item['source_page']}.",
                    )
                )

        has_components = len(findings) > 0

        # 2. Perform Rule-Based Arithmetic Verification & Status Semantics
        if not has_components:
            calculated_total = None
            variance_amount = None
            arithmetic_status = "NOT_VERIFIABLE"
            extraction_summary_status = "MISSING_BREAKDOWN"
            status = "NEEDS_JUSTIFICATION"
            explanation = (
                f"The proposal declares a total budget of Rs. {declared_total:,.2f}, but no reliable cost-head amounts were extracted. "
                "Therefore, component arithmetic cannot be independently verified."
            )
            arithmetic_mismatch = False
            difference_amount = 0.0
        else:
            calculated_total = sum(f.proposed_amount for f in findings)
            variance_amount = declared_total - calculated_total
            diff = abs(variance_amount)

            # Check if partial or full breakdown (core cost heads: personnel/equipment/contingency)
            found_heads_lower = {f.cost_head.lower() for f in findings}
            is_partial = len(findings) < 3 and not (
                {"personnel", "manpower"}.intersection(found_heads_lower) and {"equipment", "facilities"}.intersection(found_heads_lower)
            )
            extraction_summary_status = "PARTIAL_BREAKDOWN" if is_partial else "FULL_BREAKDOWN"

            if diff <= 100.0:  # Within rounding tolerance
                arithmetic_status = "MATCH"
                status = "COMPLIANT"
                arithmetic_mismatch = False
                difference_amount = 0.0
                if is_partial:
                    explanation = (
                        "Partial budget breakdown extracted. Extracted cost heads reconcile with the declared total, "
                        "but one or more standard cost heads may not have been reported or extracted."
                    )
                else:
                    explanation = "Extracted itemized budget component sum matches the declared total budget."
            else:
                arithmetic_status = "MISMATCH"
                status = "FLAGGED"
                arithmetic_mismatch = True
                difference_amount = diff
                if is_partial:
                    explanation = (
                        f"Partial budget breakdown extracted. Component sum (Rs. {calculated_total:,.2f}) differs from declared total "
                        f"(Rs. {declared_total:,.2f}) by Rs. {diff:,.2f}. Arithmetic verification is partial because one or more cost heads "
                        "may not have been reported or reliably extracted."
                    )
                else:
                    explanation = (
                        f"Component breakdown sum (Rs. {calculated_total:,.2f}) differs from declared total (Rs. {declared_total:,.2f}) "
                        f"by Rs. {diff:,.2f}."
                    )

        return FinancialComplianceReportRead(
            proposal_id=proposal.id,
            status=status,
            declared_total=declared_total,
            calculated_total=calculated_total,
            arithmetic_status=arithmetic_status,
            variance_amount=variance_amount,
            extraction_summary_status=extraction_summary_status,
            explanation=explanation,
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
