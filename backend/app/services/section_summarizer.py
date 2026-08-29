"""Section Summarizer Service.

Provides deterministic, rule-based text summarization for primary UI display without using LLM/AI inference.
Selects key topic sentences and bullet points while preserving complete original text internally.
"""

import re
import unicodedata


def generate_section_summary(key: str, text: str, max_sentences: int = 4, max_bullets: int = 5) -> str:
    """Generate a concise, structured display summary for a section from its raw source text."""
    if not text or text in ["NOT_REPORTED", "NOT_APPLICABLE", "EMPTY", "EXTRACTION_FAILED"]:
        return text or "NOT_REPORTED"

    norm_text = unicodedata.normalize("NFKC", text).strip()
    lines = [line.strip() for line in norm_text.split("\n") if line.strip()]

    # 1. Check if section contains explicit list items / bullet points
    bullet_items: list[str] = []
    for line in lines:
        if re.match(r"^(?:[•\-\*]|(?:\d+|[a-z]|[ivx]+)[\.\)]|\([0-9a-z]+\))\s+", line, re.IGNORECASE):
            clean_item = re.sub(r"^(?:[•\-\*]|(?:\d+|[a-z]|[ivx]+)[\.\)]|\([0-9a-z]+\))\s+", "", line).strip()
            if len(clean_item) > 10:
                bullet_items.append(clean_item)

    if bullet_items and len(bullet_items) >= 2:
        selected_bullets = bullet_items[:max_bullets]
        return "\n".join([f"• {b}" for b in selected_bullets])

    # 2. Key Tools / Techniques extraction if key is tools_techniques
    if key in ["tools_techniques", "technology"]:
        terms = re.findall(
            r"\b(?:phytostabilization|phytoextraction|phytodegradation|rhizofiltration|microbe-assisted|biochar-assisted|lorawan|atex|tri-axial|transducer|telemetry|iot|thermal\s+imaging|gas\s+dispersion|biochar|soil\s+remediation|heavy\s+metals)\b",
            norm_text,
            re.IGNORECASE,
        )
        if terms:
            unique_terms = []
            for t in terms:
                title_t = t.capitalize()
                if title_t not in unique_terms:
                    unique_terms.append(title_t)
            if len(unique_terms) >= 2:
                return "\n".join([f"• {t}" for t in unique_terms[:max_bullets]])

    # 3. Sentence-based summarization for prose paragraphs
    sentences = re.split(r"(?<=[.!?])\s+", norm_text)
    clean_sentences = [s.strip() for s in sentences if len(s.strip()) > 20 and not re.search(r"^(?:Vol\.|Figure|Fig\.|Table|\d+\s+\d+)", s)]

    if not clean_sentences:
        return norm_text[:350] + ("..." if len(norm_text) > 350 else "")

    if len(clean_sentences) <= max_sentences:
        summary_str = " ".join(clean_sentences)
    else:
        # Pick lead sentence + key method/findings sentences
        selected = [clean_sentences[0]]
        for s in clean_sentences[1:]:
            if len(selected) >= max_sentences:
                break
            if re.search(r"\b(?:study|method|results|findings|aim|objective|data|analyzed|demonstrate|show|conclude|limitations|framework)\b", s, re.IGNORECASE):
                if s not in selected:
                    selected.append(s)

        if len(selected) < min(2, len(clean_sentences)):
            selected = clean_sentences[:max_sentences]

        summary_str = " ".join(selected)

    if len(summary_str) > 500:
        summary_str = summary_str[:497] + "..."

    return summary_str
