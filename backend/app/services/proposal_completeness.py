from app.models.proposal import Proposal
from app.schemas.proposal import CompletenessFindingRead, ProposalCompletenessReportRead


class ProposalCompletenessService:
    @staticmethod
    def evaluate_completeness(proposal: Proposal) -> ProposalCompletenessReportRead:
        missing_fields: list[str] = []
        warnings: list[str] = []
        findings: list[CompletenessFindingRead] = []

        # 1. Mandatory Core Scrutiny Checklist
        if not proposal.title or not proposal.title.strip():
            missing_fields.append("title")
            findings.append(
                CompletenessFindingRead(
                    field="title",
                    severity="ERROR",
                    message="Proposal project title is missing.",
                )
            )

        if not proposal.objectives or len(proposal.objectives.strip()) < 15:
            missing_fields.append("objectives")
            findings.append(
                CompletenessFindingRead(
                    field="objectives",
                    severity="ERROR",
                    message="Technical objectives section is missing or incomplete.",
                )
            )

        if not proposal.methodology or len(proposal.methodology.strip()) < 15:
            missing_fields.append("methodology")
            findings.append(
                CompletenessFindingRead(
                    field="methodology",
                    severity="ERROR",
                    message="Research methodology / technical approach section is missing.",
                )
            )

        if proposal.budget_total is None or proposal.budget_total <= 0:
            missing_fields.append("budget_total")
            findings.append(
                CompletenessFindingRead(
                    field="budget_total",
                    severity="ERROR",
                    message="Total requested budget is zero or unspecified.",
                )
            )

        if proposal.extracted_principal_investigator and proposal.principal_investigator:
            admin_pi = proposal.principal_investigator.strip()
            doc_pi = proposal.extracted_principal_investigator.strip()
            if admin_pi.lower() not in doc_pi.lower() and doc_pi.lower() not in admin_pi.lower():
                warnings.append("Administrative metadata PI differs from document-extracted PI.")
                findings.append(
                    CompletenessFindingRead(
                        field="principal_investigator",
                        severity="WARNING",
                        message=f"Administrative metadata PI ({admin_pi}) differs from document-extracted PI ({doc_pi}).",
                    )
                )

        # 2. Recommended Secondary Fields
        if not proposal.problem_statement or len(proposal.problem_statement.strip()) < 15:
            missing_fields.append("problem_statement")
            warnings.append("Problem statement / background context is incomplete.")
            findings.append(
                CompletenessFindingRead(
                    field="problem_statement",
                    severity="WARNING",
                    message="Problem statement section could not be clearly identified.",
                )
            )

        if not proposal.expected_outcomes or len(proposal.expected_outcomes.strip()) < 15:
            missing_fields.append("expected_outcomes")
            warnings.append("Expected deliverables / R&D outcomes section is missing.")
            findings.append(
                CompletenessFindingRead(
                    field="expected_outcomes",
                    severity="WARNING",
                    message="Expected deliverables section is incomplete.",
                )
            )

        if not proposal.domain or proposal.domain == "Coal Mining R&D":
            warnings.append("Research domain is set to default generic category.")
            findings.append(
                CompletenessFindingRead(
                    field="domain",
                    severity="INFO",
                    message="Research domain should be specified for benchmarking.",
                )
            )

        # Overall Status
        has_errors = any(f.severity == "ERROR" for f in findings)
        status = "INCOMPLETE" if has_errors else "COMPLETE"

        return ProposalCompletenessReportRead(
            proposal_id=proposal.id,
            status=status,
            missing_fields=missing_fields,
            warnings=warnings,
            findings=findings,
        )
