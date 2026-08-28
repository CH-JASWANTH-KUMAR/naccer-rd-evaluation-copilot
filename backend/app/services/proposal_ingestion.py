import hashlib
import re
from pathlib import Path

import pypdf
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_page import DocumentPage
from app.models.proposal import Proposal
from app.models.proposal_section import ProposalSection
from app.repositories.institutions import InstitutionRepository
from app.repositories.proposals import ProposalRepository
from app.schemas.proposal import ProposalRead
from app.services.financial_compliance import FinancialComplianceService
from app.services.proposal_completeness import ProposalCompletenessService

PROPOSAL_STORAGE_DIR = Path(__file__).resolve().parent.parent.parent / "storage" / "documents"


class ProposalIngestionService:
    def __init__(self, db: Session):
        self.db = db
        self.prop_repo = ProposalRepository(db)
        self.inst_repo = InstitutionRepository(db)

    def ingest_proposal_pdf(
        self,
        file: UploadFile,
        institution_id: str | None = None,
        principal_investigator: str = "Dr. R. K. Verma",
        domain: str = "Mine Safety & Ventilation",
    ) -> ProposalRead:
        filename = file.filename or "proposal.pdf"
        if not filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF documents (.pdf) are supported for proposal intake.",
            )

        # 1. Read file bytes & compute SHA-256 hash
        content = file.file.read()
        file_size = len(content)
        file_hash = hashlib.sha256(content).hexdigest()

        # Get or create institution
        inst = None
        if institution_id:
            inst = self.inst_repo.get_by_id(institution_id)
        if not inst:
            inst_list = self.inst_repo.get_all()
            if inst_list:
                inst = inst_list[0]
            else:
                from app.schemas.institution import InstitutionCreate

                inst = self.inst_repo.create(
                    InstitutionCreate(
                        name="CSIR-CIMFR Dhanbad",
                        code="CSIR-CIMFR-AUTO",
                        type="RESEARCH_INSTITUTE",
                        location="Dhanbad, Jharkhand",
                    )
                )

        # 2. Check for Duplicate Document Hash
        existing_doc = self.db.query(Document).filter(Document.document_hash == file_hash).first()
        if existing_doc:
            existing_prop = self.prop_repo.get_by_id(existing_doc.proposal_id)
            if existing_prop:
                return ProposalRead.model_validate(existing_prop)

        # 3. Create Initial Proposal Record
        proposal = Proposal(
            title=f"Uploaded Proposal: {filename}",
            institution_id=inst.id,
            principal_investigator=principal_investigator,
            domain=domain,
            status="UNDER_REVIEW",
            processing_status="EXTRACTING",
        )
        self.db.add(proposal)
        self.db.commit()
        self.db.refresh(proposal)

        # 4. Save PDF locally & Create Document Entity
        PROPOSAL_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        storage_path = PROPOSAL_STORAGE_DIR / f"{proposal.id}_{filename}"
        with open(storage_path, "wb") as f:
            f.write(content)

        doc = Document(
            proposal_id=proposal.id,
            filename=filename,
            file_type="application/pdf",
            file_size=file_size,
            document_hash=file_hash,
            storage_path=str(storage_path),
            processing_status="PROCESSING",
        )
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)

        # 5. Extract Pages via pypdf
        reader = pypdf.PdfReader(storage_path)
        page_count = len(reader.pages)
        doc.page_count = page_count

        pages_text: list[tuple[int, str]] = []
        for idx, page in enumerate(reader.pages, start=1):
            txt = page.extract_text() or ""
            doc_page = DocumentPage(
                document_id=doc.id,
                page_number=idx,
                text=txt,
            )
            self.db.add(doc_page)
            pages_text.append((idx, txt))

        self.db.commit()

        # 6. Section Parsing & Field Extraction
        extracted_fields, sections = self._extract_proposal_sections(pages_text, doc.id, proposal.id)

        # Populate Proposal Fields
        if extracted_fields.get("title"):
            proposal.title = extracted_fields["title"][:500]
        if extracted_fields.get("problem_statement"):
            proposal.problem_statement = extracted_fields["problem_statement"]
        if extracted_fields.get("objectives"):
            proposal.objectives = extracted_fields["objectives"]
        if extracted_fields.get("methodology"):
            proposal.methodology = extracted_fields["methodology"]
        if extracted_fields.get("technology"):
            proposal.technology = extracted_fields["technology"]
        if extracted_fields.get("expected_outcomes"):
            proposal.expected_outcomes = extracted_fields["expected_outcomes"]
        if extracted_fields.get("budget_total"):
            proposal.budget_total = extracted_fields["budget_total"]
        if extracted_fields.get("duration_months"):
            proposal.duration_months = extracted_fields["duration_months"]

        # Store Sections
        for sec in sections:
            self.db.add(sec)

        doc.processing_status = "PROCESSED"
        self.db.commit()

        # 7. Run Completeness & Compliance Scrutiny Engines
        comp_report = ProposalCompletenessService.evaluate_completeness(proposal)
        proposal.completeness_status = comp_report.status

        fin_report = FinancialComplianceService.evaluate_financial_compliance(proposal)
        proposal.compliance_status = fin_report.status

        proposal.processing_status = "READY_FOR_REVIEW" if comp_report.status == "COMPLETE" else "INCOMPLETE"
        self.db.commit()
        self.db.refresh(proposal)

        return ProposalRead.model_validate(proposal)

    def reprocess_proposal(self, proposal_id: str) -> ProposalRead:
        proposal = self.prop_repo.get_by_id(proposal_id)
        if not proposal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Proposal with ID '{proposal_id}' not found.",
            )

        comp_report = ProposalCompletenessService.evaluate_completeness(proposal)
        proposal.completeness_status = comp_report.status

        fin_report = FinancialComplianceService.evaluate_financial_compliance(proposal)
        proposal.compliance_status = fin_report.status

        proposal.processing_status = "READY_FOR_REVIEW" if comp_report.status == "COMPLETE" else "INCOMPLETE"
        self.db.commit()
        self.db.refresh(proposal)

        return ProposalRead.model_validate(proposal)

    def _extract_proposal_sections(
        self, pages_text: list[tuple[int, str]], document_id: str, proposal_id: str
    ) -> tuple[dict, list[ProposalSection]]:
        full_text = "\n".join([f"--- PAGE {p_num} ---\n{text}" for p_num, text in pages_text])
        extracted: dict = {}
        sections: list[ProposalSection] = []

        # 1. Extract Title
        title_match = re.search(
            r"(?:Title|Project Title|Name of Project)\s*:?\s*([^\n]+(?:\n[^\n]+){0,2})", full_text, re.IGNORECASE
        )
        if title_match:
            extracted["title"] = title_match.group(1).replace("\n", " ").strip()

        # 2. Extract Objectives
        obj_match = re.search(
            r"(?:Objectives|Project Objectives|Technical Objectives)\s*:?\s*([^\n]+(?:\n[^\n]+){1,10})",
            full_text,
            re.IGNORECASE,
        )
        if obj_match:
            extracted["objectives"] = obj_match.group(1).strip()
            sections.append(
                ProposalSection(
                    proposal_id=proposal_id,
                    document_id=document_id,
                    section_type="Objectives",
                    section_title="Objectives",
                    start_page=1,
                    end_page=1,
                    content=extracted["objectives"],
                )
            )

        # 3. Extract Methodology
        meth_match = re.search(
            r"(?:Methodology|Proposed Methodology|Technical Approach|Method)\s*:?\s*([^\n]+(?:\n[^\n]+){1,10})",
            full_text,
            re.IGNORECASE,
        )
        if meth_match:
            extracted["methodology"] = meth_match.group(1).strip()
            sections.append(
                ProposalSection(
                    proposal_id=proposal_id,
                    document_id=document_id,
                    section_type="Methodology",
                    section_title="Methodology",
                    start_page=1,
                    end_page=2,
                    content=extracted["methodology"],
                )
            )

        # 4. Extract Technology
        tech_match = re.search(
            r"(?:Technology|Technologies|Tools & Equipment|Hardware & Software)\s*:?\s*([^\n]+)",
            full_text,
            re.IGNORECASE,
        )
        if tech_match:
            extracted["technology"] = tech_match.group(1).strip()

        # 5. Extract Problem Statement
        prob_match = re.search(
            r"(?:Problem Statement|Background|Introduction|Research Gap)\s*:?\s*([^\n]+(?:\n[^\n]+){1,6})",
            full_text,
            re.IGNORECASE,
        )
        if prob_match:
            extracted["problem_statement"] = prob_match.group(1).strip()

        # 6. Extract Expected Outcomes
        out_match = re.search(
            r"(?:Expected Outcomes|Deliverables|Expected Deliverables|Results)\s*:?\s*([^\n]+(?:\n[^\n]+){1,6})",
            full_text,
            re.IGNORECASE,
        )
        if out_match:
            extracted["expected_outcomes"] = out_match.group(1).strip()

        # 7. Extract Budget
        budget_match = re.search(
            r"(?:Total Budget|Estimated Cost|Project Cost|Total Outlay|Proposed Budget)\s*:?\s*(Rs\.?\s*[\d\.\,]+\s*(?:Lakhs?|Crores?|INR)?)",
            full_text,
            re.IGNORECASE,
        )
        if budget_match:
            raw_b = budget_match.group(1).strip()
            extracted["budget_total"] = FinancialComplianceService._parse_currency(raw_b)

        return extracted, sections
