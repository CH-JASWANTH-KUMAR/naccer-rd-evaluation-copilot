from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

FIXTURES_DIR = Path(__file__).resolve().parent


def create_complete_proposal(output_path: Path) -> Path:
    """Generate SYNTHETIC TEST PROPOSAL A (Complete proposal with budget breakdown)."""
    c = canvas.Canvas(str(output_path), pagesize=letter)
    width, height = letter

    # Page 1
    c.setFont("Helvetica-Bold", 14)
    c.drawString(72, height - 72, "SYNTHETIC TEST PROPOSAL — NOT AN OFFICIAL CIL/NaCCER DOCUMENT")
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, height - 100, "Project Title: AI-Based Real-Time Methane Monitoring System")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(72, height - 130, "Problem Statement")
    c.setFont("Helvetica", 10)
    c.drawString(72, height - 150, "Methane gas buildup in underground coal seams poses severe explosion risks.")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(72, height - 180, "Project Objectives")
    c.setFont("Helvetica", 10)
    c.drawString(72, height - 200, "1. Deploy spatial IoT gas sensors in underground coal mine galleries.")
    c.drawString(72, height - 215, "2. Predict methane ventilation thresholds using edge machine learning models.")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(72, height - 250, "Proposed Methodology")
    c.setFont("Helvetica", 10)
    c.drawString(72, height - 270, "Hardware sensor node deployment integrated with spatial mesh networking.")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(72, height - 300, "Expected Outcomes")
    c.setFont("Helvetica", 10)
    c.drawString(72, height - 320, "1. Real-time CH4 alert system with sub-minute latency.")
    c.drawString(72, height - 335, "2. Reduced mine ventilation energy costs.")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(72, height - 370, "Estimated Cost")
    c.setFont("Helvetica", 10)
    c.drawString(72, height - 390, "Total Budget: Rs 48.50 Lakhs")
    c.drawString(72, height - 405, "Equipment: Rs 20.00 Lakhs")
    c.drawString(72, height - 420, "Personnel: Rs 18.50 Lakhs")
    c.drawString(72, height - 435, "Consumables: Rs 10.00 Lakhs")

    c.showPage()
    c.save()
    return output_path


def create_incomplete_proposal(output_path: Path) -> Path:
    """Generate SYNTHETIC TEST PROPOSAL B (Incomplete proposal missing methodology & containing arithmetic mismatch)."""
    c = canvas.Canvas(str(output_path), pagesize=letter)
    width, height = letter

    # Page 1
    c.setFont("Helvetica-Bold", 14)
    c.drawString(72, height - 72, "SYNTHETIC TEST PROPOSAL — NOT AN OFFICIAL CIL/NaCCER DOCUMENT")
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, height - 100, "Project Title: Bio-Leaching of Coal Tailings Dumps")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(72, height - 130, "Problem Statement")
    c.setFont("Helvetica", 10)
    c.drawString(72, height - 150, "Mineral recovery from coal refuse dumps requires biological extraction.")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(72, height - 180, "Project Objectives")
    c.setFont("Helvetica", 10)
    c.drawString(72, height - 200, "Microbial extraction of high purity minerals from tailing piles.")

    # Missing Methodology & Outcomes!

    c.setFont("Helvetica-Bold", 12)
    c.drawString(72, height - 250, "Estimated Cost")
    c.setFont("Helvetica", 10)
    c.drawString(72, height - 270, "Total Budget: Rs 30.00 Lakhs")
    c.drawString(72, height - 285, "Equipment: Rs 25.00 Lakhs")
    c.drawString(72, height - 300, "Personnel: Rs 15.00 Lakhs")  # Sum = 40 Lakhs vs Declared 30 Lakhs -> Mismatch!

    c.showPage()
    c.save()
    return output_path


if __name__ == "__main__":
    p_a = FIXTURES_DIR / "synthetic_proposal_complete.pdf"
    p_b = FIXTURES_DIR / "synthetic_proposal_incomplete.pdf"
    create_complete_proposal(p_a)
    create_incomplete_proposal(p_b)
    print(f"Generated synthetic proposals:\n  Complete: {p_a}\n  Incomplete: {p_b}")
