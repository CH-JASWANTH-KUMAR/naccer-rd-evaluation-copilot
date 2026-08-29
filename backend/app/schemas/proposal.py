from datetime import datetime

from pydantic import Field

from app.schemas.common import ORMBase
from app.schemas.institution import InstitutionRead


class CompletenessFindingRead(ORMBase):
    field: str
    severity: str = Field(description="ERROR, WARNING, or INFO")
    message: str


class ProposalCompletenessReportRead(ORMBase):
    proposal_id: str
    status: str = Field(description="COMPLETE or INCOMPLETE")
    missing_fields: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    findings: list[CompletenessFindingRead] = Field(default_factory=list)


class FinancialHeadBreakdownRead(ORMBase):
    cost_head: str
    proposed_amount: float
    raw_amount_string: str | None = None
    compliance_status: str = "COMPLIANT"
    source_page: int | None = None
    notes: str | None = None


class FinancialComplianceReportRead(ORMBase):
    proposal_id: str
    status: str = Field(description="COMPLIANT, FLAGGED, or NEEDS_JUSTIFICATION")
    declared_total: float
    calculated_total: float
    arithmetic_mismatch: bool
    difference_amount: float
    findings: list[FinancialHeadBreakdownRead] = Field(default_factory=list)


class ProposalCreate(ORMBase):
    title: str
    institution_id: str
    principal_investigator: str
    extracted_principal_investigator: str | None = None
    domain: str
    problem_statement: str | None = None
    objectives: str | None = None
    methodology: str | None = None
    technology: str | None = None
    literature_review: str | None = None
    expected_outcomes: str | None = None
    timeline: str | None = None
    duration_months: int | None = 12
    status: str = "UNDER_REVIEW"
    priority: str = "MEDIUM"
    budget_total: float | None = None
    raw_budget_text: str | None = None


class ProposalUpdate(ORMBase):
    title: str | None = None
    principal_investigator: str | None = None
    extracted_principal_investigator: str | None = None
    domain: str | None = None
    problem_statement: str | None = None
    objectives: str | None = None
    methodology: str | None = None
    technology: str | None = None
    expected_outcomes: str | None = None
    duration_months: int | None = None
    status: str | None = None
    priority: str | None = None
    budget_total: float | None = None
    raw_budget_text: str | None = None


class ProposalRead(ORMBase):
    id: str
    proposal_reference: str
    title: str
    institution_id: str
    institution: InstitutionRead | None = None
    principal_investigator: str
    extracted_principal_investigator: str | None = None
    domain: str
    problem_statement: str | None = None
    objectives: str | None = None
    methodology: str | None = None
    technology: str | None = None
    literature_review: str | None = None
    expected_outcomes: str | None = None
    timeline: str | None = None
    duration_months: int | None = 12
    status: str
    priority: str
    budget_total: float | None = None
    raw_budget_text: str | None = None
    completeness_status: str
    compliance_status: str
    processing_status: str
    processing_error: str | None = None
    submission_date: datetime
    created_at: datetime
    updated_at: datetime
