# NaCCER R&D Evaluation Copilot — Page-Aware Document Processing Architecture

> Phase P0.2 Document Ingestion & Provenance Specifications

## 1. Document Processing Pipeline Architecture

```
USER PDF Upload
      ↓
POST /api/v1/proposals/{proposal_id}/documents
      ↓
Local Storage (`backend/storage/documents/{doc_id}_{filename}`)
      ↓
`Document` Record (status = `PROCESSING`)
      ↓
`pypdf` Page Extractor
      ↓
┌────────────────────────────────────────────────────────┐
│                   `DocumentPage`                       │
│    (document_id, page_number, text) [Unique Constraint]│
└───────────────────────────┬────────────────────────────┘
                            │ Heading Matching
                            ▼
┌────────────────────────────────────────────────────────┐
│                 `ProposalSection`                      │
│ (section_type, section_title, content, start/end_page) │
└───────────────────────────┬────────────────────────────┘
                            │ Safe Non-Overwriting Update
                            ▼
┌────────────────────────────────────────────────────────┐
│                      `Proposal`                        │
│ (problem_statement, objectives, methodology, etc.)     │
└────────────────────────────────────────────────────────┘
```

---

## 2. Why Page-Level Provenance is Mandatory

For NaCCER / CMPDI technical reviewers, AI-generated findings or evaluation scores without exact source citations are unacceptable.

Every extracted snippet and section must maintain:
- **`document_id`**: Foreign key pointing to the exact uploaded PDF file.
- **`page_number`**: 1-indexed page location within the PDF.
- **`start_page` & `end_page`**: Boundary pages for detected proposal sections.

Future evidence and benchmark modules (Phase P0.3+) will anchor citations directly to: `Document → Page → Snippet`.

---

## 3. Storage Behavior & Isolation

Uploaded PDF files are stored in development under `backend/storage/documents/`.
- Files are named using a sanitized UUID prefix: `{document_id}_{sanitized_original_filename}`.
- Direct filesystem access is not exposed as a public static directory.
- `backend/storage/` is ignored in `.gitignore`.
- The storage abstraction (`DocumentProcessingService`) isolates filesystem calls so S3-compatible cloud storage can be introduced in production without breaking service contracts.

---

## 4. Processing Lifecycle & Failure Handling

| Status | Description |
| :--- | :--- |
| `UPLOADED` | File received and stored to disk. |
| `PROCESSING` | `pypdf` engine is reading pages and matching headings. |
| `PROCESSED` | Pages and sections successfully persisted to database. |
| `FAILED` | Exception occurred or scanned PDF detected (<50 characters extracted). `processing_error` contains clear error message explaining OCR limitation. |

> [!NOTE]
> **OCR Limitation Note**: The current extractor processes text-based PDFs. If a PDF is scanned / image-only, `processing_status` is set to `FAILED` with message `"Scanned / image-only PDFs are not supported yet (OCR will be added in Phase P0.2+ / P0.3)."`. Empty proposal records are never silently created.
