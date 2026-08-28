from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.document import Document
from app.models.document_page import DocumentPage
from app.models.proposal_section import ProposalSection


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_document(
        self, proposal_id: str, filename: str, file_type: str, file_size: int, storage_path: str
    ) -> Document:
        doc = Document(
            proposal_id=proposal_id,
            filename=filename,
            file_type=file_type,
            file_size=file_size,
            storage_path=storage_path,
            processing_status="UPLOADED",
        )
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def get_by_id(self, document_id: str) -> Document | None:
        stmt = (
            select(Document)
            .options(joinedload(Document.pages), joinedload(Document.sections))
            .where(Document.id == document_id)
        )
        return self.db.scalars(stmt).first()

    def get_by_proposal_id(self, proposal_id: str) -> list[Document]:
        stmt = (
            select(Document)
            .options(joinedload(Document.pages), joinedload(Document.sections))
            .where(Document.proposal_id == proposal_id)
            .order_by(Document.created_at.desc())
        )
        return list(self.db.scalars(stmt).unique().all())

    def update_status(self, document_id: str, status: str, error_message: str | None = None) -> Document | None:
        doc = self.get_by_id(document_id)
        if doc:
            doc.processing_status = status
            doc.processing_error = error_message
            self.db.commit()
            self.db.refresh(doc)
        return doc

    def add_page(self, document_id: str, page_number: int, text: str) -> DocumentPage:
        page = DocumentPage(document_id=document_id, page_number=page_number, text=text)
        self.db.add(page)
        self.db.commit()
        self.db.refresh(page)
        return page

    def get_pages(self, document_id: str) -> list[DocumentPage]:
        stmt = (
            select(DocumentPage).where(DocumentPage.document_id == document_id).order_by(DocumentPage.page_number.asc())
        )
        return list(self.db.scalars(stmt).all())

    def add_section(
        self,
        proposal_id: str,
        document_id: str,
        section_type: str,
        section_title: str,
        content: str,
        start_page: int,
        end_page: int,
        confidence: float = 1.0,
    ) -> ProposalSection:
        section = ProposalSection(
            proposal_id=proposal_id,
            document_id=document_id,
            section_type=section_type,
            section_title=section_title,
            content=content,
            start_page=start_page,
            end_page=end_page,
            confidence=confidence,
        )
        self.db.add(section)
        self.db.commit()
        self.db.refresh(section)
        return section

    def get_sections(self, document_id: str) -> list[ProposalSection]:
        stmt = (
            select(ProposalSection)
            .where(ProposalSection.document_id == document_id)
            .order_by(ProposalSection.start_page.asc())
        )
        return list(self.db.scalars(stmt).all())
