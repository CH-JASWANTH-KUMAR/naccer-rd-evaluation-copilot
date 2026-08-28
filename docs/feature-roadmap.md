# NaCCER R&D Evaluation Copilot - Feature Roadmap

## Phase 0: Base Frontend Foundation (COMPLETED IN THIS SETUP)
- [x] Next.js 16.3.3 App Router scaffolding with React 19.2 and TypeScript.
- [x] Enterprise neutral visual system (Slate/Zinc palette, Lucide icons, responsive design).
- [x] Scalable folder structure (`app/`, `components/`, `lib/`, `docs/`, `public/`).
- [x] Typed domain interfaces (`lib/types/`) and REST client abstractions (`lib/api/`).
- [x] Core Page Routes:
  - Dashboard (`/dashboard`)
  - Proposals Directory (`/proposals`) & 9-Tab Workspace (`/proposals/[id]`)
  - Historical Project Database (`/projects`) & Detail (`/projects/[id]`)
  - Evaluation Workspace (`/evaluations`) & Rubric Detail (`/evaluations/[id]`)
  - Evaluation Report View (`/reports`)
  - Proposal Upload Workspace (`/upload`)
  - Settings Page (`/settings`)
  - Health API Endpoint (`/api/health`)
- [x] Complete developer documentation and environment template.

---

## Phase P0: Core AI/ML & Rules Engines (UPCOMING)
1. **Proposal Document Understanding**: OCR parsing, section extraction, and structured JSON extraction from uploaded PDFs.
2. **Proposal Completeness & Compliance**: Rule engine validating required DST/NaCCER attachments, certificates, and eligibility.
3. **Historical R&D Project Benchmarking**: Vector embeddings & pgvector search to identify prior CIL project overlaps.
4. **Evidence-Based Novelty Analysis**: NLP similarity distance scoring against global scientific literature and patent databases.
5. **Financial Compliance Checking**: Automatic verification of proposed equipment rates, SRF/JRF fellowship allowances, and contingency limits.
6. **Configurable Evaluation Rubric**: Automated baseline scoring with reviewer score adjustments.
7. **Explainable Report Generation**: Citation-backed PDF synthesis report generator.

---

## Phase P1: Workflow & Governance (UPCOMING)
8. **Human Reviewer Workspace & Feedback Loop**: Fine-tuning reviewer score modifications and comment threads.
9. **Audit Trail Logging**: Immutable action history for all committee decisions.
