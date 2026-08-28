from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.documents import DocumentRepository
from app.schemas.document import DocumentDetailRead, DocumentPageRead, ProposalSectionRead
from app.services.document_processor import DocumentProcessingService

router = APIRouter()


@router.post(
    "/proposals/{proposal_id}/documents",
    response_model=DocumentDetailRead,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and process proposal PDF document",
)
def upload_proposal_document(
    proposal_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload proposal PDF, extract page text, detect sections, and store page records."""
    processor = DocumentProcessingService(db)
    doc = processor.upload_and_process_pdf(proposal_id, file)

    pages = processor.doc_repo.get_pages(doc.id)
    sections = processor.doc_repo.get_sections(doc.id)

    return DocumentDetailRead(
        id=doc.id,
        proposal_id=doc.proposal_id,
        filename=doc.filename,
        file_type=doc.file_type,
        file_size=doc.file_size,
        storage_path=doc.storage_path,
        processing_status=doc.processing_status,
        processing_error=doc.processing_error,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
        pages_count=len(pages),
        sections_count=len(sections),
    )


@router.get(
    "/proposals/{proposal_id}/documents",
    response_model=list[DocumentDetailRead],
    summary="List documents for a proposal",
)
def list_proposal_documents(proposal_id: str, db: Session = Depends(get_db)):
    """Retrieve all uploaded document records for a proposal."""
    repo = DocumentRepository(db)
    docs = repo.get_by_proposal_id(proposal_id)
    results = []
    for doc in docs:
        pages = repo.get_pages(doc.id)
        sections = repo.get_sections(doc.id)
        results.append(
            DocumentDetailRead(
                id=doc.id,
                proposal_id=doc.proposal_id,
                filename=doc.filename,
                file_type=doc.file_type,
                file_size=doc.file_size,
                storage_path=doc.storage_path,
                processing_status=doc.processing_status,
                processing_error=doc.processing_error,
                created_at=doc.created_at,
                updated_at=doc.updated_at,
                pages_count=len(pages),
                sections_count=len(sections),
            )
        )
    return results


@router.get(
    "/documents/{document_id}",
    response_model=DocumentDetailRead,
    summary="Get document processing details",
)
def get_document_details(document_id: str, db: Session = Depends(get_db)):
    """Retrieve detailed metadata for a specific document."""
    repo = DocumentRepository(db)
    doc = repo.get_by_id(document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{document_id}' not found.",
        )
    pages = repo.get_pages(doc.id)
    sections = repo.get_sections(doc.id)
    return DocumentDetailRead(
        id=doc.id,
        proposal_id=doc.proposal_id,
        filename=doc.filename,
        file_type=doc.file_type,
        file_size=doc.file_size,
        storage_path=doc.storage_path,
        processing_status=doc.processing_status,
        processing_error=doc.processing_error,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
        pages_count=len(pages),
        sections_count=len(sections),
    )


@router.get(
    "/documents/{document_id}/pages",
    response_model=list[DocumentPageRead],
    summary="Get extracted pages for document",
)
def get_document_pages(document_id: str, db: Session = Depends(get_db)):
    """Retrieve page-by-page extracted text records."""
    repo = DocumentRepository(db)
    doc = repo.get_by_id(document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{document_id}' not found.",
        )
    return repo.get_pages(document_id)


@router.get(
    "/documents/{document_id}/sections",
    response_model=list[ProposalSectionRead],
    summary="Get detected sections for document",
)
def get_document_sections(document_id: str, db: Session = Depends(get_db)):
    """Retrieve detected proposal section range records."""
    repo = DocumentRepository(db)
    doc = repo.get_by_id(document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{document_id}' not found.",
        )
    return repo.get_sections(document_id)
