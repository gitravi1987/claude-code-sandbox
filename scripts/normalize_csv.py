"""
normalize_csv.py — Clean and standardize raw account/contact CSV exports.

Usage:
    python scripts/normalize_csv.py --input data/raw/sales_nav_export.csv
    python scripts/normalize_csv.py --input data/raw/export.csv --source Perplexity
    python scripts/normalize_csv.py --input data/raw/export.csv --output data/processed/clean.csv
"""

import argparse
import uuid
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd

# ── Column name normalization map ────────────────────────────────────────────
COLUMN_ALIASES = {
    "company name": "company_name",
    "account name": "company_name",
    "organization": "company_name",
    "company": "company_name",
    "website": "website",
    "company website": "website",
    "url": "website",
    "industry": "segment",
    "industry vertical": "segment",
    "headcount": "employee_band",
    "company headcount": "employee_band",
    "employees": "employee_band",
    "number of employees": "employee_band",
    "location": "plant_locations",
    "headquarters": "hq_state",
    "city": "plant_locations",
    "state": "hq_state",
    "linkedin": "linkedin_company_url",
    "linkedin company page url": "linkedin_company_url",
    "profile url": "linkedin_company_url",
    "revenue": "turnover_band",
    "annual revenue": "turnover_band",
}

# ── Segment keyword mapping ───────────────────────────────────────────────────
SEGMENT_KEYWORDS = {
    "Automotive": ["automotive", "auto components", "auto parts", "vehicle", "tyre", "tire",
                   "stamping", "forging", "casting", "transmission", "axle", "brake",
                   "motor company", "leyland", "fastener", "clayton", "rane", "wheels india",
                   "renault", "nissan", "daimler", "bharatbenz", "bosch", "2-wheeler",
                   "car assembly", "truck", "commercial vehicle", "two-wheeler"],
    "Pharma": ["pharma", "pharmaceutical", "drug", "medicine", "api", "formulation",
               "life sciences", "biotech", "generics"],
    "FMCG/F&B": ["fmcg", "food", "beverage", "dairy", "snack", "consumer goods",
                 "packaged food", "confectionery", "edible", "rice", "flour"],
    "Packaging": ["packaging", "corrugated", "flexible packaging", "rigid packaging",
                  "carton", "container", "bottle", "can", "label"],
    "Metals": ["steel", "metal", "aluminium", "aluminum", "copper", "iron", "rolling",
               "wire rod", "tube", "pipe", "alloy", "foundry"],
    "Chemicals": ["chemical", "specialty chemical", "paint", "coating", "adhesive",
                  "ink", "resin", "polymer", "petrochemical", "fertiliser", "fertilizer"],
    "Machinery": ["machinery", "machine tool", "equipment", "engineering", "industrial",
                  "pump", "valve", "compressor", "conveyor", "automation", "robotics"],
    "Textiles": ["textile", "garment", "spinning", "weaving", "apparel", "fabric",
                 "yarn", "knitting", "dyeing"],
}

# ── State detection keywords ──────────────────────────────────────────────────
TN_KEYWORDS = ["tamil nadu", "chennai", "coimbatore", "hosur", "madurai", "trichy",
               "tiruchirappalli", "salem", "ambattur", "oragadam", "sriperumbudur",
               "tirunelveli", "erode", "tiruppur", "tn"]
KA_KEYWORDS = ["karnataka", "bengaluru", "bangalore", "mysuru", "mysore", "hubli",
               "dharwad", "mangaluru", "mangalore", "davangere", "tumkur", "belgaum",
               "belagavi", "ka", "kolar", "peenya"]

# ── Employee band normalization ───────────────────────────────────────────────
EMPLOYEE_BAND_MAP = [
    (5001, float("inf"), "5000+"),
    (1001, 5000, "1000-5000"),
    (501, 1000, "500-1000"),
    (0, 500, "<500"),
]


def normalize_column_name(col: str) -> str:
    clean = col.strip().lower().replace("-", " ").replace("/", " ")
    return COLUMN_ALIASES.get(clean, clean.replace(" ", "_"))


def infer_state(text: str) -> str:
    if not isinstance(text, str):
        return ""
    low = text.lower()
    if any(k in low for k in TN_KEYWORDS):
        return "TN"
    if any(k in low for k in KA_KEYWORDS):
        return "KA"
    return ""


def infer_segment(text: str) -> str:
    if not isinstance(text, str):
        return ""
    low = text.lower()
    for segment, keywords in SEGMENT_KEYWORDS.items():
        if any(k in low for k in keywords):
            return segment
    return "Other"


def normalize_employee_band(val) -> str:
    import re
    if pd.isna(val) or val == "":
        return ""
    raw = str(val).strip()
    # Pass through already-valid labels (e.g. "5000+", "1000-5000", "500-1000", "<500")
    if raw in ("5000+", "1000-5000", "500-1000", "<500"):
        return raw
    # Check for explicit "5000+" pattern before stripping "+"
    if "5000+" in raw or "5001" in raw or "10000" in raw:
        return "5000+"
    text = raw.lower().replace(",", "").replace("+", "")
    nums = re.findall(r"\d+", text)
    if not nums:
        return raw
    n = int(nums[0])
    for lo, hi, label in EMPLOYEE_BAND_MAP:
        if lo <= n <= hi:
            return label
    return raw


def fuzzy_match_score(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()


def flag_duplicates(df: pd.DataFrame, threshold: float = 0.85) -> pd.DataFrame:
    df = df.copy()
    df["duplicate_flag"] = ""
    names = df["company_name"].fillna("").tolist()
    for i in range(len(names)):
        if df.at[i, "duplicate_flag"]:
            continue
        for j in range(i + 1, len(names)):
            if fuzzy_match_score(names[i], names[j]) >= threshold:
                df.at[j, "duplicate_flag"] = f"Possible duplicate of row {i+2}: {names[i]}"
    return df


def ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    required = [
        "account_id", "company_name", "segment", "hq_state", "plant_locations",
        "employee_band", "turnover_band", "website", "linkedin_company_url",
        "source", "relevant_to", "priority", "status", "notes",
        "created_at", "updated_at", "duplicate_flag",
    ]
    for col in required:
        if col not in df.columns:
            df[col] = ""
    return df[required + [c for c in df.columns if c not in required]]


def main():
    parser = argparse.ArgumentParser(description="Normalize raw account CSV exports.")
    parser.add_argument("--input", required=True, help="Path to raw CSV file")
    parser.add_argument("--output", default="", help="Output path (default: data/processed/<name>_clean.csv)")
    parser.add_argument("--source", default="Manual",
                        choices=["SalesNav", "Perplexity", "IndustryDB", "Manual"],
                        help="Data source label")
    parser.add_argument("--relevant-to", default="Both",
                        choices=["Fortress", "VAYON", "Both"],
                        help="Which company this data is for")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: File not found: {input_path}")
        raise SystemExit(1)

    output_path = Path(args.output) if args.output else \
        Path("data/processed") / (input_path.stem + "_clean.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Reading: {input_path}")
    df = pd.read_csv(input_path, dtype=str)
    print(f"  Rows loaded: {len(df)}")

    # Normalize column names
    df.columns = [normalize_column_name(c) for c in df.columns]

    # Ensure company_name exists
    if "company_name" not in df.columns:
        print("ERROR: Could not find a company name column. Columns found:", list(df.columns))
        raise SystemExit(1)

    # Clean text fields
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()

    df["company_name"] = df["company_name"].str.title()

    # Infer hq_state if missing
    if "hq_state" not in df.columns:
        df["hq_state"] = ""
    location_source = df["plant_locations"] if "plant_locations" in df.columns else pd.Series([""] * len(df))
    missing_state = df["hq_state"].fillna("") == ""
    df.loc[missing_state, "hq_state"] = location_source[missing_state].apply(infer_state)

    # Infer segment if missing
    text_for_segment = (df.get("segment", pd.Series([""] * len(df))).fillna("") + " " +
                        df.get("company_name", pd.Series([""] * len(df))).fillna("") + " " +
                        df.get("notes", pd.Series([""] * len(df))).fillna(""))
    mask_no_segment = df.get("segment", pd.Series([""] * len(df))).fillna("") == ""
    if "segment" not in df.columns:
        df["segment"] = text_for_segment.apply(infer_segment)
    else:
        df.loc[mask_no_segment, "segment"] = text_for_segment[mask_no_segment].apply(infer_segment)

    # Normalize employee band
    if "employee_band" in df.columns:
        df["employee_band"] = df["employee_band"].apply(normalize_employee_band)

    # Assign UUIDs to new records
    def assign_id(val):
        if pd.isna(val) or str(val).strip() == "":
            return str(uuid.uuid4())
        return val

    if "account_id" not in df.columns:
        df["account_id"] = [str(uuid.uuid4()) for _ in range(len(df))]
    else:
        df["account_id"] = df["account_id"].apply(assign_id)

    # Source and defaults
    today = str(date.today())
    if "source" not in df.columns or df["source"].fillna("").eq("").all():
        df["source"] = args.source
    if "relevant_to" not in df.columns or df["relevant_to"].fillna("").eq("").all():
        df["relevant_to"] = args.relevant_to
    df["status"] = df.get("status", pd.Series([""] * len(df))).replace("", "New").fillna("New")
    df["priority"] = df.get("priority", pd.Series([""] * len(df))).replace("", "Medium").fillna("Medium")
    df["created_at"] = df.get("created_at", pd.Series([""] * len(df))).replace("", today).fillna(today)
    df["updated_at"] = today

    # Fuzzy duplicate detection
    df = df.reset_index(drop=True)
    df = flag_duplicates(df)
    dup_count = (df["duplicate_flag"] != "").sum()

    # Ensure all required columns present
    df = ensure_columns(df)

    df.to_csv(output_path, index=False)

    print(f"  Rows output: {len(df)}")
    print(f"  Duplicate flags: {dup_count} (review 'duplicate_flag' column)")
    print(f"  Written to: {output_path}")
    if dup_count > 0:
        print("  NOTE: Review flagged duplicates manually before syncing to Google Sheets.")


if __name__ == "__main__":
    main()
