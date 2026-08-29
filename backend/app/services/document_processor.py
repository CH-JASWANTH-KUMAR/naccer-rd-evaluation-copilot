import os
import re
from pathlib import Path

import pypdf
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.repositories.documents import DocumentRepository
from app.repositories.proposals import ProposalRepository

STORAGE_DIR = Path(__file__).resolve().parent.parent.parent / "storage" / "documents"
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB limit

SECTION_PATTERNS = [
    ("TITLE", r"^(?:\d+\.\s*)?(?:project|proposal)\s+title|^(?:title)\s*:?$", "Title"),
    (
        "PROBLEM_STATEMENT",
        r"^(?:\d+\.\s*)?(?:background\s+and\s+)?problem\s+statement|^statement\s+of\s+(?:the\s+)?problem",
        "Problem Statement",
    ),
    ("OBJECTIVES", r"^(?:\d+\.\s*)?(?:research\s+|specific\s+|project\s+)?objectives", "Objectives"),
    (
        "LITERATURE_REVIEW",
        r"^(?:\d+\.\s*)?(?:literature\s+review|review\s+of\s+literature|prior\s+work)",
        "Literature Review",
    ),
    ("TECHNOLOGY", r"^(?:\d+\.\s*)?(?:technology\s+and\s+infrastructure|technology|hardware\s+and\s+software)", "Technology & Infrastructure"),
    ("METHODOLOGY", r"^(?:\d+\.\s*)?(?:proposed\s+)?methodology|technical\s+approach", "Methodology"),
    ("VALIDATION_PLAN", r"^(?:\d+\.\s*)?(?:experimental\s+)?validation\s+plan|testing\s+plan", "Experimental Validation Plan"),
    (
        "EXPECTED_OUTCOMES",
        r"^(?:\d+\.\s*)?(?:expected\s+)?outcomes(?:\s+and\s+deliverables)?|expected\s+deliverables|expected\s+results",
        "Expected Outcomes",
    ),
    ("BUDGET", r"^(?:\d+\.\s*)?(?:project\s+budget|estimated\s+budget|project\s+cost|financial\s+breakdown)", "Budget"),
    ("RISK_ANALYSIS", r"^(?:\d+\.\s*)?(?:risk\s+analysis|risk\s+assessment\s+and\s+mitigation)", "Risk Analysis"),
    ("MANPOWER", r"^(?:\d+\.\s*)?(?:team\s+and\s+institutional\s+capability|manpower|project\s+team|personnel)", "Team Capability"),
    ("REFERENCES", r"^(?:\d+\.\s*)?(?:references|citations|bibliography)", "References"),
]


class DocumentProcessingService:
    def __init__(self, db: Session):
        self.db = db
        self.doc_repo = DocumentRepository(db)
        self.prop_repo = ProposalRepository(db)

    def upload_and_process_pdf(self, proposal_id: str, file: UploadFile):
        # 1. Validate Proposal Exists
        proposal = self.prop_repo.get_by_id(proposal_id)
        if not proposal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Proposal with ID '{proposal_id}' does not exist.",
            )

        # 2. Validate File Format & Extension
        filename = file.filename or "uploaded_document.pdf"
        if not filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF documents (.pdf) are supported for processing.",
            )

        if file.content_type and file.content_type not in ["application/pdf", "application/x-pdf", "octet-stream"]:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported media type '{file.content_type}'. Must be application/pdf.",
            )

        # 3. Read File Bytes & Validate Size
        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()
        file.file.seek(0)

        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty (0 bytes).",
            )

        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed limit of {MAX_FILE_SIZE // (1024 * 1024)}MB.",
            )

        # 4. Save File to Storage Directory
        STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        sanitized_name = re.sub(r"[^\w\.\-]", "_", filename)
        doc_record = self.doc_repo.create_document(
            proposal_id=proposal_id,
            filename=filename,
            file_type="application/pdf",
            file_size=file_size,
            storage_path="",  # Updated after creation with ID
        )

        storage_path = STORAGE_DIR / f"{doc_record.id}_{sanitized_name}"
        with open(storage_path, "wb") as f:
            f.write(file.file.read())

        doc_record.storage_path = str(storage_path)
        self.db.commit()

        # 5. Process PDF
        self.doc_repo.update_status(doc_record.id, "PROCESSING")

        try:
            reader = pypdf.PdfReader(storage_path)
            total_pages = len(reader.pages)

            if total_pages == 0:
                self.doc_repo.update_status(doc_record.id, "FAILED", "PDF file contains 0 pages or is corrupted.")
                return doc_record

            # Extract page text
            extracted_pages: list[tuple[int, str]] = []
            total_text_length = 0

            for page_idx, page in enumerate(reader.pages, start=1):
                raw_text = page.extract_text() or ""
                clean_text = raw_text.strip()
                extracted_pages.append((page_idx, clean_text))
                total_text_length += len(clean_text)

                # Persist DocumentPage record
                self.doc_repo.add_page(doc_record.id, page_idx, clean_text)

            # Check if PDF is scanned / image-only
            if total_text_length < 50:
                self.doc_repo.update_status(
                    doc_record.id,
                    "FAILED",
                    "Scanned / image-only PDFs are not supported yet (OCR will be added in Phase P0.2+ / P0.3).",
                )
                return doc_record

            # Detect Proposal Sections
            sections_found = self._detect_sections(proposal_id, doc_record.id, extracted_pages)

            # Safely update structured proposal fields (only if currently empty)
            self._update_proposal_fields_safely(proposal, sections_found)

            self.doc_repo.update_status(doc_record.id, "PROCESSED")
            return self.doc_repo.get_by_id(doc_record.id)

        except Exception as e:
            error_msg = f"Failed to extract PDF text: {str(e)}"
            self.doc_repo.update_status(doc_record.id, "FAILED", error_msg)
            return self.doc_repo.get_by_id(doc_record.id)

    def _detect_sections(self, proposal_id: str, document_id: str, pages: list[tuple[int, str]]) -> dict[str, str]:
        """Deterministic section detector using offset-based section boundary parser."""
        from app.services.proposal_section_parser import parse_proposal_sections

        parsed_data = parse_proposal_sections(pages)
        detected_sections: dict[str, str] = {}
        sec_dict = parsed_data["sections"]

        for key, s_res in sec_dict.items():
            sec_type_upper = key.upper()
            if s_res.status == "REPORTED":
                detected_sections[sec_type_upper] = s_res.content
                self.doc_repo.add_section(
                    proposal_id=proposal_id,
                    document_id=document_id,
                    section_type=sec_type_upper,
                    section_title=s_res.section_title,
                    content=s_res.content,
                    start_page=s_res.source_page_start,
                    end_page=s_res.source_page_end,
                    confidence=1.0 if s_res.extraction_confidence == "HIGH" else 0.5,
                )
            else:
                detected_sections[sec_type_upper] = "NOT_REPORTED"

        return detected_sections

    def _update_proposal_fields_safely(self, proposal, sections: dict[str, str]):
        """Populate proposal fields ONLY if they are currently empty, preserving user edits."""
        if not proposal.problem_statement and "PROBLEM_STATEMENT" in sections:
            proposal.problem_statement = sections["PROBLEM_STATEMENT"][:2000]

        if not proposal.objectives and "OBJECTIVES" in sections:
            proposal.objectives = sections["OBJECTIVES"][:2000]

        if not proposal.methodology and "METHODOLOGY" in sections:
            proposal.methodology = sections["METHODOLOGY"][:2000]

        if not proposal.literature_review and "LITERATURE_REVIEW" in sections:
            proposal.literature_review = sections["LITERATURE_REVIEW"][:2000]

        if not proposal.expected_outcomes and "EXPECTED_OUTCOMES" in sections:
            proposal.expected_outcomes = sections["EXPECTED_OUTCOMES"][:2000]

        if not proposal.timeline and "WORK_PLAN" in sections:
            proposal.timeline = sections["WORK_PLAN"][:2000]

        self.db.commit()
