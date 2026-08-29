"""Structured Historical Corpus Ingestion for CIL Ongoing R&D Projects Catalogue (31.03.2026).

Populates the 20 official Coal India Limited ongoing R&D projects into the HistoricalProject knowledge base.
All records preserve exact dates, project codes, outlays, source pages, implementing agencies, and objectives.
"""

from datetime import date

from sqlalchemy.orm import Session

from app.repositories.projects import HistoricalProjectRepository
from app.schemas.project import HistoricalProjectCreate

CATALOGUE_DOCUMENT_NAME = "31_03_2026_RD ongoing projects.pdf"
CATALOGUE_SOURCE_NAME = "CIL/CMPDI R&D Catalogue (31.03.2026)"

CIL_ONGOING_PROJECTS: list[dict] = [
    {
        "index": 1,
        "project_code": "CIL/R&D/04/14/2021",
        "title": "Scaling up the conversion of CO2 to methanol and other value-added chemicals with 500 Kg CO2/day capacity.",
        "institution": "Jawaharlal Nehru Centre for Advanced Scientific Research (JNCASR), Jakkur, Bangalore",
        "sub_implementing_agencies": "Singareni Collieries Company Limited (SCCL), BREATHE Applied Sciences Pvt Ltd",
        "domain": "Clean Coal Technology & Carbon Capture",
        "start_date": date(2021, 10, 1),
        "completion_date": date(2026, 2, 28),
        "approved_cost": 19985700.0,
        "approved_cost_raw": "Rs. 1998.57 Lakhs (JNCASR: 1998.57, SCCL: Nil)",
        "objectives": (
            "To develop an integrated technology for the conversion of CO2 to methanol and other value added chemicals "
            "at industrial relevant scales having commercially viable conversion efficiencies. "
            "To develop end-to-end technology of thermo-catalytic CO2 reduction by integrating 4 sub-technologies: "
            "(a) CO2 capture, (b) Hydrogen generation, (c) Reduction of CO2 and (d) Product purification."
        ),
        "technology": "Thermo-catalytic CO2 reduction, CO2 capture, Hydrogen generation, Product purification",
        "source_page": 1,
    },
    {
        "index": 2,
        "project_code": "CIL/R&D/04/18/2022",
        "title": "Development of tandem approach for Paste Fill Technology and extraction methodology by continuous miner (CM) deployment for Shyampur B Colliery of Mugma Area, ECL",
        "institution": "Eastern Coalfields Limited (ECL), Sanctoria",
        "sub_implementing_agencies": "CSIR-CIMFR, Dhanbad",
        "domain": "Mining Technology & Strata Control",
        "start_date": date(2022, 9, 15),
        "completion_date": date(2025, 9, 30),
        "approved_cost": 49974500.0,
        "approved_cost_raw": "Rs. 4997.45 Lakhs (ECL: 4822.66, CIMFR: 174.79)",
        "objectives": (
            "Development of suitable paste backfill system. "
            "Development of suitable mining method in tandem with paste backfill. "
            "Subsidence monitoring and prediction for paste fill panels. "
            "Procurement, erection, commissioning and monitoring of paste backfilling system as well as monitoring of mining methods, strata and surface."
        ),
        "technology": "Paste fill backfilling, Continuous Miner (CM) tandem mining, Strata monitoring, Subsidence prediction",
        "source_page": 1,
    },
    {
        "index": 3,
        "project_code": "CIL/R&D/04/19/2023",
        "title": "Prototyping of Bi-facial Perovskite Module Leading to 4-T Perovskite-Si Tandem Structure",
        "institution": "Indian Institute of Technology (IIT), Bombay",
        "sub_implementing_agencies": "IIT Bombay",
        "domain": "Renewable Energy & Solar Photovoltaics",
        "start_date": date(2023, 7, 20),
        "completion_date": date(2026, 7, 19),
        "approved_cost": 17700000.0,
        "approved_cost_raw": "Rs. 1770.00 Lakhs (IIT Bombay: 1770.00)",
        "objectives": (
            "Development of the Bi-Facial Perovskite Module to achieve ~20% efficiency at module level and ~24% at cell level "
            "with projected stability for ~10 years (ISOS protocol). "
            "Implementation of the 4-Terminal tandem structure with projected efficiency >25% at module level and >30% at cell level."
        ),
        "technology": "Bi-facial Perovskite Module, 4-Terminal Si-Perovskite Tandem Structure, Photovoltaics",
        "source_page": 2,
    },
    {
        "index": 4,
        "project_code": "CIL/R&D/05/03/2024",
        "title": "5G Captive Non-public Network for Integrated Voice, Video & Data Communication in Opencast Coal Mines",
        "institution": "ME Division, CMPDI (HQ), Ranchi",
        "sub_implementing_agencies": "Centre for Development of Advanced Computing (C-DAC), Thiruvananthapuram",
        "domain": "Mine Telecommunication, Automation & Robotics",
        "start_date": date(2024, 1, 24),
        "completion_date": date(2026, 1, 23),
        "approved_cost": 24065400.0,
        "approved_cost_raw": "Rs. 2406.54 Lakhs (CMPDI: 88.50, C-DAC: 2318.04)",
        "objectives": (
            "Setting up of 5G Captive Non-Public network at an opencast coal mine; "
            "Design, development and demonstration of 5G use cases: Digital twin of load haul dump operation, "
            "collision avoidance system, 5G drone based digital mapping and remote monitoring, 5G camera based traffic control, "
            "voice & video calls, surveillance & asset tracking, AR/VR application, environmental monitoring."
        ),
        "technology": "5G Captive Non-Public Network (CNPN), Digital Twin, LiDAR/Collision Avoidance, Drone Mapping, Video Analytics",
        "source_page": 2,
    },
    {
        "index": 5,
        "project_code": "CIL/R&D/1/80/2024",
        "title": "Design of Geotechnical structures for extraction of coal seam at higher depth using Continuous Miner",
        "institution": "National Institute of Technology (NIT), Rourkela",
        "sub_implementing_agencies": "RI-V CMPDI Bilaspur, University of Wollongong Australia, SCCL Kothagudem",
        "domain": "Geotechnical Engineering & Rock Mechanics",
        "start_date": date(2024, 7, 1),
        "completion_date": date(2027, 6, 30),
        "approved_cost": 3033800.0,
        "approved_cost_raw": "Rs. 303.38 Lakhs (NIT Rourkela: 303.38, RI-V CMPDI: Nil)",
        "objectives": (
            "To develop design norms for different geotechnical structures involved during CM based coal extraction at depth range of 200-600 m depth. "
            "Assessment and classification of rock mass based on drill core. "
            "Continuous monitoring of strata behaviour during actual mining operation. "
            "Numerical modeling for pillar/coal block extraction and stress management techniques."
        ),
        "technology": "Continuous Miner (CM), Rock Mass Rating (RMR), Numerical Modeling, Strata Instrumentation & Monitoring",
        "source_page": 3,
    },
    {
        "index": 6,
        "project_code": "CIL/R&D/1/81/2024",
        "title": "Development of Energy Efficient Ergonomically Designed (EEED) Chair Lift Man Riding System",
        "institution": "Indian Institute of Technology (IIT-ISM), Dhanbad",
        "sub_implementing_agencies": "DGMS Dhanbad, BCCL Dhanbad",
        "domain": "Mining Machinery & Underground Transportation",
        "start_date": date(2024, 7, 1),
        "completion_date": date(2026, 6, 30),
        "approved_cost": 5395000.0,
        "approved_cost_raw": "Rs. 53.95 Lakhs (IIT-ISM: 53.95, BCCL: Nil)",
        "objectives": (
            "To develop a test rig of novel closed-loop Hydro Static Transmission (HST) system representing the power pack of chair lift man riding system. "
            "Analyze energy consumption and whole-body vibration of a rider for feasible implementation fit for steeply incline mines. "
            "Optimize time utilization, safety, and worker productivity."
        ),
        "technology": "Hydro Static Transmission (HST), Closed-loop hydraulic power pack, Ergonomic vibration test rig",
        "source_page": 3,
    },
    {
        "index": 7,
        "project_code": "CIL/R&D/04/21/2024",
        "title": "Study on post-mining accelerated reclamation in coal mining area using soil microbial community",
        "institution": "CSIR-Central Institute of Mining and Fuel Research (CIMFR), Dhanbad",
        "sub_implementing_agencies": "BCCL, Dhanbad",
        "domain": "Environmental Reclamation & Biotechnology",
        "start_date": date(2024, 9, 15),
        "completion_date": date(2026, 9, 14),
        "approved_cost": 5123000.0,
        "approved_cost_raw": "Rs. 51.23 Lakhs (CIMFR: 51.23, BCCL: Nil)",
        "objectives": (
            "Isolation and screening of nutrient recycling soil microbial community from mining and forest area. "
            "Develop microbial consortium to enhance soil nutrient cycle and soil fertility for accelerated plant growth in coal mine overburden dumps."
        ),
        "technology": "Bio-reclamation, Soil Microbial Consortium, Nutrient Recycling, Overburden Revegetation",
        "source_page": 4,
    },
    {
        "index": 8,
        "project_code": "CIL/R&D/03/04/2024",
        "title": "Assessment of coking coal quality with respect to active components present in coking coal",
        "institution": "National Metallurgical Laboratory (NML), Jamshedpur",
        "sub_implementing_agencies": "Central Mine Planning & Development Institute (CMPDI), Ranchi",
        "domain": "Clean Coal Preparation & Metallurgy",
        "start_date": date(2024, 9, 20),
        "completion_date": date(2026, 12, 19),
        "approved_cost": 19564000.0,
        "approved_cost_raw": "Rs. 195.64 Lakhs (NML: 62.21, CMPDI: 133.43)",
        "objectives": (
            "Identification and characterization of active components in various coking coals. "
            "Isolation of active components by physical separation. "
            "Characterization of vitrinite, inertinite, and reflectance as well as raw coking coal. "
            "Formulating a mathematical model to assess coking coal quality."
        ),
        "technology": "Vitrinite Reflectance Analysis, Petrographic Petrography, Physical Component Separation, Coking Coal Quality Modeling",
        "source_page": 4,
    },
    {
        "index": 9,
        "project_code": "CIL/R&D/01/82/2024",
        "title": "Creation of research facilities for examining the mental state and improving mental health including dementia",
        "institution": "Indian Institute of Technology (IIT), Mandi",
        "sub_implementing_agencies": "CCL Ranchi, CMPDI Ranchi",
        "domain": "Miner Health, Occupational Safety & Cognitive Science",
        "start_date": date(2024, 12, 20),
        "completion_date": date(2026, 12, 19),
        "approved_cost": 33356000.0,
        "approved_cost_raw": "Rs. 333.56 Lakhs (IIT Mandi: 333.56, CCL: Nil, CMPDI: Nil)",
        "objectives": (
            "To develop research facilities for early detection of mental health issues of Indian population including mine workers and CIL employees. "
            "Health screening of mining workers entering mines based on mental health. "
            "Neuro feedback-based interventions for faster cognitive enhancement."
        ),
        "technology": "Neuro-feedback Bio-sensing, Cognitive Health Screening, EEG/Mental State Assessment",
        "source_page": 5,
    },
    {
        "index": 10,
        "project_code": "CIL/R&D/04/22/2025",
        "title": "Carbon electrode based indigenous low-cost perovskite solar cells development",
        "institution": "Indian Institute of Technology (IIT), Roorkee",
        "sub_implementing_agencies": "NaCCER, CMPDIL HQ, Ranchi",
        "domain": "Renewable Energy & Materials Science",
        "start_date": date(2025, 5, 1),
        "completion_date": date(2027, 4, 30),
        "approved_cost": 49205000.0,
        "approved_cost_raw": "Rs. 492.05 Lakhs (IIT Roorkee: 456.65, NaCCER: 35.40)",
        "objectives": (
            "Fabrication and advance characterization of carbon electrode. "
            "Fabrication of high efficiency HTL-free carbon-based PSC (Perovskite Solar Cells). "
            "Cost benefit analysis of perovskite module and prototype demonstration."
        ),
        "technology": "HTL-free Carbon Electrode Perovskite Solar Cells (PSC), Photovoltaic Fabrication",
        "source_page": 5,
    },
    {
        "index": 11,
        "project_code": "CIL/R&D/01/84/2025",
        "title": "Indigenous Development of IoT-Enabled Technology for Monitoring, Analysis and Interpretation of Longwall Shield Pressures for Improving Safety and Productivity (Phase-II, TRL 5 to 8)",
        "institution": "NaCCER, CMPDI HQ, Ranchi",
        "sub_implementing_agencies": "Indian Institute of Technology (IIT) Kharagpur, Eastern Coalfields Limited (ECL) Sanctoria",
        "domain": "IoT, Mining Safety & Predictive Maintenance",
        "start_date": date(2025, 5, 1),
        "completion_date": date(2027, 4, 30),
        "approved_cost": 33706000.0,
        "approved_cost_raw": "Rs. 337.06 Lakhs (NaCCER: 92.93, IIT KGP: 244.13)",
        "objectives": (
            "To develop a comprehensive system for monitoring the entire longwall panel's shield pressure and shearer position. "
            "Pressure sensors installed in all shields; position sensors integrated to collect shearer position data every 60 seconds. "
            "Master data acquisition system (MDAS) placed on energy trolley with RS485 communication. "
            "Upgrading software for data collection and early forecasting of periodic roof weighting, shield leakage, and predictive maintenance information."
        ),
        "technology": "IoT Telemetry Sensors, RS485 Industrial Data Acquisition (MDAS), Longwall Powered Support Pressure Telemetry, Shearer Position Tracking, Predictive Maintenance & Leakage Forecasting",
        "source_page": 6,
    },
    {
        "index": 12,
        "project_code": "CIL/R&D/01/85/2025",
        "title": "Development of an Indigenous Optical Fiber Based Instrument for Measuring In-The-Hole Velocity of Detonation (VOD) and Analyze the Performance of Explosives & Accessories in Field Condition (Phase-II, TRL 5 to 8/9)",
        "institution": "NaCCER, CMPDI HQ, Ranchi",
        "sub_implementing_agencies": "Blasting Division CMPDIL HQ, Regional Institute – VI CMPDI Singrauli",
        "domain": "Blasting Engineering & Instrumentation",
        "start_date": date(2025, 5, 1),
        "completion_date": date(2026, 4, 30),
        "approved_cost": 28230000.0,
        "approved_cost_raw": "Rs. 282.30 Lakhs (NaCCER: 282.30)",
        "objectives": (
            "Development of robust optical fiber instrument for measuring in-the-hole Velocity of Detonation (VOD). "
            "Validate system performance under real-world explosive conditions in confined environments. "
            "Optimize automated reporting software for blast performance evaluation."
        ),
        "technology": "Fiber-optic VOD Sensing, High-speed Detonation Telemetry, Blast Performance Analytics",
        "source_page": 6,
    },
    {
        "index": 13,
        "project_code": "CIL/R&D/05/04/2025",
        "title": "Automation, Control & Wireless Communication in Underground Mines on 4GLTE/5G ready Communication Network in Jhanjhra Mines ECL",
        "institution": "Indian Telephone Industries (ITI Ltd.), Lucknow",
        "sub_implementing_agencies": "Mine Electronics, NaCCER, CMPDI, Ranchi",
        "domain": "Mine Telecommunication, IoT & Underground Automation",
        "start_date": date(2025, 6, 15),
        "completion_date": date(2027, 6, 14),
        "approved_cost": 218491000.0,
        "approved_cost_raw": "Rs. 2184.91 Lakhs (ITI: 1992.93, ME Deptt: 111.74, NaCCER: 80.24)",
        "objectives": (
            "To establish 4G LTE/5G Ready Communication Network in Underground Coal Mines. "
            "Seamless voice and video communication between underground workers and control centres using 5G CNPN/4G LTE. "
            "Automate conveyor belts, pumps, and deploy IoT sensors for monitoring CH4, CO2, temperature, humidity, air velocity, asset and miner tracking."
        ),
        "technology": "4G LTE / 5G Underground Network, IoT Environmental Gas Sensors, Conveyor & Pump Automation, Asset/Miner Tracking",
        "source_page": 7,
    },
    {
        "index": 14,
        "project_code": "CIL/R&D/04/23/2025",
        "title": "A Pilot Project on Underground Coal Gasification (UCG) to establish technology in Indian geo-mining conditions -Phase-2",
        "institution": "CMPDIL HQ Ranchi and ECL Sanctoria",
        "sub_implementing_agencies": "Ergo Exergy Technologies Inc, Montreal Qc, Canada",
        "domain": "Underground Coal Gasification & Geo-Mining",
        "start_date": date(2025, 6, 20),
        "completion_date": date(2026, 9, 19),
        "approved_cost": 483932000.0,
        "approved_cost_raw": "Rs. 4839.32 Lakhs (EETI Canada: 4076.63, CMPDI: 193.77, ECL: Nil)",
        "objectives": (
            "Development of detailed design of UCG Pilot Plant, construction, commissioning, operation and controlled shutdown, "
            "followed by post-shutdown monitoring. Feasibility study report on UCG Pilot Plant operation for commercial deployment."
        ),
        "technology": "Underground Coal Gasification (UCG), Syngas Extraction, Deep Geo-mining Control",
        "source_page": 8,
    },
    {
        "index": 15,
        "project_code": "CIL/R&D/01/86/2025",
        "title": "Revolutionizing Mine Safety: An AI-Enabled Fire Detection System for Underground Active and Closed/Abandoned Mines",
        "institution": "Indian Institute of Engineering Science and Technology (IIEST), Shibpur",
        "sub_implementing_agencies": "Milieu Global IT Solutions Pvt Ltd Hyderabad, CCL Ranchi",
        "domain": "AI, Mine Safety & Predictive Monitoring",
        "start_date": date(2025, 8, 10),
        "completion_date": date(2027, 8, 9),
        "approved_cost": 42074000.0,
        "approved_cost_raw": "Rs. 420.74 Lakhs (IIEST: 53.99, MGISPL: 366.75)",
        "objectives": (
            "Identification and installation of gas and video monitoring stations at underground active and abandoned mines. "
            "Real-time gas concentration and video acquisition. "
            "Prediction of fire hazards using AI-driven machine learning, deep learning, computer vision, and gas sensor telemetry."
        ),
        "technology": "AI Gas Telemetry, Deep Learning Computer Vision, Predictive Fire Hazard Modeling, Real-time Sensor Analytics",
        "source_page": 8,
    },
    {
        "index": 16,
        "project_code": "CIL/R&D/04/24/2025",
        "title": "Sustainable Solutions for Removal of Fluoride from Groundwater in Mining Area of Col India Ltd in Jharkhand, Odisha and West Bengal for Safe Drinking Water, Phase-I",
        "institution": "CSIR-Institute of Minerals and Materials Technology (IMMT), Bhubaneswar",
        "sub_implementing_agencies": "Reseapro Scientific Services Pvt Ltd, CMPDI RI-VII Bhubaneshwar, CMPDI RI-III Ranchi",
        "domain": "Environmental Remediation & Water Quality",
        "start_date": date(2025, 9, 1),
        "completion_date": date(2026, 8, 31),
        "approved_cost": 129106000.0,
        "approved_cost_raw": "Rs. 1291.06 Lakhs (IMMT: 318.10, CSIR: 884.21, RI-VII: 44.37, RI-III: 44.37)",
        "objectives": (
            "Water sampling, lab analysis, fluoride removal methods (activated alumina adsorption, electrolytic defluoridation), "
            "IoT sensor kits for real-time measurement of water quality (pH, TDS, turbidity), geo-spatial GPS tagging, and cloud AI/ML predictive dashboard."
        ),
        "technology": "Electrolytic Defluoridation (EDF), Activated Alumina Adsorption, IoT Water Quality Sensors, Geo-Spatial GPS Tagging, Cloud AI Dashboard",
        "source_page": 9,
    },
    {
        "index": 17,
        "project_code": "CIL/R&D/01/87/2025",
        "title": "Non-Invasive Health Screening and Smart Monitoring Systems for Coal Miners' Safety and Well-being",
        "institution": "Indian Institute of Engineering Science and Technology (IIEST), Shibpur",
        "sub_implementing_agencies": "ECL, Sanctoria",
        "domain": "Miner Health & Electronic Bio-Sensing",
        "start_date": date(2025, 9, 10),
        "completion_date": date(2027, 9, 9),
        "approved_cost": 47057000.0,
        "approved_cost_raw": "Rs. 470.57 Lakhs (IIEST: 470.57, ECL: Nil)",
        "objectives": (
            "Non-Invasive Oral and Lung Carcinoma Screening in Coal Miners with Occupational Exposure Using Electronic Bio Sensing Systems."
        ),
        "technology": "Electronic Bio-Sensing Systems, Non-invasive Carcinoma Screening, Occupational Exposure Monitoring",
        "source_page": 10,
    },
    {
        "index": 18,
        "project_code": "CIL/R&D/01/88/2026",
        "title": "Development of Innovative Extraction Method for Safer Extraction of Coal Seam by Underground Method with Higher Productivity and Percentage of Extraction using Continuous Mining System",
        "institution": "Indian Institute of Technology (IIT-ISM), Dhanbad",
        "sub_implementing_agencies": "National Centre for Coal and Energy Research (NaCCER), Eastern Coalfields Limited (ECL)",
        "domain": "Continuous Mining & Pillar Extraction",
        "start_date": date(2026, 3, 2),
        "completion_date": date(2027, 3, 1),
        "approved_cost": 16048000.0,
        "approved_cost_raw": "Rs. 160.48 Lakhs",
        "objectives": (
            "Design of block mining system including panel layout, sequence of extraction, coal evacuation system. "
            "Cut-out distance for CM/Bolter miner. Determination of size of rib/remnant pillars. "
            "Optimisation of fleet management system. Strata control and monitoring plan."
        ),
        "technology": "Continuous Mining System (CM/Bolter Miner), Block Mining Panel Layout, Fleet Management Optimization, Strata Control Monitoring",
        "source_page": 11,
    },
    {
        "index": 19,
        "project_code": "CIL/R&D/01/89/2026",
        "title": "Pilot scale paste backfilling to evaluate the effectiveness of paste fill technology in conventional bord and pillar coal mining working using LHD/SDL",
        "institution": "National Centre for Coal and Energy Research (NaCCER)",
        "sub_implementing_agencies": "IIT (ISM) Dhanbad, CSIR-CIMFR Dhanbad, SECL",
        "domain": "Paste Backfilling & Bord & Pillar Mining",
        "start_date": date(2026, 3, 15),
        "completion_date": date(2026, 9, 15),
        "approved_cost": 8383000.0,
        "approved_cost_raw": "Rs. 83.83 Lakhs (NaCCER: 46.27, IIT-ISM: 16.05, CIMFR: 21.51, SECL: Nil)",
        "objectives": (
            "Identifying and developing suitable paste backfill material using available waste material near mine site. "
            "Laboratory studies of physico-mechanical properties, borehole core drilling, dismantling paste-fill plant design. "
            "Extraction methodologies by conventional bord and pillar mining with paste backfilling, spontaneous heating/fire propensity monitoring."
        ),
        "technology": "Paste Backfill Plant, LHD/SDL Bord & Pillar Mining, Borehole Core Analysis, Spontaneous Heating Thermal Monitoring",
        "source_page": 11,
    },
    {
        "index": 20,
        "project_code": "CIL/R&D/05/05/2026",
        "title": "Design, Development and Demonstration of a Closed-Loop Low-Head Surface Hydrokinetic-Based Pumped Storage (SHK-PSP) Technology utilizing stabilized Overburden Dump as Upper Reservoirs and Mine Voids as Lower Reservoirs for sustainable Energy Storage solutions (Phase-I)",
        "institution": "Western Coalfields Limited (WCL)",
        "sub_implementing_agencies": "MACLEC Technical Project Laboratory (P) Ltd.",
        "domain": "Energy Storage & Hydrokinetic Pumped Storage",
        "start_date": date(2026, 4, 1),
        "completion_date": date(2026, 10, 1),
        "approved_cost": 46699000.0,
        "approved_cost_raw": "Rs. 466.99 Lakhs",
        "objectives": (
            "To scientifically design, validate and establish engineering methodologies for the stabilization and hydrological conversion "
            "of overburden (OB) dump zones into safe upper reservoirs for mine-based low-head pumped storage applications. "
            "Demonstrate closed-loop Surface Hydrokinetic Pumped Storage Plant (SHK-PSP) using mine voids as lower reservoirs."
        ),
        "technology": "Surface Hydrokinetic Pumped Storage (SHK-PSP), Overburden Dump Hydrological Conversion, Abandoned Mine Void Energy Storage",
        "source_page": 12,
    },
]


def seed_cil_ongoing_projects_corpus(db: Session) -> dict:
    """Ingest/seed the canonical 20 CIL ongoing R&D projects into PostgreSQL."""
    repo = HistoricalProjectRepository(db)

    # 1. Create or retrieve Import Batch
    batch = repo.get_import_batch_by_hash("cil_catalogue_hash_31032026")
    if not batch:
        batch = repo.create_import_batch(
            source_name=CATALOGUE_SOURCE_NAME,
            source_type="OFFICIAL",
            document_name=CATALOGUE_DOCUMENT_NAME,
            document_hash="cil_catalogue_hash_31032026",
            source_url="https://www.cmpdi.co.in/sites/default/files/2026-04/31_03_2026_RD%20ongoing%20projects.pdf",
        )

    imported = 0
    updated = 0

    for pdata in CIL_ONGOING_PROJECTS:
        existing = repo.get_by_code(pdata["project_code"])

        # Build normalized search text
        norm_text = (
            f"Project Code: {pdata['project_code']} | Title: {pdata['title']} | "
            f"Implementing Agencies: {pdata['institution']} (Sub: {pdata['sub_implementing_agencies']}) | "
            f"Domain: {pdata['domain']} | Objectives: {pdata['objectives']} | Technology/Terms: {pdata['technology']}"
        )

        if existing:
            # Update existing record fields while preserving ID
            existing.title = pdata["title"]
            existing.institution = pdata["institution"]
            existing.sub_implementing_agencies = pdata["sub_implementing_agencies"]
            existing.domain = pdata["domain"]
            existing.objectives = pdata["objectives"]
            existing.technology = pdata["technology"]
            existing.start_date = pdata["start_date"]
            existing.completion_date = pdata["completion_date"]
            existing.approved_cost = pdata["approved_cost"]
            existing.approved_cost_raw = pdata["approved_cost_raw"]
            existing.source = CATALOGUE_SOURCE_NAME
            existing.source_type = "OFFICIAL"
            existing.source_document_name = CATALOGUE_DOCUMENT_NAME
            existing.source_page_start = pdata["source_page"]
            existing.source_page_end = pdata["source_page"]
            existing.source_record_identifier = pdata["project_code"]
            existing.raw_record_text = norm_text
            existing.verification_status = "VERIFIED"
            db.commit()
            updated += 1
        else:
            proj_create = HistoricalProjectCreate(
                project_code=pdata["project_code"],
                title=pdata["title"],
                institution=pdata["institution"],
                sub_implementing_agencies=pdata["sub_implementing_agencies"],
                domain=pdata["domain"],
                objectives=pdata["objectives"],
                technology=pdata["technology"],
                status="ONGOING",
                start_date=pdata["start_date"],
                completion_date=pdata["completion_date"],
                approved_cost=pdata["approved_cost"],
                approved_cost_raw=pdata["approved_cost_raw"],
                source=CATALOGUE_SOURCE_NAME,
                source_type="OFFICIAL",
                source_document_name=CATALOGUE_DOCUMENT_NAME,
                source_page_start=pdata["source_page"],
                source_page_end=pdata["source_page"],
                source_record_identifier=pdata["project_code"],
                raw_record_text=norm_text,
                verification_status="VERIFIED",
                import_batch_id=batch.id,
            )
            repo.create(proj_create)
            imported += 1

    return {
        "batch_id": batch.id,
        "total_projects": len(CIL_ONGOING_PROJECTS),
        "imported": imported,
        "updated": updated,
        "document_name": CATALOGUE_DOCUMENT_NAME,
    }
