"""
create_sample_data.py — Generate realistic sample accounts CSV for pipeline testing.

Creates data/processed/sample_accounts.csv with 20 fictitious manufacturing companies
matching the South India ICP. Use this to test the full pipeline before real data arrives.

Usage:
    python scripts/create_sample_data.py
    python scripts/create_sample_data.py --rows 30
    python scripts/create_sample_data.py --output data/processed/test.csv
"""

import argparse
import uuid
from datetime import date
from pathlib import Path

import pandas as pd

# ── Sample data pools ─────────────────────────────────────────────────────────

SAMPLE_COMPANIES = [
    # Automotive — TN
    {"company_name": "Kaveri Auto Components Pvt Ltd", "segment": "Automotive",
     "hq_state": "TN", "plant_locations": "Hosur, Chennai",
     "employee_band": "1000-5000", "turnover_band": "500-1000Cr",
     "website": "https://www.bosch.com", "source": "SalesNav",
     "notes": "Tier-1 press shop. Hosur cluster. ISO 45001 likely."},

    # Automotive — KA
    {"company_name": "Deccan Precision Stampings Ltd", "segment": "Automotive",
     "hq_state": "KA", "plant_locations": "Bengaluru, Mysuru",
     "employee_band": "1000-5000", "turnover_band": "1000-5000Cr",
     "website": "https://www.mahindra.com", "source": "SalesNav",
     "notes": "Assembly + stamping. Bengaluru."},

    # FMCG — TN
    {"company_name": "Nilgiris Packaged Foods Ltd", "segment": "FMCG/F&B",
     "hq_state": "TN", "plant_locations": "Coimbatore, Madurai",
     "employee_band": "500-1000", "turnover_band": "500-1000Cr",
     "website": "https://www.itcportal.com", "source": "Perplexity",
     "notes": "Packaging lines, high-speed FMCG. Safety culture unknown."},

    # Pharma — TN
    {"company_name": "Sakthi Pharma Manufacturing Ltd", "segment": "Pharma",
     "hq_state": "TN", "plant_locations": "Chennai, Oragadam",
     "employee_band": "1000-5000", "turnover_band": "1000-5000Cr",
     "website": "https://www.sunpharma.com", "source": "IndustryDB",
     "notes": "API + formulations. Oragadam SEZ. ATEX zones likely."},

    # Metals — KA
    {"company_name": "Tungabhadra Steel Works Ltd", "segment": "Metals",
     "hq_state": "KA", "plant_locations": "Davangere, Hubli",
     "employee_band": "5000+", "turnover_band": "5000Cr+",
     "website": "https://www.jswsteel.in", "source": "SalesNav",
     "notes": "Rolling mill. Hot work risks. Zero Harm program."},

    # Packaging — TN
    {"company_name": "Coromandel Packaging Industries", "segment": "Packaging",
     "hq_state": "TN", "plant_locations": "Chennai, Trichy",
     "employee_band": "500-1000", "turnover_band": "500-1000Cr",
     "website": "https://www.uflex.com", "source": "Perplexity",
     "notes": "Corrugated + flexible. Slitter safety gap likely."},

    # Chemicals — KA
    {"company_name": "Western Ghats Specialty Chemicals", "segment": "Chemicals",
     "hq_state": "KA", "plant_locations": "Mangaluru, Bengaluru",
     "employee_band": "1000-5000", "turnover_band": "1000-5000Cr",
     "website": "https://www.pidiliteindustries.com", "source": "IndustryDB",
     "notes": "Specialty chemicals. ATEX classification required."},

    # Machinery OEM — TN
    {"company_name": "Kavindra Machine Tools Ltd", "segment": "Machinery",
     "hq_state": "TN", "plant_locations": "Coimbatore",
     "employee_band": "500-1000", "turnover_band": "500-1000Cr",
     "website": "https://www.lmttools.com", "source": "Manual",
     "notes": "CNC machine OEM. CE marking + risk assessment needed."},

    # FMCG — KA
    {"company_name": "Deccan Agro Processing Ltd", "segment": "FMCG/F&B",
     "hq_state": "KA", "plant_locations": "Mysuru, Bengaluru",
     "employee_band": "1000-5000", "turnover_band": "500-1000Cr",
     "website": "https://www.britanniaindustries.com", "source": "SalesNav",
     "notes": "Biscuit + snack manufacturing. Conveyor safety."},

    # Automotive — TN
    {"company_name": "Palar Valley Forging Works", "segment": "Automotive",
     "hq_state": "TN", "plant_locations": "Hosur, Salem",
     "employee_band": "500-1000", "turnover_band": "500-1000Cr",
     "website": "https://www.forvia.com", "source": "SalesNav",
     "notes": "Forging shop. Press safety, LOTO gaps."},

    # Pharma — KA
    {"company_name": "Bengaluru Biosynth Laboratories", "segment": "Pharma",
     "hq_state": "KA", "plant_locations": "Bengaluru",
     "employee_band": "1000-5000", "turnover_band": "1000-5000Cr",
     "website": "https://www.drreddys.com", "source": "Perplexity",
     "notes": "API manufacturing. Confined space + chemical handling."},

    # Metals — TN
    {"company_name": "Cauvery Metal Alloys Ltd", "segment": "Metals",
     "hq_state": "TN", "plant_locations": "Trichy, Salem",
     "employee_band": "1000-5000", "turnover_band": "1000-5000Cr",
     "website": "https://www.hindalco.com", "source": "IndustryDB",
     "notes": "Aluminum rolling. Overhead crane + hot work risks."},

    # Textiles — TN
    {"company_name": "Kongu Spinners & Weavers Ltd", "segment": "Other",
     "hq_state": "TN", "plant_locations": "Coimbatore, Tiruppur",
     "employee_band": "500-1000", "turnover_band": "500-1000Cr",
     "website": "https://www.vardhman.com", "source": "Manual",
     "notes": "Large spinning mill. Machinery guarding gaps."},

    # Packaging — KA
    {"company_name": "Sharavathi Paper & Board Mills", "segment": "Packaging",
     "hq_state": "KA", "plant_locations": "Shimoga, Davangere",
     "employee_band": "500-1000", "turnover_band": "500-1000Cr",
     "website": "https://www.ballarpur.com", "source": "Perplexity",
     "notes": "Paper + board. Press nip safety, slitter risks."},

    # Automotive MNC — TN
    {"company_name": "Vega Powertrain Systems India Pvt Ltd", "segment": "Automotive",
     "hq_state": "TN", "plant_locations": "Chennai, Oragadam",
     "employee_band": "5000+", "turnover_band": "5000Cr+",
     "website": "https://www.hyundai.com", "source": "SalesNav",
     "notes": "MNC. Assembly. ISO 45001 certified. Zero Harm program."},

    # Chemicals — TN
    {"company_name": "Madurai Industrial Coatings Ltd", "segment": "Chemicals",
     "hq_state": "TN", "plant_locations": "Madurai, Tuticorin",
     "employee_band": "500-1000", "turnover_band": "500-1000Cr",
     "website": "https://www.asianpaints.com", "source": "IndustryDB",
     "notes": "Paint + coatings. Solvent handling, ATEX."},

    # Machinery — KA
    {"company_name": "Tungabhadra Engineering Solutions", "segment": "Machinery",
     "hq_state": "KA", "plant_locations": "Bengaluru, Hubli",
     "employee_band": "500-1000", "turnover_band": "500-1000Cr",
     "website": "https://www.ace-micromatic.com", "source": "Manual",
     "notes": "Machine tool OEM. SIL/PLr functional safety opportunity."},

    # FMCG large — TN
    {"company_name": "South India Beverages Corporation", "segment": "FMCG/F&B",
     "hq_state": "TN", "plant_locations": "Chennai, Coimbatore, Salem",
     "employee_band": "5000+", "turnover_band": "5000Cr+",
     "website": "https://www.pepsico.com", "source": "SalesNav",
     "notes": "MNC. Bottling plant. ISO 45001 certified."},

    # Pharma — TN small-large
    {"company_name": "Ponni API Synthesis Pvt Ltd", "segment": "Pharma",
     "hq_state": "TN", "plant_locations": "Ambattur, Sriperumbudur",
     "employee_band": "500-1000", "turnover_band": "500-1000Cr",
     "website": "https://www.strides.com", "source": "IndustryDB",
     "notes": "API. Chemical handling safety gaps expected."},

    # Automotive KA large
    {"company_name": "Mysuru Transmission & Axle Ltd", "segment": "Automotive",
     "hq_state": "KA", "plant_locations": "Mysuru",
     "employee_band": "1000-5000", "turnover_band": "1000-5000Cr",
     "website": "https://www.sona.com", "source": "SalesNav",
     "notes": "Drivetrain components. Press shop + robotic cells."},
]


def create_sample_accounts(n: int) -> pd.DataFrame:
    today = str(date.today())
    rows = []
    pool = SAMPLE_COMPANIES * ((n // len(SAMPLE_COMPANIES)) + 1)

    for i in range(n):
        base = pool[i].copy()
        base["account_id"] = str(uuid.uuid4())
        base["safety_score"] = ""
        base["iso_45001"] = "Unknown"
        base["safety_awards"] = ""
        base["ehs_page_url"] = ""
        base["ehs_text_snippet"] = ""
        base["linkedin_company_url"] = ""
        base["relevant_to"] = "Both"
        base["priority"] = "Medium"
        base["status"] = "New"
        base["last_contact_date"] = ""
        base["next_action"] = "Enrich website → score → add EHS contact"
        base["created_at"] = today
        base["updated_at"] = today
        base["duplicate_flag"] = ""
        rows.append(base)

    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(
        description="Generate sample accounts CSV for pipeline testing.")
    parser.add_argument("--rows", type=int, default=20,
                        help="Number of sample rows to generate (default: 20)")
    parser.add_argument("--output", default="data/processed/sample_accounts.csv",
                        help="Output CSV path")
    args = parser.parse_args()

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    df = create_sample_accounts(args.rows)
    df.to_csv(out, index=False)

    print(f"Created {len(df)} sample accounts → {out}")
    print(f"\nColumn layout: {list(df.columns)}")
    print(f"\nNext steps:")
    print(f"  python scripts/crawl_enrichment.py --input {out} --dry-run")
    print(f"  python scripts/safety_score.py --input {out} --explain")
    print(f"  python scripts/sync_gsheets.py --sheet accounts --input {out} --dry-run")
    print(f"  python scripts/weekly_report.py --dry-run")


if __name__ == "__main__":
    main()
