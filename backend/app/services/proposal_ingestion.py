import hashlib
import io
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
        title: str | None = None,
        institution_id: str | None = None,
        principal_investigator: str = "Dr. R. K. Verma",
        domain: str = "Mine Safety & Ventilation",
        budget_total: float | None = None,
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

        # 2. Extract Pages via pypdf to re-verify section extraction
        try:
            reader = pypdf.PdfReader(io.BytesIO(content))
            pages_text: list[tuple[int, str]] = []
            for p_idx, page in enumerate(reader.pages, start=1):
                txt = page.extract_text() or ""
                pages_text.append((p_idx, txt))
        except Exception:
            pages_text = []

        existing_doc = self.db.query(Document).filter(Document.document_hash == file_hash).first()
        if existing_doc:
            existing_prop = self.prop_repo.get_by_id(existing_doc.proposal_id)
            if existing_prop and pages_text:
                # 1. Invalidate stale pages and sections in DB
                self.db.query(DocumentPage).filter(DocumentPage.document_id == existing_doc.id).delete()
                self.db.query(ProposalSection).filter(ProposalSection.document_id == existing_doc.id).delete()
                self.db.commit()

                # 2. Save fresh pages
                for idx, txt in pages_text:
                    self.db.add(DocumentPage(document_id=existing_doc.id, page_number=idx, text=txt))
                self.db.commit()

                from app.services.document_type_classifier import classify_document
                doc_type_res = classify_document(pages_text)

                existing_doc.document_type = doc_type_res.document_type
                existing_doc.document_type_confidence = doc_type_res.document_type_confidence
                existing_doc.document_type_reasons = doc_type_res.document_type_reasons

                existing_prop.document_type = doc_type_res.document_type
                existing_prop.document_type_confidence = doc_type_res.document_type_confidence
                existing_prop.document_type_reasons = doc_type_res.document_type_reasons

                if doc_type_res.document_type == "RESEARCH_PAPER":
                    extracted_fields, sections = self._extract_paper_sections(pages_text, existing_doc.id, existing_prop.id)
                else:
                    extracted_fields, sections = self._extract_proposal_sections(pages_text, existing_doc.id, existing_prop.id)

                for sec in sections:
                    self.db.add(sec)

                existing_prop.problem_statement = extracted_fields.get("problem_statement", "NOT_REPORTED")
                existing_prop.objectives = extracted_fields.get("objectives", "NOT_REPORTED")
                existing_prop.methodology = extracted_fields.get("methodology", "NOT_REPORTED")
                existing_prop.technology = extracted_fields.get("technology", "NOT_REPORTED")
                existing_prop.expected_outcomes = extracted_fields.get("expected_outcomes", "NOT_REPORTED")
                existing_prop.literature_review = extracted_fields.get("literature_review", "NOT_REPORTED")
                existing_prop.timeline = extracted_fields.get("timeline", "NOT_REPORTED")

                self.db.commit()
                self.db.refresh(existing_prop)

                from app.services.proposal_section_parser import parse_proposal_sections
                parsed = parse_proposal_sections(pages_text)
                struct_secs = self._build_structured_sections(parsed["sections"], doc_type_res.document_type, pages_text, existing_prop.id)

                res_read = ProposalRead.model_validate(existing_prop)
                res_read.structured_sections = struct_secs
                return res_read

        # 3. Create Initial Proposal Record
        initial_title = title.strip() if title and title.strip() else f"Uploaded Proposal: {filename}"
        proposal = Proposal(
            title=initial_title,
            institution_id=inst.id,
            principal_investigator=principal_investigator,
            domain=domain,
            budget_total=budget_total or 0.0,
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
        pages_text = []
        try:
            reader = pypdf.PdfReader(storage_path)
            page_count = len(reader.pages)
            doc.page_count = page_count

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
        except Exception as exc:
            doc.processing_status = "FAILED"
            doc.processing_error = f"Unable to parse PDF document: {exc}"
            self.db.commit()

        # 6. Document Type Classification
        from app.services.document_type_classifier import classify_document
        doc_type_res = classify_document(pages_text)

        doc.document_type = doc_type_res.document_type
        doc.document_type_confidence = doc_type_res.document_type_confidence
        doc.document_type_reasons = doc_type_res.document_type_reasons

        proposal.document_type = doc_type_res.document_type
        proposal.document_type_confidence = doc_type_res.document_type_confidence
        proposal.document_type_reasons = doc_type_res.document_type_reasons

        # 7. Section Parsing & Field Extraction according to Document Type
        if doc_type_res.document_type == "RESEARCH_PAPER":
            extracted_fields, sections = self._extract_paper_sections(pages_text, doc.id, proposal.id)
        else:
            extracted_fields, sections = self._extract_proposal_sections(pages_text, doc.id, proposal.id)

        # Populate Proposal Fields (prioritizing explicit user input if provided)
        if not title and extracted_fields.get("title"):
            proposal.title = extracted_fields["title"][:500]
        if extracted_fields.get("principal_investigator"):
            proposal.extracted_principal_investigator = extracted_fields["principal_investigator"]
        if extracted_fields.get("raw_budget_text"):
            proposal.raw_budget_text = extracted_fields["raw_budget_text"]
        if (proposal.budget_total is None or proposal.budget_total <= 0) and extracted_fields.get("budget_total"):
            proposal.budget_total = extracted_fields["budget_total"]

        proposal.problem_statement = extracted_fields.get("problem_statement", "NOT_REPORTED")
        proposal.objectives = extracted_fields.get("objectives", "NOT_REPORTED")
        proposal.methodology = extracted_fields.get("methodology", "NOT_REPORTED")
        proposal.technology = extracted_fields.get("technology", "NOT_REPORTED")
        proposal.expected_outcomes = extracted_fields.get("expected_outcomes", "NOT_REPORTED")
        proposal.literature_review = extracted_fields.get("literature_review", "NOT_REPORTED")
        proposal.timeline = extracted_fields.get("timeline", "NOT_REPORTED")

        if extracted_fields.get("duration_months"):
            proposal.duration_months = extracted_fields["duration_months"]

        # Store Sections
        for sec in sections:
            self.db.add(sec)

        doc.processing_status = "PROCESSED"
        self.db.commit()

        # 8. Run Completeness & Compliance Scrutiny Engines
        comp_report = ProposalCompletenessService.evaluate_completeness(proposal)
        proposal.completeness_status = comp_report.status

        fin_report = FinancialComplianceService.evaluate_financial_compliance(proposal)
        proposal.compliance_status = fin_report.status

        proposal.processing_status = "READY_FOR_REVIEW" if comp_report.status == "COMPLETE" else "INCOMPLETE"
        self.db.commit()
        self.db.refresh(proposal)

        from app.services.proposal_section_parser import parse_proposal_sections
        parsed_data = parse_proposal_sections(pages_text)
        struct_secs = self._build_structured_sections(parsed_data["sections"], doc_type_res.document_type, pages_text, proposal.id)

        res_read = ProposalRead.model_validate(proposal)
        res_read.structured_sections = struct_secs
        return res_read

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
        from app.services.proposal_section_parser import parse_proposal_sections

        parsed_data = parse_proposal_sections(pages_text)
        extracted: dict = parsed_data["metadata"]
        sec_dict = parsed_data["sections"]
        sections: list[ProposalSection] = []

        for key, s_res in sec_dict.items():
            content_val = s_res.content if s_res.status in ["REPORTED", "EMPTY"] else "NOT_REPORTED"
            extracted[key] = content_val

            if s_res.status == "REPORTED":
                sections.append(
                    ProposalSection(
                        proposal_id=proposal_id,
                        document_id=document_id,
                        section_type=s_res.section_type,
                        section_title=s_res.section_title,
                        start_page=s_res.source_page_start,
                        end_page=s_res.source_page_end,
                        content=s_res.content,
                        confidence=1.0 if s_res.extraction_confidence == "HIGH" else 0.5,
                    )
                )

        if extracted.get("raw_budget_text") and not extracted.get("budget_total"):
            extracted["budget_total"] = FinancialComplianceService._parse_currency(extracted["raw_budget_text"])

        return extracted, sections

    def _extract_paper_sections(
        self, pages_text: list[tuple[int, str]], document_id: str, proposal_id: str
    ) -> tuple[dict, list[ProposalSection]]:
        """Extract paper-native sections for RESEARCH_PAPER documents without forcing proposal-specific fields."""
        from app.services.proposal_section_parser import parse_proposal_sections

        parsed_data = parse_proposal_sections(pages_text)
        sec_dict = parsed_data["sections"]
        sections: list[ProposalSection] = []

        extracted: dict = {
            "title": parsed_data["metadata"].get("title", ""),
            "principal_investigator": parsed_data["metadata"].get("principal_investigator", ""),
            "problem_statement": sec_dict["problem_statement"].content if sec_dict["problem_statement"].status == "REPORTED" else "NOT_APPLICABLE",
            "objectives": "NOT_APPLICABLE",
            "technology": "NOT_APPLICABLE",
            "methodology": sec_dict["methodology"].content if sec_dict["methodology"].status == "REPORTED" else "NOT_APPLICABLE",
            "expected_outcomes": "NOT_APPLICABLE",
            "literature_review": sec_dict["literature_review"].content if sec_dict["literature_review"].status == "REPORTED" else "NOT_APPLICABLE",
            "timeline": "NOT_APPLICABLE",
            "raw_budget_text": "NOT_APPLICABLE",
            "budget_total": 0.0,
        }

        # Store native paper sections for auditability
        for key in ["problem_statement", "literature_review", "methodology", "references"]:
            s_res = sec_dict.get(key)
            if s_res and s_res.status == "REPORTED":
                sections.append(
                    ProposalSection(
                        proposal_id=proposal_id,
                        document_id=document_id,
                        section_type=s_res.section_type,
                        section_title=s_res.section_title,
                        start_page=s_res.source_page_start,
                        end_page=s_res.source_page_end,
                        content=s_res.content,
                        confidence=1.0,
                    )
                )

        return extracted, sections

    def _build_structured_sections(
        self, sec_dict: dict, document_type: str, pages_text: list[tuple[int, str]] | None = None, proposal_id: str = ""
    ) -> list:
        from app.schemas.document import StructuredSectionRead
        from app.services.section_summarizer import generate_section_summary

        res: list[StructuredSectionRead] = []
        prop_prefix = proposal_id[:6] if proposal_id else "000"

        all_text = " ".join([getattr(s, "content", "") for s in sec_dict.values() if hasattr(s, "content")]).lower()
        is_review_paper = any(
            term in all_text for term in ["systematic review", "scoping review", "literature review", "review article", "synthesizes peer-reviewed", "review paper"]
        ) or any(k in sec_dict for k in ["review_purpose", "review_methodology", "evidence_base", "future_directions"])

        if document_type == "RESEARCH_PAPER":
            if is_review_paper:
                paper_order = [
                    ("abstract", "Abstract"),
                    ("problem_statement", "Research Problem / Motivation"),
                    ("research_gap", "Research Gap"),
                    ("review_purpose", "Review Purpose / Scope"),
                    ("literature_review", "Literature / Background"),
                    ("review_methodology", "Review Methodology / Search Strategy"),
                    ("evidence_base", "Evidence Base / Techniques"),
                    ("key_findings", "Key Findings / Synthesis"),
                    ("limitations", "Study Limitations"),
                    ("future_directions", "Future Directions & Recommendations"),
                    ("references", "References & Citations"),
                ]
            else:
                paper_order = [
                    ("abstract", "Abstract"),
                    ("problem_statement", "Research Problem / Motivation"),
                    ("research_gap", "Research Gap / Need"),
                    ("objectives", "Study Purpose / Research Questions"),
                    ("literature_review", "Literature Review / Background"),
                    ("methodology", "Methodology / Study Design"),
                    ("tools_techniques", "Tools / Techniques / Approaches"),
                    ("results", "Results / Key Findings"),
                    ("discussion", "Discussion & Implications"),
                    ("limitations", "Study Limitations"),
                    ("future_work", "Future Work & Recommendations"),
                    ("references", "References & Citations"),
                ]

            ev_counter = 1
            for tuple_item in paper_order:
                key = tuple_item[0]
                display_title = tuple_item[1]

                s_res = sec_dict.get(key)
                if not s_res or s_res.status != "REPORTED":
                    fallback_key = None
                    if key == "review_purpose":
                        fallback_key = "objectives"
                    elif key == "review_methodology":
                        fallback_key = "methodology"
                    elif key == "evidence_base":
                        fallback_key = "tools_techniques"
                    elif key == "key_findings":
                        fallback_key = "results"
                    elif key == "future_directions":
                        fallback_key = "future_work"

                    if fallback_key and fallback_key in sec_dict:
                        f_res = sec_dict[fallback_key]
                        if f_res.status == "REPORTED":
                            s_res = f_res

                if s_res and s_res.status == "REPORTED" and s_res.content not in ["NOT_REPORTED", "NOT_APPLICABLE", "EMPTY"]:
                    start_p = s_res.source_page_start
                    end_p = s_res.source_page_end
                    if pages_text:
                        range_text = " ".join([txt for idx, txt in pages_text if start_p <= idx <= end_p])
                        if not range_text:
                            start_p, end_p = 1, len(pages_text)

                    summ = generate_section_summary(key, s_res.content)
                    res.append(
                        StructuredSectionRead(
                            key=key,
                            display_title=display_title,
                            content=s_res.content,
                            summary=summ,
                            status="REPORTED",
                            source_page_start=start_p,
                            source_page_end=end_p,
                            extraction_confidence=s_res.extraction_confidence,
                            evidence_id=f"PAPER-{prop_prefix}-EVID-{ev_counter:03d}",
                        )
                    )
                    ev_counter += 1
                else:
                    res.append(
                        StructuredSectionRead(
                            key=key,
                            display_title=display_title,
                            content="NOT_REPORTED",
                            summary="NOT_REPORTED",
                            status="NOT_REPORTED",
                            source_page_start=1,
                            source_page_end=1,
                            extraction_confidence="HIGH",
                            evidence_id=f"PAPER-{prop_prefix}-EVID-{ev_counter:03d}",
                        )
                    )
                    ev_counter += 1
        else:
            proposal_order = [
                ("problem_statement", "Problem Statement & Context"),
                ("research_gap", "Research Gap"),
                ("objectives", "Project Objectives"),
                ("technology", "Technology & Infrastructure"),
                ("methodology", "Proposed Methodology"),
                ("validation_plan", "Experimental Validation Plan"),
                ("expected_outcomes", "Expected Outcomes & Deliverables"),
                ("budget", "Project Budget & Financial Breakdown"),
                ("timeline", "Project Timeline & Milestones"),
                ("literature_review", "Literature Review"),
                ("team", "Team & Institutional Capability"),
                ("references", "References"),
            ]

            ev_counter = 1
            for key, display_title in proposal_order:
                s_res = sec_dict.get(key)
                if s_res and s_res.status == "REPORTED" and s_res.content not in ["NOT_REPORTED", "NOT_APPLICABLE", "EMPTY"]:
                    start_p = s_res.source_page_start
                    end_p = s_res.source_page_end
                    if pages_text:
                        range_text = " ".join([txt for idx, txt in pages_text if start_p <= idx <= end_p])
                        if not range_text:
                            start_p, end_p = 1, len(pages_text)

                    summ = generate_section_summary(key, s_res.content)
                    res.append(
                        StructuredSectionRead(
                            key=key,
                            display_title=display_title,
                            content=s_res.content,
                            summary=summ,
                            status="REPORTED",
                            source_page_start=start_p,
                            source_page_end=end_p,
                            extraction_confidence=s_res.extraction_confidence,
                            evidence_id=f"PROP-{prop_prefix}-EVID-{ev_counter:03d}",
                        )
                    )
                    ev_counter += 1
                else:
                    res.append(
                        StructuredSectionRead(
                            key=key,
                            display_title=display_title,
                            content="NOT_REPORTED",
                            summary="NOT_REPORTED",
                            status="NOT_REPORTED",
                            source_page_start=1,
                            source_page_end=1,
                            extraction_confidence="HIGH",
                            evidence_id=f"PROP-{prop_prefix}-EVID-{ev_counter:03d}",
                        )
                    )
                    ev_counter += 1

        return res
