from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

FIXTURES_DIR = Path(__file__).resolve().parent


def create_synthetic_pdf(output_path: Path) -> Path:
    """Generate a synthetic 5-page proposal PDF with extractable text for testing."""
    c = canvas.Canvas(str(output_path), pagesize=letter)
    width, height = letter

    # Page 1: Title & Background
    c.setFont("Helvetica-Bold", 18)
    c.drawString(72, height - 72, "1. Project Title")
    c.setFont("Helvetica", 12)
    c.drawString(72, height - 100, "[SYNTHETIC TEST DATA] AI-Driven Gas Detection System")

    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, height - 150, "Background")
    c.setFont("Helvetica", 11)
    c.drawString(72, height - 180, "Synthetic test data background information on mine safety and gas monitoring.")
    c.showPage()

    # Page 2: Problem Statement & Objectives
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, height - 72, "2. Problem Statement")
    c.setFont("Helvetica", 11)
    c.drawString(
        72, height - 100, "Synthetic problem statement regarding hazardous methane accumulation in underground seams."
    )

    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, height - 160, "3. Research Objectives")
    c.setFont("Helvetica", 11)
    c.drawString(72, height - 190, "Objective 1: Deploy wireless mesh sensor nodes.")
    c.drawString(72, height - 210, "Objective 2: Real-time telemetry monitoring.")
    c.showPage()

    # Page 3: Literature Review & Methodology
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, height - 72, "4. Literature Review")
    c.setFont("Helvetica", 11)
    c.drawString(72, height - 100, "Synthetic literature review analyzing existing wired gas detection systems.")

    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, height - 160, "5. Proposed Methodology")
    c.setFont("Helvetica", 11)
    c.drawString(72, height - 190, "Methodology includes IoT spatial mesh node prototyping and lab validation.")
    c.showPage()

    # Page 4: Work Plan & Expected Outcomes
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, height - 72, "6. Work Plan")
    c.setFont("Helvetica", 11)
    c.drawString(
        72,
        height - 100,
        "24-month project timeline: Months 1-6 design, Months 7-18 lab trials, Months 19-24 field test.",
    )

    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, height - 160, "7. Expected Outcomes")
    c.setFont("Helvetica", 11)
    c.drawString(72, height - 190, "Expected deliverables: Autonomous warning system and reduced venting latency.")
    c.showPage()

    # Page 5: Budget, Manpower & Equipment
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, height - 72, "8. Estimated Budget")
    c.setFont("Helvetica", 11)
    c.drawString(72, height - 100, "Total Estimated Budget: 4,500,000 INR.")

    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, height - 160, "9. Manpower")
    c.setFont("Helvetica", 11)
    c.drawString(72, height - 190, "Principal Investigator, 2 Senior Research Fellows.")

    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, height - 240, "10. Equipment")
    c.setFont("Helvetica", 11)
    c.drawString(72, height - 270, "Gas calibration chamber, wireless transceiver modules.")
    c.showPage()

    c.save()
    return output_path


def create_scanned_pdf(output_path: Path) -> Path:
    """Generate a synthetic scanned PDF (drawing shapes only, 0 extractable text string)."""
    c = canvas.Canvas(str(output_path), pagesize=letter)
    width, height = letter
    c.rect(50, 50, width - 100, height - 100, stroke=1, fill=0)
    c.line(50, height // 2, width - 50, height // 2)
    c.showPage()
    c.save()
    return output_path


if __name__ == "__main__":
    pdf_file = FIXTURES_DIR / "synthetic_proposal.pdf"
    scanned_file = FIXTURES_DIR / "scanned_proposal.pdf"
    create_synthetic_pdf(pdf_file)
    create_scanned_pdf(scanned_file)
    print(f"Generated synthetic test PDFs at: {pdf_file} and {scanned_file}")
