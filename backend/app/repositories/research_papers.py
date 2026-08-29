from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.paper_page import PaperPage
from app.models.research_paper import ResearchPaper
from app.schemas.research_paper import ResearchPaperCreate


class ResearchPaperRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, paper_id: str) -> ResearchPaper | None:
        stmt = select(ResearchPaper).options(selectinload(ResearchPaper.pages)).where(ResearchPaper.id == paper_id)
        return self.db.scalar(stmt)

    def get_by_hash(self, file_hash: str) -> ResearchPaper | None:
        stmt = select(ResearchPaper).options(selectinload(ResearchPaper.pages)).where(ResearchPaper.file_hash == file_hash)
        return self.db.scalar(stmt)

    def get_all(self, research_domain: str | None = None) -> list[ResearchPaper]:
        stmt = select(ResearchPaper).options(selectinload(ResearchPaper.pages)).order_by(ResearchPaper.created_at.desc())
        if research_domain:
            stmt = stmt.where(ResearchPaper.research_domain == research_domain)
        return list(self.db.scalars(stmt).all())

    def create(self, paper_data: ResearchPaperCreate) -> ResearchPaper:
        paper = ResearchPaper(
            title=paper_data.title,
            authors=paper_data.authors,
            abstract=paper_data.abstract,
            publication_year=paper_data.publication_year,
            journal_or_conference=paper_data.journal_or_conference,
            doi=paper_data.doi,
            research_domain=paper_data.research_domain,
            keywords=paper_data.keywords,
            source_filename=paper_data.source_filename,
            source_document_type=paper_data.source_document_type,
            page_count=paper_data.page_count,
            file_hash=paper_data.file_hash,
            storage_path=paper_data.storage_path,
            extraction_status=paper_data.extraction_status,
            raw_text=paper_data.raw_text,
        )
        self.db.add(paper)
        self.db.commit()
        self.db.refresh(paper)
        return paper

    def add_page(self, paper_id: str, page_number: int, text: str, detected_sections: str | None = None) -> PaperPage:
        page = PaperPage(
            research_paper_id=paper_id,
            page_number=page_number,
            extracted_text=text,
            character_count=len(text),
            detected_sections=detected_sections,
            extraction_status="COMPLETED",
        )
        self.db.add(page)
        self.db.commit()
        self.db.refresh(page)
        return page
