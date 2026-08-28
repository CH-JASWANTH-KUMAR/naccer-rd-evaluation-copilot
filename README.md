# NaCCER R&D Evaluation Copilot

> Production-oriented AI/ML R&D Proposal Evaluation platform for NaCCER / Coal India Limited (CIL) technical reviewers.

## 📌 Project Purpose & Base Setup Phase Scope

This repository contains the **Base Frontend Foundation** for the NaCCER R&D Evaluation Copilot. The application is designed to assist technical committees and reviewers in evaluating research proposals submitted for Coal India R&D funding.

> [!IMPORTANT]
> **Current Development Phase Status (Base Setup Only):**
> AI/ML processing, proposal analysis, RAG vector distance calculation, document embeddings, financial rule checking engines, backend REST services, and database persistence are **intentionally NOT implemented in this phase**.
> 
> All UI views use typed domain abstractions (`lib/api/` and `lib/types/`) and clearly labeled structural placeholders.

---

## 🛠️ Core Tech Stack

- **Framework**: Next.js 16.3.3 (App Router)
- **UI Architecture**: React 19.2 (Strict Server & Client Components)
- **Language**: TypeScript (Strict Type Checking)
- **Styling**: Tailwind CSS v4, Enterprise CSS Custom Variables
- **Icons**: Lucide Icons (`lucide-react`)
- **Package Manager**: `pnpm` (Single Lockfile `pnpm-lock.yaml`)
- **Linting**: ESLint 9 (Next.js Config)

---

## 🚀 Setup & Development Commands

Ensure you have **Node.js 20.9+** and **pnpm** installed.

```bash
# Clone and enter project directory
cd naccer-rd-evaluation-copilot

# Install dependencies with pnpm
pnpm install

# Start Next.js local development server
pnpm dev

# Run TypeScript type check
npx tsc --noEmit

# Run ESLint linter
pnpm lint

# Build production bundle
pnpm build
```

---

## 📁 Scalable App Router Project Structure

```
naccer-rd-evaluation-copilot/
├── app/
│   ├── layout.tsx                     # Root layout with Enterprise theme
│   ├── page.tsx                       # Root redirect to /dashboard
│   ├── globals.css                    # Design Tokens & CSS Variables
│   ├── (dashboard)/
│   │   ├── layout.tsx                 # Persistent Sidebar + Header Shell
│   │   ├── dashboard/page.tsx         # Executive Overview & Metrics Shell
│   │   ├── proposals/
│   │   │   ├── page.tsx               # Proposals Directory List
│   │   │   └── [id]/page.tsx          # 9-Tab Proposal Detail Workspace
│   │   ├── projects/
│   │   │   ├── page.tsx               # Historical Project Search & Directory
│   │   │   └── [id]/page.tsx          # Historical Project Benchmark Detail
│   │   ├── evaluations/
│   │   │   ├── page.tsx               # Evaluation Rubric List
│   │   │   └── [id]/page.tsx          # Interactive Scoring Workspace
│   │   ├── reports/page.tsx           # Multi-section Formal Evaluation Report
│   │   └── settings/page.tsx          # Rubric & API Threshold Settings
│   ├── upload/page.tsx                # Proposal PDF Drag & Drop Workspace
│   └── api/health/route.ts            # Minimal Health Check Endpoint
│
├── components/
│   ├── ui/                            # Enterprise UI Components (Button, Card, Table, Badge, Tabs, Input, Select, Progress)
│   ├── layout/                        # Responsive Sidebar & Topbar Header
│   ├── dashboard/                     # Metrics Cards & Activity Tables
│   └── shared/                        # Module Placeholder Banners
│
├── lib/
│   ├── constants/                     # Domain Constants & Demo Data
│   ├── types/                         # TypeScript Domain Models
│   ├── utils/                         # Class Merger (`cn`) & Formatters
│   ├── config/                        # App Config & Environment Stubs
│   └── api/                           # Typed REST Service Abstraction Layer
│
├── docs/                              # System Documentation
│   ├── architecture.md                # Future System Architecture & Boundary
│   ├── feature-roadmap.md             # Development Phase Roadmap (P0 & P1)
│   └── development.md                 # Setup & Workflow Guidelines
│
├── .env.example                       # Environment Variable Template
└── package.json                       # Next.js 16.3.3 / React 19.2 manifest
```

---

## 🌐 Routes Overview

- `/` -> Redirects to `/dashboard`
- `/dashboard` -> Executive Metrics & Recent Submissions Table
- `/proposals` -> Filterable Proposal Directory
- `/proposals/[id]` -> Proposal Detail Workspace (Overview, Document, Completeness, Financial, Historical Benchmark, Novelty, Evaluation, Evidence, Review History)
- `/projects` -> Historical Benchmarking Directory
- `/projects/[id]` -> Historical Benchmark Detail Page
- `/evaluations` -> Active Technical Evaluations List
- `/evaluations/[id]` -> Interactive Reviewer Rubric & Score Workspace
- `/reports` -> Printable Synthesis Report Document
- `/upload` -> Proposal PDF Upload & Metadata Registration Form
- `/settings` -> Platform & Rubric Thresholds Configuration
- `/api/health` -> System JSON Health Status Endpoint

---

## 🔮 Future Development Roadmap

- **Phase P0 (Core AI & Rules Engine Integration)**:
  1. Proposal Document OCR & Ingestion Pipeline
  2. Proposal Completeness & Compliance Engine
  3. Historical Project Vector Benchmarking (pgvector / FastAPI)
  4. Evidence-Based Novelty Search Engine
  5. Financial Rule & Cost Head Checking Engine
  6. Configurable Evaluation Rubric & Auto Scoring
  7. Explainable Report Generation

- **Phase P1 (Workflow & Governance)**:
  8. Human Reviewer Feedback Loop
  9. Immutable Audit Trail Logging

---

## 📄 License & Confidentiality

Developed for NaCCER / CMPDI R&D Proposal Evaluation Systems. Internal Enterprise Use.
