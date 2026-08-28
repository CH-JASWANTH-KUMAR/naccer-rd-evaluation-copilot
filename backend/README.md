# NaCCER R&D Evaluation Copilot - Backend API & Database

> Python FastAPI REST API service layer and PostgreSQL relational database for NaCCER / CMPDI R&D Proposal Evaluation.

## 📌 Architecture Overview

The backend uses a clean, layered architecture:
`Router (FastAPI) → Service (Business Logic) → Repository (SQLAlchemy ORM) → PostgreSQL Database`

> [!IMPORTANT]
> **Phase P0.2 Scope:**
> This phase implements **Proposal PDF Ingestion, Local Storage, Page-Aware Text Extraction (`DocumentPage`), Deterministic Section Detection (`ProposalSection`), and Document REST API Endpoints**. No OCR, LLM, embeddings, RAG, pgvector, or financial AI engines are included in this phase.

---

## 🛠️ Tech Stack & Requirements

- **Python**: 3.12+ (Tested on Python 3.14.7)
- **Framework**: FastAPI 0.115+
- **ASGI Server**: Uvicorn
- **PDF Extractor**: `pypdf` 6.0+
- **Multipart Handler**: `python-multipart`
- **ORM**: SQLAlchemy 2.0+
- **Schemas**: Pydantic 2.0+ & pydantic-settings
- **Database**: PostgreSQL 16+ (or Docker container)
- **Database Driver**: `psycopg` (v3)
- **Migrations**: Alembic 1.13+
- **Testing**: Pytest & HTTPX
- **Code Quality**: Ruff & Mypy

---

## 🚀 Setup & Execution Guide

### 1. Virtual Environment & Dependencies
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Database Migrations
```bash
alembic upgrade head
```

### 3. Running FastAPI Development Server
```bash
uvicorn app.main:app --reload --port 8000
```
Open API documentation at `http://localhost:8000/docs`.

### 4. Code Quality & Pytest Suite
```bash
ruff check .
mypy app
pytest
```

---

## 🌐 Version 1 REST API Endpoints (`/api/v1`)

### Health & Development
- `GET /api/v1/health` -> System health status
- `POST /api/v1/seed` -> Populate development DEMO DATA

### Institutions
- `GET /api/v1/institutions` -> List registered institutions
- `POST /api/v1/institutions` -> Register new institution

### Proposals
- `GET /api/v1/proposals` -> List proposals (optional `domain` & `status` filters)
- `POST /api/v1/proposals` -> Ingest new proposal record
- `GET /api/v1/proposals/{id}` -> Get proposal detail view
- `PATCH /api/v1/proposals/{id}` -> Update proposal fields
- `DELETE /api/v1/proposals/{id}` -> Delete proposal record

### Document Processing (Phase P0.2)
- `POST /api/v1/proposals/{proposal_id}/documents` -> Upload PDF file, extract page text & detect sections
- `GET /api/v1/proposals/{proposal_id}/documents` -> List documents for proposal
- `GET /api/v1/documents/{document_id}` -> Get document processing details
- `GET /api/v1/documents/{document_id}/pages` -> Retrieve page-by-page text (`DocumentPage`)
- `GET /api/v1/documents/{document_id}/sections` -> Retrieve detected proposal sections (`ProposalSection`)
