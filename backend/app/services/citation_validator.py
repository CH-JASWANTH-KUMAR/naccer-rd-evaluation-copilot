from typing import Any

from app.schemas.ai_analysis import AIAnalysisResult, EvidenceReference


class CitationValidator:
    """Validates evidence citations against the RAG context and enforces safety boundaries."""

    DISALLOWED_TERMS = [
        "AUTONOMOUS_APPROVAL",
        "AUTONOMOUS_REJECTION",
        "DECLARING_NOT_NOVEL",
        "DECLARING_DUPLICATE",
        "GRANTING_FUNDING_AMOUNT",
    ]

    @classmethod
    def validate_and_enrich_result(
        cls,
        result: AIAnalysisResult,
        valid_evidence_ids: set[str],
        evidence_id_map: dict[str, dict[str, Any]],
    ) -> AIAnalysisResult:
        """Filter out hallucinated evidence IDs and populate evidence citations from valid RAG context."""

        def enrich_evidence_list(ref_list: list[EvidenceReference]) -> list[EvidenceReference]:
            enriched: list[EvidenceReference] = []
            for ref in ref_list:
                eid = ref.source_reference
                if eid in valid_evidence_ids:
                    info = evidence_id_map[eid]
                    enriched.append(
                        EvidenceReference(
                            source_type=info["source_type"],
                            source_reference=f"[{eid}] {info['source_reference']}",
                            page_start=info["page_start"],
                            page_end=info["page_end"],
                            evidence_text=info["evidence_text"],
                        )
                    )
                elif ref.source_reference and ref.source_reference.startswith("["):
                    enriched.append(ref)
            return enriched

        # Enrich Criterion Analysis supporting evidence
        for ca in result.criterion_analysis:
            ca.supporting_evidence = enrich_evidence_list(ca.supporting_evidence)

        # Enrich Strengths & Concerns
        for s in result.strengths:
            s.supporting_evidence = enrich_evidence_list(s.supporting_evidence)
        for c in result.concerns:
            c.supporting_evidence = enrich_evidence_list(c.supporting_evidence)

        # Safety Check
        cls.validate_safety_boundaries(result)
        return result

    @classmethod
    def validate_safety_boundaries(cls, result: AIAnalysisResult) -> None:
        text_check = f"{result.overall_observation}".upper()
        for term in cls.DISALLOWED_TERMS:
            if term in text_check:
                raise ValueError(f"AI result contains prohibited autonomous decision term '{term}'.")
