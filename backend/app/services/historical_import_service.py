import hashlib
import re
from datetime import datetime
from pathlib import Path

import pypdf
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.repositories.projects import HistoricalProjectRepository
from app.schemas.project import HistoricalProjectCreate, ImportReportRead

HISTORICAL_STORAGE_DIR = Path(__file__).resolve().parent.parent.parent / "storage" / "historical"
OFFICIAL_CMPDI_URL = "https://www.cmpdi.co.in/sites/default/files/2026-04/31_03_2026_RD%20ongoing%20projects.pdf"


class HistoricalProjectImportService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = HistoricalProjectRepository(db)

    def import_pdf_catalog(
        self,
        file: UploadFile,
        source_name: str = "CIL/CMPDI R&D Catalogue",
        source_type: str = "OFFICIAL",
        source_url: str | None = OFFICIAL_CMPDI_URL,
    ) -> ImportReportRead:
        filename = file.filename or "cil_cmpdi_projects.pdf"
        if not filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF documents (.pdf) are supported for historical catalogue import.",
            )

        # 1. Read file bytes & compute SHA-256 hash
        content = file.file.read()
        file_hash = hashlib.sha256(content).hexdigest()

        # 2. Check for Duplicate Import
        existing_batch = self.repo.get_import_batch_by_hash(file_hash)
        if existing_batch:
            return ImportReportRead(
                import_batch_id=existing_batch.id,
                source_name=existing_batch.source_name,
                document_name=existing_batch.document_name,
                document_hash=existing_batch.document_hash,
                total_detected=existing_batch.total_records,
                imported_count=existing_batch.successful_records,
                needs_review_count=existing_batch.needs_review_records,
                duplicate_count=existing_batch.total_records,
                failed_count=existing_batch.failed_records,
                status="ALREADY_IMPORTED",
                message="This document hash has already been imported. Duplicate import skipped.",
            )

        # 3. Store PDF locally in development storage
        HISTORICAL_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        batch = self.repo.create_import_batch(
            source_name=source_name,
            source_type=source_type,
            document_name=filename,
            document_hash=file_hash,
            source_url=source_url,
        )

        storage_path = HISTORICAL_STORAGE_DIR / f"{batch.id}_{filename}"
        with open(storage_path, "wb") as f:
            f.write(content)

        # 4. Extract pages using pypdf
        reader = pypdf.PdfReader(storage_path)
        page_count = len(reader.pages)
        self.repo.create_source_document(
            import_batch_id=batch.id,
            filename=filename,
            file_hash=file_hash,
            page_count=page_count,
            storage_path=str(storage_path),
            source_url=source_url,
        )

        pages_text: list[tuple[int, str]] = []
        for idx, page in enumerate(reader.pages, start=1):
            txt = page.extract_text() or ""
            pages_text.append((idx, txt))

        # 5. Parse project records
        raw_records = self._parse_catalogue_records(pages_text)

        imported_count = 0
        needs_review_count = 0
        failed_count = 0
        duplicate_count = 0

        for rec in raw_records:
            try:
                # Check if project code already exists in DB
                existing_proj = self.repo.get_by_code(rec["project_code"])
                if existing_proj:
                    duplicate_count += 1
                    continue

                # Determine validation status
                verification_status = "NEEDS_REVIEW"
                if not rec["title"] or not rec["institution"] or rec["project_code"].startswith("UNKNOWN"):
                    needs_review_count += 1
                else:
                    imported_count += 1

                project_create = HistoricalProjectCreate(
                    project_code=rec["project_code"],
                    title=rec["title"] or "Untitled Historical Project",
                    institution=rec["institution"] or "Unknown Implementing Agency",
                    domain=rec["domain"] or "Coal Mining & Safety R&D",
                    objectives=rec.get("objectives"),
                    methodology=rec.get("methodology"),
                    technology=rec.get("technology"),
                    expected_outcomes=rec.get("expected_outcomes"),
                    status=rec.get("status", "ONGOING"),
                    start_date=rec.get("start_date"),
                    completion_date=rec.get("completion_date"),
                    approved_cost=rec.get("approved_cost", 0.0),
                    approved_cost_raw=rec.get("approved_cost_raw"),
                    source=source_name,
                    source_type=source_type,
                    source_url=source_url,
                    source_document_name=filename,
                    source_page_start=rec.get("source_page_start", 1),
                    source_page_end=rec.get("source_page_end", 1),
                    source_record_identifier=rec["project_code"],
                    raw_record_text=rec.get("raw_record_text"),
                    verification_status=verification_status,
                    import_batch_id=batch.id,
                )
                self.repo.create(project_create)

            except Exception:
                failed_count += 1

        total_detected = len(raw_records)
        self.repo.update_import_batch_status(
            batch_id=batch.id,
            status="COMPLETED" if failed_count == 0 else "PARTIAL",
            total=total_detected,
            successful=imported_count,
            needs_review=needs_review_count,
            failed=failed_count,
        )

        return ImportReportRead(
            import_batch_id=batch.id,
            source_name=source_name,
            document_name=filename,
            document_hash=file_hash,
            total_detected=total_detected,
            imported_count=imported_count,
            needs_review_count=needs_review_count,
            duplicate_count=duplicate_count,
            failed_count=failed_count,
            status="COMPLETED" if failed_count == 0 else "PARTIAL",
            message=f"Successfully processed {total_detected} projects from CIL/CMPDI catalogue.",
        )

    def _parse_catalogue_records(self, pages_text: list[tuple[int, str]]) -> list[dict]:
        """Structure-aware record extraction for CIL/CMPDI project catalogues."""
        records: list[dict] = []
        full_document_text = "\n".join([f"--- PAGE {p_num} ---\n{text}" for p_num, text in pages_text])

        # Pattern matching project blocks (e.g., CIL/R&D/..., Sl. No. X, Project Code:)
        pattern = r"(?=(?:CIL\/R&D\/\d+[\w\/]*|\bSl\.?\s*No\.?\s*\d+|\bProject\s*Code\s*:|\bSub-grant\s*:))"
        splits = re.split(pattern, full_document_text, flags=re.IGNORECASE)

        if len(splits) <= 1:
            return self._parse_fallback_blocks(pages_text)

        record_idx = 1
        for block in splits:
            clean_block = block.strip()
            if len(clean_block) < 30:
                continue

            page_matches = [int(m) for m in re.findall(r"--- PAGE (\d+) ---", block)]
            page_start = page_matches[0] if page_matches else 1
            page_end = page_matches[-1] if page_matches else page_start

            # Extract Project Code
            code_match = re.search(
                r"(CIL\/R&D\/[\w\/\-]+|CIL\/[\w\/\-]+|\b[A-Z]{2,4}\/\d{2,4}\/[\w\/\-]+)", clean_block, re.IGNORECASE
            )
            project_code = code_match.group(1) if code_match else f"CIL-RD-2026-{record_idx:03d}"

            # Extract Institution / Implementing Agency
            agency_match = re.search(
                r"(?:Principal\s+Implementing\s+Agency|Implementing\s+Agency|Institution|Submitting\s+Institute)\s*:?\s*([^\n]+(?:\n[^\n]+){0,1})",
                clean_block,
                re.IGNORECASE,
            )
            sub_agency_match = re.search(r"Sub-implementing\s+agency\s*:?\s*([^\n]+)", clean_block, re.IGNORECASE)

            agency = (
                agency_match.group(1).replace("\n", " ").strip() if agency_match else "CSIR-CIMFR / CMPDI / IIT (ISM)"
            )
            if sub_agency_match:
                agency = f"{agency} (Sub: {sub_agency_match.group(1).strip()})"

            # Extract Title
            title_match = re.search(
                r"(?:Title|Project Title|Name of Project)\s*:?\s*([^\n]+(?:\n[^\n]+){0,2})",
                clean_block,
                re.IGNORECASE,
            )
            if title_match:
                title = title_match.group(1).replace("\n", " ").strip()
            else:
                lines = [
                    line_item.strip()
                    for line_item in clean_block.split("\n")
                    if line_item.strip() and not line_item.startswith("---") and not line_item.startswith("Sl.")
                ]
                title = lines[0] if lines else f"Ongoing CIL R&D Project {record_idx}"

            # Extract Approved Cost
            cost_match = re.search(
                r"(?:Approved\s+(?:Outlay|Cost)|Cost|Outlay)\s*:?\s*(Rs\.?\s*[\d\.\,]+\s*(?:Lakhs?|Crores?|INR)?)",
                clean_block,
                re.IGNORECASE,
            )
            cost_raw = cost_match.group(1).strip() if cost_match else None
            cost_numeric = self._parse_cost_numeric(cost_raw)

            # Dates
            start_date = self._extract_date(
                clean_block, [r"Start Date\s*:?\s*([\d\/\.\-]+)", r"Date of Commencement\s*:?\s*([\d\/\.\-]+)"]
            )
            comp_date = self._extract_date(
                clean_block, [r"Completion Date\s*:?\s*([\d\/\.\-]+)", r"Scheduled Completion\s*:?\s*([\d\/\.\-]+)"]
            )

            records.append(
                {
                    "project_code": project_code[:100],
                    "title": title[:500],
                    "institution": agency[:255],
                    "domain": "Mining & Safety R&D",
                    "objectives": clean_block[:1000],
                    "methodology": None,
                    "technology": None,
                    "expected_outcomes": None,
                    "status": "ONGOING",
                    "start_date": start_date,
                    "completion_date": comp_date,
                    "approved_cost": cost_numeric,
                    "approved_cost_raw": cost_raw,
                    "source_page_start": page_start,
                    "source_page_end": page_end,
                    "raw_record_text": clean_block[:3000],
                }
            )
            record_idx += 1

        return records

    def _parse_fallback_blocks(self, pages_text: list[tuple[int, str]]) -> list[dict]:
        records: list[dict] = []
        rec_count = 1
        for p_num, text in pages_text:
            lines = [line_item.strip() for line_item in text.split("\n") if line_item.strip()]
            for line in lines:
                if len(line) > 25 and ("project" in line.lower() or "r&d" in line.lower() or "cil" in line.lower()):
                    records.append(
                        {
                            "project_code": f"CIL-RD-2026-{rec_count:03d}",
                            "title": line[:500],
                            "institution": "CMPDI / Implementing Agency",
                            "domain": "Coal Mining R&D",
                            "objectives": line,
                            "status": "ONGOING",
                            "approved_cost": 0.0,
                            "source_page_start": p_num,
                            "source_page_end": p_num,
                            "raw_record_text": text[:1500],
                        }
                    )
                    rec_count += 1
        return records

    def _parse_cost_numeric(self, cost_raw: str | None) -> float:
        if not cost_raw:
            return 0.0
        nums = re.findall(r"\d+(?:\.\d+)?", cost_raw.replace(",", ""))
        if not nums:
            return 0.0
        val = float(nums[0])
        if "lakh" in cost_raw.lower():
            val *= 100000.0
        elif "crore" in cost_raw.lower():
            val *= 10000000.0
        return val

    def _extract_date(self, text: str, patterns: list[str]) -> str | None:
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                raw_d = m.group(1).strip()
                try:
                    parts = re.split(r"[\.\/\-]", raw_d)
                    if len(parts) == 3:
                        d, m_val, y = int(parts[0]), int(parts[1]), int(parts[2])
                        if y < 100:
                            y += 2000
                        return datetime(y, m_val, d).strftime("%Y-%m-%d")
                except Exception:
                    pass
        return None
