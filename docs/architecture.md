# NaCCER R&D Evaluation Copilot - System Architecture Overview

## 🏗️ Monolithic Frontend & Future REST API Boundary

The **NaCCER R&D Evaluation Copilot** follows a modular monolith architecture. The Next.js 16 App Router application serves as the authoritative enterprise UI workspace, designed to communicate with a future Python FastAPI backend through clean, strongly typed REST service modules.

### High-Level Future Data Flow Architecture

```
┌────────────────────────────────────────────────────────┐
│               Next.js 16 App Router Frontend            │
│  (React 19.2, TypeScript, Tailwind CSS, Enterprise UI) │
└───────────────────────────┬────────────────────────────┘
                            │ REST API (JSON over HTTP)
                            ▼
┌────────────────────────────────────────────────────────┐
│                 Python FastAPI Backend                 │
│         (REST Endpoints, Document Parsing, OCR)        │
└───────┬───────────────────┬───────────────────┬────────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐   ┌─────────────────┐   ┌──────────────┐
│  PostgreSQL  │   │     pgvector    │   │MinIO / S3 Object│
│ (Metadata/DB)│   │ (Vector Search) │   │ (PDF Storage)│
└──────────────┘   └─────────────────┘   └──────────────┘
```

---

## 🔌 API Abstraction Layer (`lib/api/`)

To prevent components from directly executing scattered `fetch()` calls or locking onto UI mocks, all data interactions are isolated within `lib/api/`:

- `proposals.ts`: Proposal retrieval, listing, filtering, and registration stubs.
- `projects.ts`: Historical project query and benchmark retrieval stubs.
- `evaluations.ts`: Rubric scoring, criterion feedback, and reviewer action stubs.
- `reports.ts`: Synthesis report aggregation and executive summary stubs.

---

## 🔒 Security & Backend Boundary Constraints

1. **No Frontend Secret Exposure**: No database credentials, vector API keys, or private models are embedded in the Next.js bundle.
2. **Clean REST Boundary**: The frontend expects standard JSON payloads from `NEXT_PUBLIC_API_BASE_URL`.
3. **Stateless UI**: UI state is strictly localized to React component state or route parameters.
