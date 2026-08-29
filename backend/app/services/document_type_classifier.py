"""Document Type Classifier Service.

Provides conservative, deterministic classification of PDF documents into:
- R&D_PROPOSAL
- RESEARCH_PAPER
- UNKNOWN

Uses structural features, metadata patterns, and section headings without LLM/AI inference.
"""

import re
import unicodedata
from dataclasses import dataclass, field


@dataclass
class DocumentTypeResult:
    document_type: str  # R&D_PROPOSAL, RESEARCH_PAPER, UNKNOWN
    document_type_confidence: str  # HIGH, MEDIUM, LOW
    document_type_reasons: list[str] = field(default_factory=list)


def normalize_text(text: str) -> str:
    if not text:
        return ""
    norm = unicodedata.normalize("NFKC", text)
    norm = norm.replace("\xa0", " ").replace("\xad", "")
    norm = re.sub(r"[ \t]+", " ", norm)
    return norm


def classify_document(pages_text: list[tuple[int, str]]) -> DocumentTypeResult:
    """Classify a document based on deterministic structural and metadata signals across its pages."""
    if not pages_text:
        return DocumentTypeResult(
            document_type="UNKNOWN",
            document_type_confidence="LOW",
            document_type_reasons=["Empty or unreadable document text."],
        )

    # 1. Prepare text slices
    first_two_pages = "\n".join([normalize_text(txt or "") for p_num, txt in pages_text if p_num <= 2])
    full_text = "\n".join([normalize_text(txt or "") for _, txt in pages_text])

    paper_reasons: list[str] = []
    proposal_reasons: list[str] = []

    # 2. Check RESEARCH_PAPER signals
    if re.search(r"^\s*abstract\b(?:\s*:)?", first_two_pages, re.IGNORECASE | re.MULTILINE):
        paper_reasons.append("Detected Abstract section/header")

    if re.search(r"^\s*key\s*words\b|keywords\s*:", first_two_pages, re.IGNORECASE | re.MULTILINE):
        paper_reasons.append("Detected Keywords section/header")

    if re.search(r"received\s*:\s*\d|accepted\s*:\s*\d|published\s*:\s*\d", first_two_pages, re.IGNORECASE):
        paper_reasons.append("Detected Received/Accepted submission metadata")

    if re.search(r"doi\s*:\s*10\.\d{4,9}/|https?://doi\.org/10\.\d{4,9}/", full_text, re.IGNORECASE):
        paper_reasons.append("Detected DOI identifier metadata")

    if re.search(
        r"\b(?:springer|elsevier|ieee|sage|wiley|nature|taylor\s+&\s+francis|oxford\s+university\s+press|mcgraw-hill)\b",
        first_two_pages,
        re.IGNORECASE,
    ):
        paper_reasons.append("Detected academic publisher / journal metadata")

    if re.search(r"\b(?:issn|isbn)\b\s*[:\s]*[\d\-]+", first_two_pages, re.IGNORECASE):
        paper_reasons.append("Detected ISSN/ISBN catalog metadata")

    if re.search(r"^\s*(?:methods\s+and\s+data|results|discussion|conclusion|references)\s*:?\s*$", full_text, re.IGNORECASE | re.MULTILINE):
        paper_reasons.append("Detected academic paper sections (Methods and Data / Results / Discussion / References)")

    # 3. Check R&D_PROPOSAL signals
    if re.search(r"^(?:\d+[\.\)]\s*)?(?:project|proposal)\s+title\s*:", first_two_pages, re.IGNORECASE | re.MULTILINE):
        proposal_reasons.append("Detected Project Title metadata label")

    if re.search(r"^(?:\d+[\.\)]\s*)?(?:project\s+|technical\s+)?objectives\s*:?\s*$", full_text, re.IGNORECASE | re.MULTILINE):
        proposal_reasons.append("Detected standalone Project Objectives section heading")

    if re.search(r"^(?:\d+[\.\)]\s*)?technology\s+(?:and|&)\s+infrastructure\s*:?\s*$", full_text, re.IGNORECASE | re.MULTILINE):
        proposal_reasons.append("Detected standalone Technology & Infrastructure section heading")

    if re.search(r"^(?:\d+[\.\)]\s*)?expected\s+outcomes(?:\s+(?:and|&)\s+deliverables)?\s*:?\s*$", full_text, re.IGNORECASE | re.MULTILINE):
        proposal_reasons.append("Detected standalone Expected Outcomes section heading")

    if re.search(r"(?:total\s+requested\s+budget|total\s+budget|estimated\s+cost|proposed\s+budget)\s*:\s*Rs", full_text, re.IGNORECASE):
        proposal_reasons.append("Detected Total Requested Budget currency breakdown")

    if re.search(r"^(?:principal\s+investigator|pi)\s*:\s*[A-Z]", first_two_pages, re.IGNORECASE | re.MULTILINE):
        proposal_reasons.append("Detected Principal Investigator metadata header")

    if re.search(r"\b(?:naccer|coal\s+india\s+limited|cil\s+r&d|ministry\s+of\s+coal|s&t\s+committee)\b", full_text, re.IGNORECASE):
        proposal_reasons.append("Detected NaCCER / Ministry of Coal R&D institutional provenance")

    paper_score = len(paper_reasons)
    proposal_score = len(proposal_reasons)

    # 4. Decision Logic
    if paper_score >= 2 and proposal_score == 0:
        return DocumentTypeResult(
            document_type="RESEARCH_PAPER",
            document_type_confidence="HIGH",
            document_type_reasons=paper_reasons,
        )

    if proposal_score >= 2 and paper_score == 0:
        return DocumentTypeResult(
            document_type="R&D_PROPOSAL",
            document_type_confidence="HIGH",
            document_type_reasons=proposal_reasons,
        )

    if paper_score > proposal_score + 1:
        return DocumentTypeResult(
            document_type="RESEARCH_PAPER",
            document_type_confidence="MEDIUM",
            document_type_reasons=paper_reasons + [f"Paper score ({paper_score}) exceeds proposal score ({proposal_score})."],
        )

    if proposal_score > paper_score + 1:
        return DocumentTypeResult(
            document_type="R&D_PROPOSAL",
            document_type_confidence="MEDIUM",
            document_type_reasons=proposal_reasons + [f"Proposal score ({proposal_score}) exceeds paper score ({paper_score})."],
        )

    # Ambiguous or unknown
    combined_reasons = (
        paper_reasons + proposal_reasons
        if (paper_reasons or proposal_reasons)
        else ["No strong research paper or R&D proposal structural signals detected."]
    )
    return DocumentTypeResult(
        document_type="UNKNOWN",
        document_type_confidence="LOW",
        document_type_reasons=combined_reasons,
    )
