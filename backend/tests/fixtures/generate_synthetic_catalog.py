from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

FIXTURES_DIR = Path(__file__).resolve().parent


def create_synthetic_catalog(output_path: Path) -> Path:
    """Generate a synthetic CIL/CMPDI historical project catalog PDF for parser unit tests."""
    c = canvas.Canvas(str(output_path), pagesize=letter)
    width, height = letter

    # Page 1
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, height - 72, "LIST OF ONGOING R&D PROJECTS OF CIL")
    c.setFont("Helvetica", 10)
    c.drawString(72, height - 90, "As on 31st March 2026 — CMPDI Technical Sub-Committee")

    # Project 1
    c.setFont("Helvetica-Bold", 12)
    c.drawString(72, height - 130, "1. Project Code: CIL/MT/2026/01")
    c.setFont("Helvetica-Bold", 11)
    c.drawString(72, height - 150, "Title: Real-Time Methane Monitoring Using IoT Mesh Nodes")
    c.setFont("Helvetica", 10)
    c.drawString(72, height - 170, "Implementing Agency: IIT (ISM) Dhanbad")
    c.drawString(72, height - 185, "Approved Outlay: Rs. 48.50 Lakhs")
    c.drawString(72, height - 200, "Start Date: 01.04.2024    Completion Date: 31.03.2026")
    c.drawString(
        72, height - 215, "Objectives: Deploy wireless gas detection sensor network in underground coal mines."
    )

    # Project 2
    c.setFont("Helvetica-Bold", 12)
    c.drawString(72, height - 260, "2. Project Code: CIL/EE/2025/08")
    c.setFont("Helvetica-Bold", 11)
    c.drawString(72, height - 280, "Title: Microbial Bio-Leaching of Coal Mine Tailings")
    c.setFont("Helvetica", 10)
    c.drawString(72, height - 300, "Implementing Agency: CSIR-CIMFR Dhanbad")
    c.drawString(72, height - 315, "Approved Outlay: Rs. 35.00 Lakhs")
    c.drawString(72, height - 330, "Start Date: 01.10.2023    Completion Date: 30.09.2025")
    c.drawString(72, height - 345, "Objectives: Eco-friendly mineral recovery from tailing dumps.")
    c.showPage()

    c.save()
    return output_path


if __name__ == "__main__":
    catalog_file = FIXTURES_DIR / "synthetic_historical_catalog.pdf"
    create_synthetic_catalog(catalog_file)
    print(f"Generated synthetic catalog PDF at: {catalog_file}")
