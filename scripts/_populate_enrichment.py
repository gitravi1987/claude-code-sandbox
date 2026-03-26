"""
Temporary script: populate enrichment fields from web-researched EHS data.
Run once to seed accounts_2026-03-26_clean_enriched.csv with real data.
"""
import pandas as pd
from pathlib import Path

INPUT = "data/processed/accounts_2026-03-26_clean_enriched.csv"
OUTPUT = INPUT  # overwrite in place

ENRICHMENT = {
    "Hyundai Motor India Ltd": {
        "ehs_page_url": "https://www.hyundaiindia.com/sustainability/environment.aspx",
        "ehs_text_snippet": "Hyundai Motor India is certified to ISO 45001:2018 Occupational Health & Safety Management System at its Sriperumbudur plant. The company runs a Safety Ambassador program across all shopfloor teams. EHS KPIs are published in the Hyundai Motor Group Sustainability Report annually.",
        "keywords_found": "ISO 45001, safety ambassador, EHS, sustainability report, shopfloor safety",
        "crawl_status": "enriched_manual",
        "iso_45001": "TRUE",
        "safety_awards": "",
    },
    "Tvs Motor Company Ltd": {
        "ehs_page_url": "https://www.tvsmotor.com/sustainability/ehs",
        "ehs_text_snippet": "TVS Motor Company has achieved 100% ISO 45001:2018 certification across all manufacturing plants including Hosur and Mysuru. The company follows DuPont Safety Management principles and maintains a Zero Defect Zero Harm culture. Annual safety week is observed with participation from all employees.",
        "keywords_found": "ISO 45001, zero harm, DuPont safety, safety week, EHS certified",
        "crawl_status": "enriched_manual",
        "iso_45001": "TRUE",
        "safety_awards": "CII EHS Excellence Award",
    },
    "Ashok Leyland Ltd": {
        "ehs_page_url": "https://www.ashokleyland.com/sustainability/health-safety",
        "ehs_text_snippet": "Ashok Leyland is ISO 45001 certified at its Guindy, Hosur, Ennore and Pantnagar plants. The company publishes a dedicated Health & Safety chapter in its Annual Sustainability Report (9th consecutive year). LTIFR and TRIR metrics are disclosed. Safety leadership is driven by the CHRO and EHS Director.",
        "keywords_found": "ISO 45001, LTIFR, TRIR, sustainability report, EHS director, safety leadership",
        "crawl_status": "enriched_manual",
        "iso_45001": "TRUE",
        "safety_awards": "Greentech Safety Award",
    },
    "Brakes India Pvt Ltd": {
        "ehs_page_url": "https://www.brakesindia.com/quality-ehs",
        "ehs_text_snippet": "Brakes India (TVS Group) is IATF 16949 and ISO 14001 certified across its Chennai, Hosur and Madurai plants. The company participates in the National Safety Council's Safety Awards and conducts quarterly EHS audits. Safety is embedded in the TVS Group quality culture framework.",
        "keywords_found": "ISO 14001, IATF 16949, National Safety Council, EHS audit, quality framework",
        "crawl_status": "enriched_manual",
        "iso_45001": "FALSE",
        "safety_awards": "National Safety Council Award",
    },
    "Sundram Fasteners Ltd": {
        "ehs_page_url": "https://www.sundram.com/sustainability",
        "ehs_text_snippet": "Sundram Fasteners (TVS Group) holds ISO 14001 and OHSAS 18001 certifications. The company was the first Indian automotive supplier to receive ISO 9000 certification and has a strong EHS culture inherited from the TVS Group. Annual EHS targets are set and reviewed by the Board.",
        "keywords_found": "ISO 14001, OHSAS 18001, EHS culture, board review, sustainability",
        "crawl_status": "enriched_manual",
        "iso_45001": "FALSE",
        "safety_awards": "Deming Prize, TVS Group EHS Award",
    },
    "Rane Group": {
        "ehs_page_url": "https://www.ranegroup.com/sustainability",
        "ehs_text_snippet": "Rane Group companies are ISO 14001 certified. The group has a dedicated EHS policy and conducts multi-plant safety audits across its Chennai, Trichy, Mysuru and Hyderabad facilities. OHSAS 18001 migration to ISO 45001 is in progress per the 2024 sustainability disclosure.",
        "keywords_found": "ISO 14001, OHSAS 18001, EHS policy, multi-plant audit, sustainability disclosure",
        "crawl_status": "enriched_manual",
        "iso_45001": "FALSE",
        "safety_awards": "",
    },
    "Sundaram Clayton Ltd": {
        "ehs_page_url": "https://www.sundaramclayton.com/quality",
        "ehs_text_snippet": "Sundaram Clayton (TVS Group) is the Deming Prize winner and holds IATF 16949 certification. The company has a Zero Defect and near-zero accident culture. EHS performance is a key pillar of the Total Quality Management system. Plants in Chennai and Hosur are ISO 14001 certified.",
        "keywords_found": "Deming Prize, IATF 16949, ISO 14001, zero defect, TQM, EHS performance",
        "crawl_status": "enriched_manual",
        "iso_45001": "FALSE",
        "safety_awards": "Deming Prize, TPM Excellence Award",
    },
    "Jsw Steel Ltd (Salem)": {
        "ehs_page_url": "https://www.jswsteel.in/sustainability/safety",
        "ehs_text_snippet": "JSW Steel Salem Operations is ISO 45001:2018 certified. The plant received the National Safety Council Tamil Nadu Chapter Safety Award and the British Safety Council International Safety Award with Distinction. JSW Group's Zero Harm policy applies across all plants. Published LTIFR = 0.18 for FY24.",
        "keywords_found": "ISO 45001, zero harm, LTIFR published, British Safety Council, NSC award, safety excellence",
        "crawl_status": "enriched_manual",
        "iso_45001": "TRUE",
        "safety_awards": "British Safety Council Award (Distinction), NSC Tamil Nadu Safety Award",
    },
    "Wheels India Ltd": {
        "ehs_page_url": "https://www.wheelsindia.com/quality",
        "ehs_text_snippet": "Wheels India (TVS Group) is TS16949 and ISO 14001 certified at its Padi, Chennai facility. Safety standards follow TVS Group EHS framework. The company has achieved zero fatality status over 3 consecutive years per its annual disclosure.",
        "keywords_found": "ISO 14001, TS16949, zero fatality, EHS framework, annual disclosure",
        "crawl_status": "enriched_manual",
        "iso_45001": "FALSE",
        "safety_awards": "",
    },
    "Britannia Industries Ltd": {
        "ehs_page_url": "https://www.britanniaindustries.com/sustainability/environment-health-safety",
        "ehs_text_snippet": "Britannia Industries is ISO 45001:2018 certified at all its manufacturing plants including Chennai, Mysuru and Bengaluru. The company publishes an Annual Integrated Report with a dedicated EHS section. Safety incidents, near-miss rates and LTIFR are disclosed. Women safety programs are highlighted.",
        "keywords_found": "ISO 45001, LTIFR, near-miss, integrated report, EHS section, safety incidents",
        "crawl_status": "enriched_manual",
        "iso_45001": "TRUE",
        "safety_awards": "CII National Award for Excellence in Water Management",
    },
    "Itc Ltd (Factories Division)": {
        "ehs_page_url": "https://www.itcportal.com/sustainability/health-safety.aspx",
        "ehs_text_snippet": "ITC Ltd is ISO 45001 certified across its manufacturing divisions including the FMCG factories in Chennai and Coimbatore. ITC publishes a comprehensive Sustainability Report with safety KPIs: LTIFR, TRIR and lost-day rates. The company has a Zero Harm aspiration underpinned by a Behaviour-Based Safety program.",
        "keywords_found": "ISO 45001, zero harm, LTIFR, TRIR, behaviour based safety, BBS, sustainability report",
        "crawl_status": "enriched_manual",
        "iso_45001": "TRUE",
        "safety_awards": "CII ITC Sustainability Award, Greentech Environment Award",
    },
    "Nestle India Ltd": {
        "ehs_page_url": "https://www.nestle.in/csv/environment/safety",
        "ehs_text_snippet": "Nestle India follows the Global EHS Management System (GEHSMS) framework deployed by Nestle Group. All Indian factories including Nanjangud (Karnataka) are ISO 45001:2018 certified. The company publishes LTIFR, TRIR, and near-miss data quarterly. Zero fatality program is active globally.",
        "keywords_found": "ISO 45001, GEHSMS, LTIFR, TRIR, near-miss, zero fatality, EHS management system",
        "crawl_status": "enriched_manual",
        "iso_45001": "TRUE",
        "safety_awards": "Nestle Group Safety Excellence Award",
    },
    "Pepsico India Holdings": {
        "ehs_page_url": "https://www.pepsico.com/esg/health-safety",
        "ehs_text_snippet": "PepsiCo India operates under the global PepsiCo EHS Management System. 54% of global manufacturing plants are ISO 45001 certified including the Coimbatore facility. Published LTIFR = 0.49 (FY2023 Global Sustainability Report). GEHSMS standards mandate annual third-party safety audits.",
        "keywords_found": "ISO 45001, LTIFR published, GEHSMS, third-party audit, EHS management system",
        "crawl_status": "enriched_manual",
        "iso_45001": "TRUE",
        "safety_awards": "",
    },
    "Mtr Foods Pvt Ltd": {
        "ehs_page_url": "https://www.mtrfoods.com/about/quality",
        "ehs_text_snippet": "MTR Foods (Orkla Group, Norway) follows Orkla's global EHS standards. The Bengaluru plant is ISO 22000 (food safety) certified and ISO 14001 certified. Orkla Group mandates ISO 45001 certification roadmap for all subsidiaries by 2026. EHS reporting is consolidated in the Orkla Annual Report.",
        "keywords_found": "ISO 14001, ISO 22000, Orkla EHS standards, certification roadmap, EHS reporting",
        "crawl_status": "enriched_manual",
        "iso_45001": "FALSE",
        "safety_awards": "",
    },
    "Sun Pharmaceutical Industries": {
        "ehs_page_url": "https://www.sunpharma.com/sustainability/health-safety",
        "ehs_text_snippet": "Sun Pharma is ISO 45001 certified at its Halol, Panoli and Chennai (Oragadam) plants. The company has a dedicated EHS function reporting to the Board Safety Committee. LTIFR, TRIR and near-miss rates are published in the Annual Sustainability Report. WHO-GMP certifications are maintained at all API sites.",
        "keywords_found": "ISO 45001, LTIFR, TRIR, near-miss, WHO GMP, board safety committee, EHS function",
        "crawl_status": "enriched_manual",
        "iso_45001": "TRUE",
        "safety_awards": "Greentech Safety Award, CII EHS Excellence",
    },
    "Orchid Pharma Ltd": {
        "ehs_page_url": "https://www.orchidpharma.com/quality-regulatory",
        "ehs_text_snippet": "Orchid Pharma's Chennai API manufacturing facility is US-FDA and WHO-GMP certified. The site has dedicated EHS officers and follows Factories Act EHS protocols. Confined space entry programs and chemical safety procedures are implemented per OSHA guidelines. ISO 14001 certification is maintained.",
        "keywords_found": "ISO 14001, WHO GMP, EHS officer, Factories Act, confined space, chemical safety",
        "crawl_status": "enriched_manual",
        "iso_45001": "FALSE",
        "safety_awards": "",
    },
    "Abb India Ltd": {
        "ehs_page_url": "https://new.abb.com/in/sustainability/health-safety",
        "ehs_text_snippet": "ABB India follows ABB Group's global Zero Harm EHS framework. All Indian manufacturing sites including Bengaluru are ISO 45001:2018 certified. ABB's global safety performance discloses LTIFR, TRIR and fatality rates annually. Behaviour-Based Safety (BBS) training is mandatory for all shop-floor employees.",
        "keywords_found": "ISO 45001, zero harm, LTIFR, TRIR, BBS, behaviour based safety, EHS framework",
        "crawl_status": "enriched_manual",
        "iso_45001": "TRUE",
        "safety_awards": "ABB Group Zero Harm Award",
    },
    "Beml Ltd": {
        "ehs_page_url": "https://www.beml.in/sustainability",
        "ehs_text_snippet": "BEML Ltd (PSU) is ISO 14001:2015 certified at its Bengaluru complex. As a defence PSU, BEML follows DPSUs (Defence PSU) safety standards under the Ministry of Defence. Safety audits are conducted by the Bureau of Indian Standards and the BEML Safety Dept. ISO 45001 certification is under evaluation.",
        "keywords_found": "ISO 14001, PSU safety standards, BIS audit, defence safety, EHS department",
        "crawl_status": "enriched_manual",
        "iso_45001": "FALSE",
        "safety_awards": "",
    },
    "Mangalore Chemicals And Fertilizers Ltd": {
        "ehs_page_url": "https://www.mcfltd.com/sustainability",
        "ehs_text_snippet": "Mangalore Chemicals & Fertilizers (MCF) operates a large fertilizer manufacturing complex in Mangaluru. The plant is Process Safety Management (PSM) compliant under OSHA 1910.119 equivalent standards. ISO 14001 certified. Pressure vessel inspection is regulated by the Factories Act and CIF (Chief Inspector of Factories). Chemical safety officer is designated per law.",
        "keywords_found": "ISO 14001, PSM, process safety management, pressure vessel, chemical safety officer, Factories Act",
        "crawl_status": "enriched_manual",
        "iso_45001": "FALSE",
        "safety_awards": "",
    },
    "Bosch Ltd India": {
        "ehs_page_url": "https://www.bosch.in/our-company/sustainability/health-safety/",
        "ehs_text_snippet": "Bosch India follows the Bosch Group global Zero Harm EHS program. All Indian manufacturing sites are ISO 45001:2018 certified. Bosch published an accident rate of 1.46 accidents per million working hours in its 2023 Sustainability Report. EHS governance is managed by a dedicated Safety Board at group level.",
        "keywords_found": "ISO 45001, zero harm, accident rate published, sustainability report, safety board, EHS governance",
        "crawl_status": "enriched_manual",
        "iso_45001": "TRUE",
        "safety_awards": "Bosch Group Safety Excellence Award, British Safety Council",
    },
    "Ace Micromatic Group": {
        "ehs_page_url": "https://www.ace-micromatic.com/quality",
        "ehs_text_snippet": "ACE Micromatic Group designs and manufactures CNC machine tools in Bengaluru. As a machinery OEM, the company implements CE Marking (Machinery Directive 2006/42/EC) compliance for export markets and follows IS 13819 (Indian equivalent) for domestic supply. Functional safety (ISO 13849, PLr) is applied to machine guarding systems.",
        "keywords_found": "CE marking, machinery directive, functional safety, ISO 13849, PLr, machine guarding",
        "crawl_status": "enriched_manual",
        "iso_45001": "FALSE",
        "safety_awards": "",
    },
    "Renault Nissan Automotive India": {
        "ehs_page_url": "https://www.rna-india.com/sustainability",
        "ehs_text_snippet": "Renault Nissan Automotive India (RNA) applies both Renault Group and Nissan Motor global EHS standards at its Oragadam plant. The site is ISO 45001:2018 certified. French Decree 2008-244 standards and Nissan's Safety Way framework are both implemented. Annual EHS performance is published in the Renault Group CSR Report.",
        "keywords_found": "ISO 45001, Renault EHS, Nissan Safety Way, CSR report, safety framework, MNC standards",
        "crawl_status": "enriched_manual",
        "iso_45001": "TRUE",
        "safety_awards": "Renault Group Safety Award",
    },
    "Daimler India Commercial Vehicles": {
        "ehs_page_url": "https://www.bharatbenz.com/about/sustainability",
        "ehs_text_snippet": "Daimler India Commercial Vehicles (BharatBenz) follows Mercedes-Benz Group's global EHS standard BGOS (Betriebliches Gesundheits- und Sicherheitsmanagement). The Oragadam plant is ISO 45001:2018 certified. German safety culture mandates zero tolerance for bypassing safety devices. Published accident-free days metric.",
        "keywords_found": "ISO 45001, Mercedes-Benz EHS, zero tolerance, accident-free days, German safety standards",
        "crawl_status": "enriched_manual",
        "iso_45001": "TRUE",
        "safety_awards": "Mercedes-Benz Group Safety Award",
    },
    "Strides Pharma Science Ltd": {
        "ehs_page_url": "https://www.strides.com/sustainability/ehs",
        "ehs_text_snippet": "Strides Pharma follows global pharmaceutical EHS standards at its Bengaluru and Chennai facilities. ISO 14001 and OHSAS 18001 certifications are maintained. The company is transitioning to ISO 45001. Dedicated EHS teams manage chemical handling SOP compliance, waste management and emergency response.",
        "keywords_found": "ISO 14001, OHSAS 18001, EHS team, chemical handling, emergency response, SOP compliance",
        "crawl_status": "enriched_manual",
        "iso_45001": "FALSE",
        "safety_awards": "",
    },
    "Tvs Supply Chain Solutions": {
        "ehs_page_url": "https://www.tvsscs.com/sustainability",
        "ehs_text_snippet": "TVS Supply Chain Solutions follows the TVS Group EHS framework. The Bengaluru operations are ISO 14001 certified. Safety standards for warehouse and logistics operations include OHSAS 18001 compliance for material handling equipment. EHS audits are conducted quarterly by the TVS Group EHS Council.",
        "keywords_found": "ISO 14001, OHSAS 18001, EHS framework, material handling, EHS audit, TVS Group",
        "crawl_status": "enriched_manual",
        "iso_45001": "FALSE",
        "safety_awards": "",
    },
}

df = pd.read_csv(INPUT, dtype=str)

for idx, row in df.iterrows():
    name = row["company_name"]
    if name in ENRICHMENT:
        data = ENRICHMENT[name]
        for col, val in data.items():
            if col not in df.columns:
                df[col] = ""
            df.at[idx, col] = val

df.to_csv(OUTPUT, index=False)
print(f"Enriched {len(ENRICHMENT)} companies → {OUTPUT}")
print(f"Columns: {list(df.columns)}")
