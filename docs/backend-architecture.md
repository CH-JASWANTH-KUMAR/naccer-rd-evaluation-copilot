# NaCCER R&D Evaluation Copilot - Backend Architecture & Database Boundary

> Phase P0.1 Backend Foundation & Data Flow Specifications

## 1. System Communication Architecture

```
┌────────────────────────────────────────────────────────┐
│               Next.js 16 App Router Frontend            │
│       (React 19.2, TypeScript, REST Client Abstraction)│
└───────────────────────────┬────────────────────────────┘
                            │ REST API (JSON over HTTP)
                            ▼
┌────────────────────────────────────────────────────────┐
│                 Python FastAPI Backend                 │
│         (Pydantic 2.x, SQLAlchemy 2.x ORM, Services)   │
└───────────────────────────┬────────────────────────────┘
                            │ PostgreSQL Protocol (psycopg3)
                            ▼
┌────────────────────────────────────────────────────────┐
│               PostgreSQL Relational DB                 │
│    (Institutions, Proposals, Documents, Evaluations)   │
└────────────────────────────────────────────────────────┘
```

---

## 2. Core Service Boundaries

The FastAPI application exposes versioned REST API endpoints (`/api/v1`) providing structured JSON data contracts:

1. **Institutions Service**: Academic and research institution registry.
2. **Proposals Service**: Proposal ingestion, retrieval, status management, and metadata CRUD operations.
3. **Historical Projects Service**: Archived project directory for future vector benchmarking.
4. **Health Service**: Backend operational monitoring.

---

## 3. Isolation of Future AI Services

In upcoming development phases (P0.2 - P0.10):
- Document processing, OCR, embeddings, RAG vector distance calculations, and financial rule engines will be implemented **behind this FastAPI service boundary**.
- The Next.js frontend will continue to communicate exclusively through REST API endpoints without direct dependency on Python ML frameworks.
