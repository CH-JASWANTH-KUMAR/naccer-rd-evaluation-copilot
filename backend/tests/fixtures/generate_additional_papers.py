"""Generate additional real-world coal mining research paper PDF fixtures for Step 5 validation."""

from pathlib import Path

FIXTURES_DIR = Path(__file__).resolve().parent

def generate_dust_suppression_paper():
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        pdf_path = FIXTURES_DIR / "paper_coal_mine_dust_suppression.pdf"
        c = canvas.Canvas(str(pdf_path), pagesize=letter)

        # PAGE 1: Title, Authors, Abstract, Keywords, Introduction
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, 750, "Hydro-Dynamic Atomization and Ultrasonic Water Mist System")
        c.drawString(50, 730, "for Dust Suppression in Continuous Mining Operations")

        c.setFont("Helvetica", 10)
        c.drawString(50, 705, "Dr. Vikram Singh, Prof. Meera Banerjee")
        c.drawString(50, 690, "CSIR-CIMFR Dhanbad & ISM Dhanbad")
        c.drawString(50, 675, "DOI: 10.1016/j.mineng.2025.105911 | Published: 2025")

        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, 645, "1. Abstract")
        c.setFont("Helvetica", 10)
        text_p1 = (
            "Respirable coal dust generated during continuous miner shearer operations presents severe occupational safety "
            "and pneumoconiosis risks in underground coal mines. This paper evaluates a high-pressure hydro-dynamic atomization "
            "curtain operating at 45 L/min water delivery rate. Field experiments demonstrate an overall respirable dust reduction "
            "efficiency of 86.4% compared to conventional low-pressure spray nozzles."
        )
        y = 630
        for line in text_p1.split(". "):
            c.drawString(50, y, line + ".")
            y -= 15

        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y - 10, "Keywords:")
        c.setFont("Helvetica", 10)
        c.drawString(110, y - 10, "Dust suppression, Respirable coal dust, Hydro-dynamic atomization, Underground mining")

        y -= 40
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, "2. Introduction")
        c.setFont("Helvetica", 10)
        intro_text = (
            "Continuous mining shearers generate fine airborne dust particles below 10 micrometers. Conventional water sprays "
            "fail to capture sub-micron dust due to high droplet surface tension."
        )
        for line in intro_text.split(". "):
            c.drawString(50, y - 15, line + ".")
            y -= 15

        c.showPage()

        # PAGE 2: Methodology, Experimental Setup, Results
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, 750, "3. Methodology")
        c.setFont("Helvetica", 10)
        meth_text = (
            "We utilized Computational Fluid Dynamic (CFD) multi-phase spray modeling combined with Response Surface Methodology "
            "(RSM) optimization. Water pressure was varied from 3.5 MPa to 8.0 MPa."
        )
        y = 735
        for line in meth_text.split(". "):
            c.drawString(50, y, line + ".")
            y -= 15

        y -= 20
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, "4. Results")
        c.setFont("Helvetica", 10)
        res_text = (
            "At 6.5 MPa operational pressure, respirable dust concentration at the return airway dropped from 14.2 mg/m3 to "
            "1.93 mg/m3. The system achieved a total dust reduction of 86.4% and an F1-score of 0.885 for automated spray activation."
        )
        y -= 15
        for line in res_text.split(". "):
            c.drawString(50, y, line + ".")
            y -= 15

        c.save()
        print("Generated paper_coal_mine_dust_suppression.pdf")
    except Exception as e:
        print("Error generating dust suppression paper:", e)


def generate_roof_strata_paper():
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        pdf_path = FIXTURES_DIR / "paper_underground_roof_strata_monitoring.pdf"
        c = canvas.Canvas(str(pdf_path), pagesize=letter)

        # PAGE 1: Title, Abstract
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, 750, "Micro-Seismic Monitoring and Roof Fall Risk Prediction")
        c.drawString(50, 730, "using Acoustic Emission Telemetry in Underground Coal Mines")

        c.setFont("Helvetica", 10)
        c.drawString(50, 705, "Dr. K. V. Ramana, Dr. S. K. Roy")
        c.drawString(50, 690, "CSIR-CIMFR Regional Centre Nagpur")
        c.drawString(50, 675, "DOI: 10.1016/j.ijrmms.2025.108102 | Published: 2025")

        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, 645, "1. Abstract")
        c.setFont("Helvetica", 10)
        text_p1 = (
            "Roof fall accidents in underground bord-and-pillar coal mines cause critical casualties. "
            "This paper presents a multi-channel acoustic emission telemetry network for real-time strata movement monitoring. "
            "A total of 1.8 million micro-seismic events were recorded over a 12-month monitoring campaign."
        )
        y = 630
        for line in text_p1.split(". "):
            c.drawString(50, y, line + ".")
            y -= 15

        c.showPage()

        # PAGE 2: Methodology & Results
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, 750, "2. Methodology & Machine Learning")
        c.setFont("Helvetica", 10)
        meth_text = (
            "We applied Convolutional Neural Networks (CNN) and Support Vector Regression (SVR) to classify acoustic emission "
            "energy counts. The sensor threshold was calibrated to an acoustic emission amplitude of 45 dB."
        )
        y = 735
        for line in meth_text.split(". "):
            c.drawString(50, y, line + ".")
            y -= 15

        y -= 20
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, "3. Results")
        c.setFont("Helvetica", 10)
        res_text = (
            "The micro-seismic roof fall forecasting model provided an early warning lead time of 36 hours prior to main roof collapse. "
            "The model achieved an overall accuracy of 92.5%, precision of 90.4%, recall of 92.6%, and F1-score of 0.915."
        )
        y -= 15
        for line in res_text.split(". "):
            c.drawString(50, y, line + ".")
            y -= 15

        c.save()
        print("Generated paper_underground_roof_strata_monitoring.pdf")
    except Exception as e:
        print("Error generating roof strata paper:", e)


if __name__ == "__main__":
    generate_dust_suppression_paper()
    generate_roof_strata_paper()
