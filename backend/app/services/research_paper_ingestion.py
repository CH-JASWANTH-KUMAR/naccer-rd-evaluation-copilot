import hashlib
import json
import re
from pathlib import Path

import pypdf
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.repositories.research_papers import ResearchPaperRepository
from app.schemas.research_paper import ResearchPaperCreate, ResearchPaperRead

RESEARCH_STORAGE_DIR = Path(__file__).resolve().parent.parent.parent / "storage" / "research_papers"

SECTION_PATTERNS = [
    ("Abstract", r"(?:\bAbstract\b)"),
    ("Introduction", r"(?:\b(?:1|2|I|II)\.?\s*Introduction\b|\bIntroduction\b)"),
    ("Related Work", r"(?:\bRelated\s+Work\b|\bLiterature\s+Review\b)"),
    ("Methodology", r"(?:\bMethodology\b|\bProposed\s+Method\b|\bMethods\b|\bSystem\s+Architecture\b)"),
    ("Materials", r"(?:\bMaterials\s+and\s+Methods\b|\bMaterials\b)"),
    ("Experimental Setup", r"(?:\bExperimental\s+Setup\b|\bExperiments\b|\bDataset\b)"),
    ("Results", r"(?:\bResults\b|\bExperimental\s+Results\b)"),
    ("Discussion", r"(?:\bDiscussion\b)"),
    ("Conclusion", r"(?:\bConclusion\b|\bConclusions\b)"),
    ("References", r"(?:\bReferences\b|\bBibliography\b)"),
]


class ResearchPaperIngestionService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ResearchPaperRepository(db)

    def ingest_paper_pdf(
        self,
        file: UploadFile,
        research_domain: str = "Coal Mining & Automation",
    ) -> ResearchPaperRead:
        filename = file.filename or "research_paper.pdf"
        if not filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF documents (.pdf) are supported for research paper ingestion.",
            )

        content = file.file.read()
        if len(content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty.",
            )

        file_hash = hashlib.sha256(content).hexdigest()

        # Check for Duplicate Paper by File Hash
        existing = self.repo.get_by_hash(file_hash)
        if existing:
            return ResearchPaperRead.model_validate(existing)

        # Store locally in storage/research_papers
        RESEARCH_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        storage_path = RESEARCH_STORAGE_DIR / f"{file_hash[:12]}_{filename}"
        with open(storage_path, "wb") as f:
            f.write(content)

        # Read PDF using pypdf
        try:
            reader = pypdf.PdfReader(storage_path)
            page_count = len(reader.pages)
        except Exception as err:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Unable to parse PDF document: {err}",
            ) from err

        pages_extracted: list[tuple[int, str, list[str]]] = []
        full_text_parts: list[str] = []

        for p_idx, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            sections = self._detect_sections_in_text(text)
            pages_extracted.append((p_idx, text, sections))
            full_text_parts.append(f"--- PAGE {p_idx} ---\n{text}")

        combined_raw_text = "\n\n".join(full_text_parts)

        # Extract Metadata conservatively
        title = self._extract_title(pages_extracted, filename)
        authors = self._extract_authors(pages_extracted)
        abstract = self._extract_abstract(pages_extracted)
        year = self._extract_year(combined_raw_text)
        doi = self._extract_doi(combined_raw_text)
        journal = self._extract_journal(combined_raw_text)
        keywords = self._extract_keywords(combined_raw_text)

        paper_create = ResearchPaperCreate(
            title=title,
            authors=authors,
            abstract=abstract,
            publication_year=year,
            journal_or_conference=journal,
            doi=doi,
            research_domain=research_domain,
            keywords=keywords,
            source_filename=filename,
            source_document_type="PDF",
            page_count=page_count,
            file_hash=file_hash,
            storage_path=str(storage_path),
            extraction_status="COMPLETED",
            raw_text=combined_raw_text,
        )

        paper = self.repo.create(paper_create)

        # Add page records
        for p_num, p_text, p_secs in pages_extracted:
            sec_json = json.dumps(p_secs) if p_secs else None
            self.repo.add_page(paper.id, p_num, p_text, sec_json)

        refreshed = self.repo.get_by_id(paper.id)
        return ResearchPaperRead.model_validate(refreshed)

    def _detect_sections_in_text(self, text: str) -> list[str]:
        detected = []
        for name, pattern in SECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
                detected.append(name)
        return detected

    def _extract_title(self, pages: list[tuple[int, str, list[str]]], filename: str) -> str:
        if not pages:
            return filename.replace(".pdf", "")
        p1_text = pages[0][1]
        lines = [line.strip() for line in p1_text.split("\n") if line.strip()]
        for line in lines:
            if len(line) > 15 and not line.startswith("---") and not line.lower().startswith("doi"):
                return line[:500]
        return filename.replace(".pdf", "")

    def _extract_authors(self, pages: list[tuple[int, str, list[str]]]) -> str | None:
        if not pages:
            return None
        p1_text = pages[0][1]
        lines = [line.strip() for line in p1_text.split("\n") if line.strip()]
        if len(lines) >= 2:
            second_line = lines[1]
            if any(char.isdigit() for char in second_line) or "@" in second_line or "university" in second_line.lower() or "institute" in second_line.lower():
                return second_line[:500]
            if len(second_line) > 5 and len(lines) >= 3:
                return f"{second_line}, {lines[2]}"[:500]
        return None

    def _extract_abstract(self, pages: list[tuple[int, str, list[str]]]) -> str | None:
        for _, text, _ in pages[:2]:
            m = re.search(r"Abstract[:\s\n]+(.*?)(?=\n\s*(?:Keywords|1\.|Introduction)|$)", text, re.IGNORECASE | re.DOTALL)
            if m:
                clean = m.group(1).strip().replace("\n", " ")
                return clean[:2000]
        return None

    def _extract_year(self, text: str) -> int | None:
        m = re.findall(r"\b(19\d{2}|20\d{2})\b", text)
        if m:
            # Pick first 20XX year or reasonable publication year
            years = [int(y) for y in m if 1990 <= int(y) <= 2026]
            if years:
                return years[0]
        return None

    def _extract_doi(self, text: str) -> str | None:
        m = re.search(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b", text, re.IGNORECASE)
        if m:
            return m.group(0)
        return None

    def _extract_journal(self, text: str) -> str | None:
        journals = ["IEEE", "ACM", "Elsevier", "Springer", "MDPI", "Journal of Mining", "Mining Technology", "Sensors"]
        for j in journals:
            if j.lower() in text.lower():
                return f"{j} Publications"
        return None

    def _extract_keywords(self, text: str) -> str | None:
        m = re.search(r"Keywords[:\s\n]+([^\n\.]+)", text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
        return None
