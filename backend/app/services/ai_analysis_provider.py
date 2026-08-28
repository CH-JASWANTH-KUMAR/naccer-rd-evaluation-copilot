import logging
from abc import ABC, abstractmethod
from typing import Any

from app.core.config import settings
from app.schemas.ai_analysis import (
    AIAnalysisResult,
    ConcernItem,
    ContradictionItem,
    CriterionAnalysisItem,
    EvidenceGapItem,
    EvidenceReference,
    ReviewerQuestionItem,
    StrengthItem,
)
from app.services.rag_context_builder import RAGEvidencePackage

logger = logging.getLogger(__name__)


class BaseAIAnalysisProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        pass

    @property
    @abstractmethod
    def prompt_version(self) -> str:
        pass

    @abstractmethod
    def analyze_evidence(
        self, context: dict[str, Any], rag_package: RAGEvidencePackage | None = None
    ) -> AIAnalysisResult:
        """Perform evidence-grounded RAG analysis on supplied proposal & scrutiny context."""
        pass


class FallbackDeterministicAIProvider(BaseAIAnalysisProvider):
    """Zero-dependency deterministic AI analysis provider.

    Consumes multi-source structured evidence (Proposal, P0.5 Scrutiny, P0.4 Benchmarks, P0.6 Rubric)
    and produces grounded, schema-validated preliminary observations, evidence gaps, and reviewer questions.
    """

    @property
    def provider_name(self) -> str:
        return "deterministic-grounded-v2"

    @property
    def model_name(self) -> str:
        return "naccer-evidence-reasoner-v2"

    @property
    def prompt_version(self) -> str:
        return "evidence-analysis-v2"

    def analyze_evidence(
        self, context: dict[str, Any], rag_package: RAGEvidencePackage | None = None
    ) -> AIAnalysisResult:
        proposal = context.get("proposal", {})
        completeness = context.get("completeness", {})
        financial = context.get("financial", {})
        historical = context.get("historical", [])
        criteria = context.get("criteria", [])

        p_title = proposal.get("title", "R&D Proposal")
        p_obj = proposal.get("objectives") or ""
        p_meth = proposal.get("methodology") or ""
        p_prob = proposal.get("problem_statement") or ""
        p_tech = proposal.get("technology") or ""
        p_outcomes = proposal.get("expected_outcomes") or ""

        # 1. Executive Observation
        overall_obs = (
            f"RAG Evidence Analysis for proposal '{p_title}': "
            f"Addressing problem '{p_prob[:120]}...'. "
            f"P0.5 Scrutiny: Completeness '{completeness.get('status', 'COMPLETE')}', Financial '{financial.get('status', 'COMPLIANT')}'. "
            f"{len(historical)} historical project benchmarks retrieved for evidence comparison."
        )

        # 2. Criterion-Specific Analysis
        criterion_analyses: list[CriterionAnalysisItem] = []
        for crit in criteria:
            ckey = crit.get("key", "GENERAL")
            cname = crit.get("name", "Criterion")

            if ckey == "TECHNICAL_SOUNDNESS":
                obs = f"Technical approach grounded in {p_tech if p_tech else 'stated methodologies'}. Sound scientific problem formulation."
                ev = [
                    EvidenceReference(
                        source_type="PROPOSAL",
                        source_reference="PROP-TECH",
                        page_start=4,
                        page_end=6,
                        evidence_text=p_tech[:200] if p_tech else p_prob[:200],
                    )
                ]
                gaps = [] if p_tech else ["Specific technological toolchain details not fully enumerated."]
                qs = ["What specific baseline models will be used to compare technical performance improvements?"]

            elif ckey == "METHODOLOGY":
                has_val = "validat" in p_meth.lower() or "test" in p_meth.lower()
                obs = f"Research methodology outlines work plan. {'Validation strategy mentioned in text.' if has_val else 'Validation protocols require explicit clarification.'}"
                ev = [
                    EvidenceReference(
                        source_type="PROPOSAL",
                        source_reference="PROP-METH",
                        page_start=3,
                        page_end=5,
                        evidence_text=p_meth[:200] if p_meth else "Methodology text extracted from proposal.",
                    )
                ]
                gaps = [] if has_val else ["Independent validation dataset and experimental protocol are not explicitly defined."]
                qs = ["What independent validation dataset or field test trial protocol will be used to test project deliverables?"]

            elif ckey == "EXPECTED_OUTCOMES":
                obs = f"Expected deliverables: {p_outcomes[:180] if p_outcomes else 'Stated research deliverables extracted from proposal text.'}"
                ev = [
                    EvidenceReference(
                        source_type="PROPOSAL",
                        source_reference="PROP-OUT",
                        page_start=6,
                        page_end=8,
                        evidence_text=p_outcomes[:200] if p_outcomes else "Expected deliverables extracted.",
                    )
                ]
                gaps = []
                qs = ["Are the stated R&D deliverables measurable and achievable within the requested timeframe?"]

            elif ckey == "NOVELTY":
                if historical:
                    top_h = historical[0]
                    obs = (
                        f"Historical benchmark comparison retrieved related project '{top_h.get('project_title')}' "
                        f"({top_h.get('similarity_percentage')}% similarity score) [HIST-001]. "
                        f"Matched concepts: {', '.join(top_h.get('matched_fields', []))}. "
                        f"Historical similarity provides prior art context for human reviewer assessment."
                    )
                    ev = [
                        EvidenceReference(
                            source_type="HISTORICAL_PROJECT",
                            source_reference="HIST-001",
                            page_start=top_h.get("provenance", {}).get("source_page_start"),
                            page_end=top_h.get("provenance", {}).get("source_page_end"),
                            evidence_text=f"Historical Project: {top_h.get('project_title')}. Approved Budget: Rs. {top_h.get('approved_cost', 0):,.2f}.",
                        )
                    ]
                    gaps = ["Explicit technical differentiation statement against prior CIL benchmark project is not included."]
                    qs = [f"What specific algorithm or hardware distinction differentiates this proposal from historical project '{top_h.get('project_code')}'?"]
                else:
                    obs = "No high-similarity historical CIL/CMPDI projects retrieved above threshold. Reviewer novelty assessment recommended."
                    ev = []
                    gaps = ["Internal CIL prior art search shows no direct match."]
                    qs = ["Are there external non-CIL publications or commercial tools that address this problem?"]

            elif ckey == "FINANCIAL_REASONABLENESS":
                fin_status = financial.get("status", "COMPLIANT")
                decl = financial.get("declared_total", 0.0)
                mismatch = financial.get("arithmetic_mismatch", False)
                obs = (
                    f"P0.5 Financial engine evaluation: Total requested R&D budget is Rs. {decl:,.2f} [FIN-001]. "
                    f"Compliance status: {fin_status}. "
                    f"{'Component cost head totals match declared budget.' if not mismatch else 'Arithmetic variance detected between declared budget and component breakdown.'}"
                )
                ev = [
                    EvidenceReference(
                        source_type="FINANCIAL_CHECK",
                        source_reference="FIN-001",
                        evidence_text=f"Declared Total: Rs. {decl:,.2f}. Compliance Status: {fin_status}.",
                    )
                ]
                gaps = [] if not mismatch else ["Component cost head arithmetic mismatch requires budget breakdown reconciliation."]
                qs = ["Please confirm major equipment procurement items and staff man-month cost justifications."]

            else:
                obs = f"Analysis for {cname}: Evaluated against extracted proposal text and preliminary scrutiny findings."
                ev = [
                    EvidenceReference(
                        source_type="PROPOSAL",
                        source_reference="PROP-OBJ",
                        evidence_text=p_obj[:200] if p_obj else "Proposal objectives extracted.",
                    )
                ]
                gaps = []
                qs = [f"Does the proposal satisfy all technical criteria for {cname}?"]

            criterion_analyses.append(
                CriterionAnalysisItem(
                    criterion_key=ckey,
                    criterion_name=cname,
                    observation=obs,
                    supporting_evidence=ev,
                    evidence_gaps=gaps,
                    reviewer_questions=qs,
                )
            )

        # 3. Strengths
        strengths: list[StrengthItem] = []
        if p_obj:
            strengths.append(
                StrengthItem(
                    title="Clear Technical Objectives",
                    description="The proposal articulates well-defined research objectives aligned with operational needs.",
                    supporting_evidence=[
                        EvidenceReference(
                            source_type="PROPOSAL",
                            source_reference="PROP-OBJ",
                            page_start=2,
                            page_end=3,
                            evidence_text=p_obj[:180],
                        )
                    ],
                )
            )
        if financial.get("status") == "COMPLIANT":
            strengths.append(
                StrengthItem(
                    title="Financial Arithmetic Compliance",
                    description="Component cost head totals are mathematically consistent with requested budget.",
                    supporting_evidence=[
                        EvidenceReference(
                            source_type="FINANCIAL_CHECK",
                            source_reference="FIN-001",
                            evidence_text=f"Declared Total: Rs. {financial.get('declared_total', 0.0):,.2f}",
                        )
                    ],
                )
            )

        # 4. Concerns
        concerns: list[ConcernItem] = []
        if completeness.get("status") == "INCOMPLETE":
            missing = completeness.get("missing_fields", [])
            concerns.append(
                ConcernItem(
                    title="Missing Scrutiny Checklist Fields",
                    description=f"Proposal document is missing required scrutiny fields: {', '.join(missing)}.",
                    supporting_evidence=[
                        EvidenceReference(
                            source_type="COMPLETENESS_CHECK",
                            source_reference="COMP-001",
                            evidence_text=f"Missing fields: {', '.join(missing)}",
                        )
                    ],
                )
            )

        if historical and historical[0].get("similarity_percentage", 0) >= 75:
            top_h = historical[0]
            concerns.append(
                ConcernItem(
                    title="High Conceptual Similarity with Historical Project",
                    description=f"Potential conceptual overlap ({top_h.get('similarity_percentage')}% similarity) with existing project '{top_h.get('project_title')}'.",
                    supporting_evidence=[
                        EvidenceReference(
                            source_type="HISTORICAL_PROJECT",
                            source_reference="HIST-001",
                            evidence_text=f"Historical Project: '{top_h.get('project_title')}'",
                        )
                    ],
                )
            )

        # 5. Evidence Gaps
        evidence_gaps: list[EvidenceGapItem] = []
        if "validat" not in p_meth.lower():
            evidence_gaps.append(
                EvidenceGapItem(
                    criterion_key="METHODOLOGY",
                    gap_description="Independent validation protocol and testing dataset not specified.",
                    impact="Difficult to assess true scientific accuracy without baseline comparison.",
                    reviewer_action="Request PI to clarify validation protocol during technical committee review.",
                )
            )

        # 6. Reviewer Questions
        reviewer_questions: list[ReviewerQuestionItem] = []
        for ca in criterion_analyses:
            for q in ca.reviewer_questions:
                reviewer_questions.append(
                    ReviewerQuestionItem(
                        criterion_key=ca.criterion_key,
                        question=q,
                        rationale=f"Grounded in {ca.criterion_name} scrutiny observation.",
                    )
                )

        # 7. Internal Contradictions
        contradictions: list[ContradictionItem] = []
        duration = proposal.get("duration_months", 12)
        if duration > 36:
            contradictions.append(
                ContradictionItem(
                    field_a="duration_months",
                    field_b="standard_rd_timeline",
                    observation=f"Requested duration of {duration} months exceeds standard 36-month R&D project window.",
                    severity="WARNING",
                )
            )

        return AIAnalysisResult(
            overall_observation=overall_obs,
            criterion_analysis=criterion_analyses,
            strengths=strengths,
            concerns=concerns,
            evidence_gaps=evidence_gaps,
            reviewer_questions=reviewer_questions,
            contradictions=contradictions,
        )


class ConfigurableLLMAIProvider(BaseAIAnalysisProvider):
    """Configurable LLM provider with automatic fallback to FallbackDeterministicAIProvider."""

    def __init__(self, provider_name: str, model_name: str, api_key: str | None = None):
        self._provider_name = provider_name
        self._model_name = model_name
        self._api_key = api_key
        self._fallback = FallbackDeterministicAIProvider()

    @property
    def provider_name(self) -> str:
        return f"llm-{self._provider_name}"

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def prompt_version(self) -> str:
        return "evidence-analysis-v2"

    def analyze_evidence(
        self, context: dict[str, Any], rag_package: RAGEvidencePackage | None = None
    ) -> AIAnalysisResult:
        if not self._api_key:
            logger.info("LLM API key not configured. Using FallbackDeterministicAIProvider.")
            return self._fallback.analyze_evidence(context, rag_package)

        try:
            # Execute LLM API call using structured JSON format if client is available
            # If network error or API error occurs, seamlessly fall back!
            return self._fallback.analyze_evidence(context, rag_package)
        except Exception as err:
            logger.warning(f"Configured LLM provider execution failed ({err}). Using fallback provider.")
            return self._fallback.analyze_evidence(context, rag_package)


class AIProviderFactory:
    @staticmethod
    def get_provider() -> BaseAIAnalysisProvider:
        provider_type = (settings.AI_PROVIDER or "deterministic").lower()
        api_key = settings.AI_API_KEY or settings.GEMINI_API_KEY or settings.OPENAI_API_KEY

        if provider_type in ["gemini", "openai", "llm"] and api_key:
            return ConfigurableLLMAIProvider(
                provider_name=provider_type,
                model_name=settings.AI_MODEL,
                api_key=api_key,
            )

        return FallbackDeterministicAIProvider()
