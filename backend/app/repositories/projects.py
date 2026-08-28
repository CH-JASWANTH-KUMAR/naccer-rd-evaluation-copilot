from datetime import UTC, datetime

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.historical_project import HistoricalProject
from app.models.historical_source_document import HistoricalSourceDocument
from app.models.import_batch import ImportBatch
from app.schemas.project import HistoricalProjectCreate


class HistoricalProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    # HistoricalProject Methods
    def create(self, data: HistoricalProjectCreate) -> HistoricalProject:
        project = HistoricalProject(
            project_code=data.project_code,
            title=data.title,
            institution=data.institution,
            domain=data.domain,
            objectives=data.objectives,
            methodology=data.methodology,
            technology=data.technology,
            expected_outcomes=data.expected_outcomes,
            status=data.status,
            start_date=data.start_date,
            completion_date=data.completion_date,
            approved_cost=data.approved_cost,
            approved_cost_raw=data.approved_cost_raw,
            source=data.source,
            source_type=data.source_type,
            source_url=data.source_url,
            source_document_name=data.source_document_name,
            source_page_start=data.source_page_start,
            source_page_end=data.source_page_end,
            source_record_identifier=data.source_record_identifier,
            raw_record_text=data.raw_record_text,
            verification_status=data.verification_status,
            import_batch_id=data.import_batch_id,
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def get_by_id(self, project_id: str) -> HistoricalProject | None:
        stmt = select(HistoricalProject).where(HistoricalProject.id == project_id)
        return self.db.scalars(stmt).first()

    def get_by_code(self, project_code: str) -> HistoricalProject | None:
        stmt = select(HistoricalProject).where(HistoricalProject.project_code == project_code)
        return self.db.scalars(stmt).first()

    def get_all(
        self,
        domain: str | None = None,
        status: str | None = None,
        institution: str | None = None,
        source_type: str | None = None,
        verification_status: str | None = None,
        search: str | None = None,
    ) -> list[HistoricalProject]:
        stmt = select(HistoricalProject).order_by(HistoricalProject.created_at.desc())

        if domain:
            stmt = stmt.where(HistoricalProject.domain == domain)
        if status:
            stmt = stmt.where(HistoricalProject.status == status)
        if institution:
            stmt = stmt.where(HistoricalProject.institution.ilike(f"%{institution}%"))
        if source_type:
            stmt = stmt.where(HistoricalProject.source_type == source_type)
        if verification_status:
            stmt = stmt.where(HistoricalProject.verification_status == verification_status)

        if search:
            q = f"%{search}%"
            stmt = stmt.where(
                or_(
                    HistoricalProject.title.ilike(q),
                    HistoricalProject.project_code.ilike(q),
                    HistoricalProject.institution.ilike(q),
                    HistoricalProject.domain.ilike(q),
                    HistoricalProject.technology.ilike(q),
                )
            )

        return list(self.db.scalars(stmt).all())

    def update_verification_status(self, project_id: str, status: str) -> HistoricalProject | None:
        project = self.get_by_id(project_id)
        if project:
            project.verification_status = status
            project.verification_timestamp = datetime.now(UTC)
            self.db.commit()
            self.db.refresh(project)
        return project

    # ImportBatch Methods
    def create_import_batch(
        self,
        source_name: str,
        source_type: str,
        document_name: str,
        document_hash: str,
        source_url: str | None = None,
    ) -> ImportBatch:
        batch = ImportBatch(
            source_name=source_name,
            source_type=source_type,
            source_url=source_url,
            document_name=document_name,
            document_hash=document_hash,
            status="STARTED",
        )
        self.db.add(batch)
        self.db.commit()
        self.db.refresh(batch)
        return batch

    def get_import_batch_by_hash(self, document_hash: str) -> ImportBatch | None:
        stmt = select(ImportBatch).where(ImportBatch.document_hash == document_hash)
        return self.db.scalars(stmt).first()

    def get_import_batch_by_id(self, batch_id: str) -> ImportBatch | None:
        stmt = select(ImportBatch).where(ImportBatch.id == batch_id)
        return self.db.scalars(stmt).first()

    def get_all_import_batches(self) -> list[ImportBatch]:
        stmt = select(ImportBatch).order_by(ImportBatch.imported_at.desc())
        return list(self.db.scalars(stmt).all())

    def update_import_batch_status(
        self,
        batch_id: str,
        status: str,
        total: int = 0,
        successful: int = 0,
        needs_review: int = 0,
        failed: int = 0,
    ) -> ImportBatch | None:
        batch = self.get_import_batch_by_id(batch_id)
        if batch:
            batch.status = status
            batch.total_records = total
            batch.successful_records = successful
            batch.needs_review_records = needs_review
            batch.failed_records = failed
            self.db.commit()
            self.db.refresh(batch)
        return batch

    def create_source_document(
        self,
        import_batch_id: str,
        filename: str,
        file_hash: str,
        page_count: int,
        storage_path: str,
        source_url: str | None = None,
    ) -> HistoricalSourceDocument:
        doc = HistoricalSourceDocument(
            import_batch_id=import_batch_id,
            filename=filename,
            source_url=source_url,
            file_hash=file_hash,
            page_count=page_count,
            storage_path=storage_path,
            extraction_status="PROCESSED",
        )
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc
