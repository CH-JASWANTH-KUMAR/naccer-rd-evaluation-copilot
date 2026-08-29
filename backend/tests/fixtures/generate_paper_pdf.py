"""Generate synthetic coal mining predictive maintenance research paper PDF fixture."""

from pathlib import Path

FIXTURES_DIR = Path(__file__).resolve().parent

def generate_pdf():
    # We can write text content into PDF using reportlab or pypdf canvas/writer if reportlab is available, or use pypdf canvas.
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        pdf_path = FIXTURES_DIR / "synthetic_research_paper_predictive_maintenance.pdf"
        c = canvas.Canvas(str(pdf_path), pagesize=letter)

        # PAGE 1: Title, Authors, Abstract, Introduction
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, 750, "Vibration and Temperature Telemetry for Failure Prediction")
        c.drawString(50, 730, "in Coal Handling Conveyor Belts and Mining Equipment")
        
        c.setFont("Helvetica", 10)
        c.drawString(50, 705, "Dr. Rajesh Sharma, Prof. Amit K. Patel, Dr. Sunita Rao")
        c.drawString(50, 690, "CSIR-Central Institute of Mining and Fuel Research & IIT Kharagpur")
        c.drawString(50, 675, "DOI: 10.1016/j.coal.2025.104822 | Published: 2025")

        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, 645, "1. Abstract")
        c.setFont("Helvetica", 10)
        text_p1 = (
            "Predictive maintenance in underground and opencast coal mining operations requires reliable, "
            "low-latency telemetry for continuous equipment degradation monitoring. Mechanical failures in heavy "
            "coal handling equipment, such as longwall shearers, continuous miners, and conveyor belt idler rollers, "
            "cause severe production downtime and safety hazards. This paper presents an integrated IoT vibration and "
            "temperature telemetry framework combined with a novel Long Short-Term Memory (LSTM) autoencoder architecture "
            "for early failure forecasting and anomaly detection in mining equipment."
        )
        y = 630
        for line in text_p1.split(". "):
            c.drawString(50, y, line + ".")
            y -= 15

        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y - 10, "Keywords:")
        c.setFont("Helvetica", 10)
        c.drawString(110, y - 10, "Predictive maintenance, Vibration telemetry, Temperature monitoring, Anomaly detection, Coal handling equipment")

        y -= 40
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, "2. Introduction")
        c.setFont("Helvetica", 10)
        intro_text = (
            "Mining operations rely heavily on continuous mechanical equipment throughput. Unscheduled bearing failures "
            "and thermal overload in conveyor gearboxes account for over 38% of unplanned operational halts in coal processing. "
            "Traditional preventative maintenance routines miss transient micro-vibrations and localized temperature spikes."
        )
        for line in intro_text.split(". "):
            c.drawString(50, y - 15, line + ".")
            y -= 15

        c.showPage()

        # PAGE 2: Related Work & Methodology
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, 750, "3. Related Work")
        c.setFont("Helvetica", 10)
        rel_text = (
            "Previous studies on condition monitoring in underground mining relied on manual weekly vibration logging. "
            "Zhang et al. (2022) proposed FFT spectral analysis for fixed-speed motors, but failed under dynamic load fluctuations. "
            "Our approach extends continuous multi-sensor telemetry to dynamic mine load profiles."
        )
        y = 735
        for line in rel_text.split(". "):
            c.drawString(50, y, line + ".")
            y -= 15

        y -= 20
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, "4. Methodology")
        c.setFont("Helvetica", 10)
        meth_text = (
            "We deploy tri-axial MEMS accelerometers (sampling rate 10 kHz) and digital thermal RTD sensors directly "
            "on conveyor roller housings and longwall shield hydraulic power packs. RS485 Modbus telemetry feeds real-time "
            "time-series streams into an edge computing gateway. Feature extraction includes RMS vibration amplitude, kurtosis, "
            "crest factor, and moving-average temperature gradients."
        )
        y -= 15
        for line in meth_text.split(". "):
            c.drawString(50, y, line + ".")
            y -= 15

        c.showPage()

        # PAGE 3: Experimental Setup & Results
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, 750, "5. Experimental Setup")
        c.setFont("Helvetica", 10)
        exp_text = (
            "Field validation was conducted over a 9-month trial at Jhanjhra Underground Mine and Rajmahal Opencast Project. "
            "A dataset of 4.2 million time-series telemetry samples was collected across 64 operational conveyor idlers "
            "and 12 longwall powered supports."
        )
        y = 735
        for line in exp_text.split(". "):
            c.drawString(50, y, line + ".")
            y -= 15

        y -= 20
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, "6. Results")
        c.setFont("Helvetica", 10)
        res_text = (
            "The proposed LSTM vibration-temperature anomaly detection model achieved an overall precision of 94.2%, "
            "recall of 91.8%, and F1-score of 0.930 for bearing degradation detection. Early warning latency averaged 48 hours "
            "prior to catastrophic mechanical failure, reducing false alarm rate to under 2.1% across all field trials."
        )
        y -= 15
        for line in res_text.split(". "):
            c.drawString(50, y, line + ".")
            y -= 15

        c.showPage()

        # PAGE 4: Discussion, Conclusion & References
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, 750, "7. Discussion & Conclusion")
        c.setFont("Helvetica", 10)
        disc_text = (
            "Integrating multi-sensor vibration and thermal telemetry significantly enhances failure prediction accuracy in harsh "
            "mining environments. The field-validated model provides reliable early warning capabilities for maintenance engineers, "
            "enabling proactive component replacement before catastrophic mechanical failure."
        )
        y = 735
        for line in disc_text.split(". "):
            c.drawString(50, y, line + ".")
            y -= 15

        y -= 20
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, "8. References")
        c.setFont("Helvetica", 9)
        c.drawString(50, y - 15, "[1] Zhang, L., et al. (2022). FFT Spectral Analysis in Mine Conveyor Motors. Journal of Mining Tech, 45(2), 112-120.")
        c.drawString(50, y - 30, "[2] Sharma, R., & Patel, A. (2024). Wireless Sensor Networks for Underground Coal Mining. IEEE Sensors Journal, 24(8), 4501-4510.")

        c.save()
        print("PDF fixture generated successfully via ReportLab.")
    except Exception as e:
        print("ReportLab error:", e)

if __name__ == "__main__":
    generate_pdf()
