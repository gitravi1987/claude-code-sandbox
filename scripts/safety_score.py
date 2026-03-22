"""
safety_score.py — Compute Safety Maturity Score (0–100) per account from enrichment data.

Uses keyword matching on `keywords_found` and `ehs_text_snippet` columns.
See docs/safety_score_rubric.md for full scoring logic.

Usage:
    python scripts/safety_score.py --input data/processed/accounts_enriched.csv
    python scripts/safety_score.py --input data/processed/accounts_enriched.csv --explain
"""

import argparse
from pathlib import Path

import pandas as pd

# ── Scoring rubric ─────────────────────────────────────────────────────────────
# Format: (keyword_pattern, points, category, description)
# Points are additive but capped per category at max_points.

RUBRIC: list[tuple[str, int, str, str]] = [
    # Certifications (max 30)
    ("iso 45001", 20, "certifications", "ISO 45001 certified"),
    ("ohsas 18001", 15, "certifications", "OHSAS 18001 certified"),
    ("iso 14001", 10, "certifications", "ISO 14001 environmental management"),

    # Programs (max 20)
    ("zero harm", 10, "programs", "Zero Harm program"),
    ("zero accident", 8, "programs", "Zero Accident program"),
    ("zero injury", 8, "programs", "Zero Injury program"),
    ("behaviour-based safety", 5, "programs", "Behaviour-Based Safety (BBS)"),
    ("behavior-based safety", 5, "programs", "Behavior-Based Safety (BBS)"),
    ("bbs", 4, "programs", "BBS program"),
    ("safety culture", 5, "programs", "Safety Culture initiative"),
    ("safety leadership", 4, "programs", "Safety Leadership program"),

    # Awards (max 20)
    ("british safety council", 10, "awards", "British Safety Council award"),
    ("safety excellence award", 10, "awards", "Safety Excellence Award"),
    ("national safety council", 8, "awards", "National Safety Council award"),
    ("nsc award", 8, "awards", "NSC Award"),
    ("greentech award", 8, "awards", "Greentech Safety Award"),
    ("safety award", 6, "awards", "Safety Award (general)"),
    ("ehs award", 6, "awards", "EHS Award"),

    # Policy depth (max 15)
    ("annual safety report", 5, "policy_depth", "Annual Safety Report published"),
    ("safety report", 3, "policy_depth", "Safety report published"),
    ("ehs policy", 5, "policy_depth", "EHS Policy page present"),
    ("hse policy", 5, "policy_depth", "HSE Policy page present"),
    ("health and safety policy", 4, "policy_depth", "Health and Safety Policy page"),
    ("safety management system", 4, "policy_depth", "Safety Management System documented"),

    # Regulatory signals (max 10)
    ("factories act", 5, "regulatory", "Factories Act compliance mentioned"),
    ("pssr", 5, "regulatory", "PSSR/Pressure Systems safety"),
    ("machinery directive", 5, "regulatory", "Machinery Directive/CE Marking"),
    ("functional safety", 5, "regulatory", "Functional Safety (SIL/PLr) mentioned"),
    ("ce marking", 4, "regulatory", "CE Marking"),
    ("risk assessment", 3, "regulatory", "Risk assessment process mentioned"),

    # Incident transparency (max 5)
    ("ltifr", 5, "transparency", "LTIFR published"),
    ("trir", 5, "transparency", "TRIR published"),
    ("lost time injury", 4, "transparency", "Lost Time Injury rate published"),
    ("safety metrics", 3, "transparency", "Safety metrics/KPIs published"),
    ("safety statistics", 3, "transparency", "Safety statistics published"),
]

CATEGORY_CAPS = {
    "certifications": 30,
    "programs": 20,
    "awards": 20,
    "policy_depth": 15,
    "regulatory": 10,
    "transparency": 5,
}

SCORE_BANDS = {
    (76, 100): "Advanced",
    (51, 75): "Established",
    (21, 50): "Developing",
    (0, 20): "Basic",
}


def compute_score(text: str, explain: bool = False) -> tuple[int, dict, list[str]]:
    """
    Returns (total_score, category_scores, matched_signals).
    """
    if not isinstance(text, str):
        text = ""
    text_lower = text.lower()

    category_raw: dict[str, int] = {cat: 0 for cat in CATEGORY_CAPS}
    matched: list[str] = []

    for keyword, points, category, description in RUBRIC:
        if keyword in text_lower:
            category_raw[category] += points
            matched.append(description)

    # Apply category caps
    category_scores = {cat: min(category_raw[cat], CATEGORY_CAPS[cat]) for cat in CATEGORY_CAPS}
    total = min(sum(category_scores.values()), 100)

    return total, category_scores, matched


def get_score_band(score: int) -> str:
    for (lo, hi), band in SCORE_BANDS.items():
        if lo <= score <= hi:
            return band
    return "Unknown"


def extract_iso_45001(text: str) -> str:
    if not isinstance(text, str):
        return "Unknown"
    text_lower = text.lower()
    if "iso 45001" in text_lower:
        return "TRUE"
    if "ohsas 18001" in text_lower:
        return "TRUE"
    return "Unknown"


def extract_awards(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text_lower = text.lower()
    found = []
    award_keywords = [
        ("british safety council", "British Safety Council"),
        ("safety excellence award", "Safety Excellence Award"),
        ("nsc award", "NSC Award"),
        ("national safety council", "National Safety Council"),
        ("greentech award", "Greentech Award"),
    ]
    for kw, label in award_keywords:
        if kw in text_lower:
            found.append(label)
    return ", ".join(found)


def main():
    parser = argparse.ArgumentParser(description="Compute Safety Maturity Score per account.")
    parser.add_argument("--input", required=True, help="Path to enriched accounts CSV")
    parser.add_argument("--output", default="", help="Output path (default: <input>_scored.csv)")
    parser.add_argument("--explain", action="store_true",
                        help="Print score breakdown for each account")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: File not found: {input_path}")
        raise SystemExit(1)

    output_path = Path(args.output) if args.output else \
        input_path.parent / (input_path.stem + "_scored.csv")

    df = pd.read_csv(input_path, dtype=str)
    print(f"Loaded {len(df)} accounts from {input_path}")

    # Build combined text for scoring
    def combined_text(row):
        parts = [
            str(row.get("keywords_found", "") or ""),
            str(row.get("ehs_text_snippet", "") or ""),
            str(row.get("notes", "") or ""),
        ]
        return " ".join(parts)

    scores = []
    bands = []
    iso_list = []
    awards_list = []

    for idx, row in df.iterrows():
        company = row.get("company_name", f"row {idx}")
        text = combined_text(row)
        score, category_scores, matched = compute_score(text)

        scores.append(score)
        bands.append(get_score_band(score))
        iso_list.append(extract_iso_45001(text))
        awards_list.append(extract_awards(text))

        if args.explain:
            print(f"\n{company} — Score: {score}/100 ({get_score_band(score)})")
            for cat, pts in category_scores.items():
                print(f"  {cat}: {pts}/{CATEGORY_CAPS[cat]}")
            if matched:
                print(f"  Signals: {', '.join(matched)}")
            else:
                print("  No EHS signals found")

    df["safety_score"] = scores
    df["score_band"] = bands
    df["iso_45001"] = iso_list
    df["safety_awards"] = awards_list

    df.to_csv(output_path, index=False)

    # Summary
    scored = df[df["safety_score"].astype(str) != ""]
    print(f"\nScoring complete:")
    print(f"  Accounts scored: {len(scored)}")
    if len(scored) > 0:
        avg = scored["safety_score"].astype(float).mean()
        print(f"  Average score: {avg:.1f}/100")
        for band in ["Advanced", "Established", "Developing", "Basic"]:
            count = (scored["score_band"] == band).sum()
            print(f"  {band}: {count}")
    print(f"\nWritten to: {output_path}")


if __name__ == "__main__":
    main()
