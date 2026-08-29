from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "synthetic_rd_proposal_predictive_maintenance.pdf"

def generate_pdf():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(OUTPUT_PATH), pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=8
    )
    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=10,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#334155'),
        spaceAfter=6
    )

    story = []

    # Header / Title
    story.append(Paragraph("SYNTHETIC TEST PROPOSAL — NaCCER EVALUATION COPILOT TEST FIXTURE", body_style))
    story.append(Paragraph("Project Title: AI-Assisted Predictive Maintenance Framework for Coal Handling and Mining Equipment", title_style))
    story.append(Spacer(1, 4))

    # Meta
    story.append(Paragraph("<b>Host Institution:</b> CSIR-CIMFR [DEMO DATA]", body_style))
    story.append(Paragraph("<b>Principal Investigator:</b> Dr. Ananya Rao", body_style))
    story.append(Paragraph("<b>Research Domain:</b> Automation & Robotics in Mining", body_style))
    story.append(Spacer(1, 8))

    # Section 1: Problem Statement
    story.append(Paragraph("1. Problem Statement", heading_style))
    story.append(Paragraph("Unexpected mechanical failure of heavy coal handling machinery, conveyor belt gearboxes, and continuous miners causes severe production downtime and safety hazards in underground and opencast coal mines.", body_style))

    # Section 2: Project Objectives
    story.append(Paragraph("2. Project Objectives", heading_style))
    story.append(Paragraph("1. Deploy IoT vibration, thermal, and acoustic telemetry sensors across coal handling equipment.<br/>2. Train edge AI predictive maintenance models to forecast component failures 72 hours in advance.<br/>3. Deliver an automated maintenance alert dashboard for CIL mine engineers.", body_style))

    # Section 3: Technology
    story.append(Paragraph("3. Technology & Infrastructure", heading_style))
    story.append(Paragraph("Tri-axial vibration transducers, infrared thermal sensors, ATEX Zone 0 edge computing nodes, PyTorch ML inference models, and wireless mesh communication gateways.", body_style))

    # Section 4: Methodology
    story.append(Paragraph("4. Proposed Methodology", heading_style))
    story.append(Paragraph("Multi-sensor data acquisition from coal handling plant drives, feature extraction, continuous anomaly detection, and field trial validation at CSIR-CIMFR test rig and operating mine sites.", body_style))

    # Section 5: Experimental Validation Plan
    story.append(Paragraph("5. Experimental Validation Plan", heading_style))
    story.append(Paragraph("12-month pilot testing across 3 coal handling conveyors at CSIR-CIMFR facility followed by field deployment at an operating CIL underground coal mine.", body_style))

    # Section 6: Expected Outcomes
    story.append(Paragraph("6. Expected Outcomes & Deliverables", heading_style))
    story.append(Paragraph("1. Real-time predictive maintenance software suite for coal handling equipment.<br/>2. Reduction in unscheduled downtime by 35%.<br/>3. Field test report and operational manual.", body_style))

    # Section 7: Budget & Financial Breakdown
    story.append(Paragraph("7. Project Budget & Financial Breakdown", heading_style))
    story.append(Paragraph("<b>Total Requested Budget:</b> Rs. 48.50 Lakhs", body_style))
    story.append(Spacer(1, 4))

    table_data = [
        ["Cost Head Item", "Proposed Amount"],
        ["Equipment and sensor interfaces", "Rs. 18.00 Lakhs"],
        ["Project personnel", "Rs. 12.00 Lakhs"],
        ["Software and computing", "Rs. 6.50 Lakhs"],
        ["Field trials and travel", "Rs. 7.00 Lakhs"],
        ["Contingency", "Rs. 3.00 Lakhs"],
    ]

    t = Table(table_data, colWidths=[280, 160])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
    ]))
    story.append(t)
    story.append(Spacer(1, 8))

    # Section 8: Risk Analysis
    story.append(Paragraph("8. Risk Analysis & Mitigation", heading_style))
    story.append(Paragraph("Harsh underground environmental conditions (dust, moisture) may impair sensor longevity. Mitigation: IP67 ATEX-certified enclosures and redundant sensor channels.", body_style))

    # Section 9: Team Capability
    story.append(Paragraph("9. Team & Institutional Capability", heading_style))
    story.append(Paragraph("Principal Investigator: Dr. Ananya Rao, Senior Principal Scientist, CSIR-CIMFR Dhanbad.", body_style))

    # Section 10: References
    story.append(Paragraph("10. References", heading_style))
    story.append(Paragraph("1. CIL Mining Equipment Safety Guidelines (2025).", body_style))

    doc.build(story)
    print(f"Generated PDF fixture at: {OUTPUT_PATH}")

if __name__ == "__main__":
    generate_pdf()
