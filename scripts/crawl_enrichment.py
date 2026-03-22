"""
crawl_enrichment.py — Crawl public company websites for EHS/safety signals.

Usage:
    python scripts/crawl_enrichment.py --input data/processed/accounts_clean.csv
    python scripts/crawl_enrichment.py --input data/processed/accounts_clean.csv --delay 2
    python scripts/crawl_enrichment.py --input data/processed/accounts_clean.csv --dry-run

Compliance:
    - Only crawls publicly accessible URLs (no login required).
    - Respects robots.txt on all domains.
    - Rate-limited (default 1 req/sec per domain).
    - Never crawls linkedin.com or any social network.
"""

import argparse
import time
import urllib.robotparser
from datetime import date
from pathlib import Path
from urllib.parse import urljoin, urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup

# ── EHS path candidates to try ────────────────────────────────────────────────
EHS_PATHS = [
    "/",
    "/about",
    "/about-us",
    "/sustainability",
    "/esg",
    "/health-safety",
    "/health-and-safety",
    "/ehs",
    "/hse",
    "/safety",
    "/health",
    "/csr",
    "/environment",
    "/responsibility",
    "/corporate-responsibility",
]

# ── EHS keyword list (used to detect relevance) ───────────────────────────────
EHS_KEYWORDS = [
    "iso 45001", "ohsas 18001", "iso 14001",
    "zero harm", "zero accident", "zero injury", "zero fatality",
    "behaviour-based safety", "behavior-based safety", "bbs",
    "safety culture", "safety excellence", "safety award",
    "british safety council", "national safety council", "nsc award",
    "greentech award", "safety leadership",
    "ehs policy", "hse policy", "health and safety policy",
    "safety management system", "safety management",
    "lockout tagout", "loto", "machine guarding", "safety interlock",
    "risk assessment", "hazard identification",
    "ltifr", "trir", "lost time injury", "safety metrics", "safety statistics",
    "factories act", "pssr", "ce marking", "functional safety",
    "annual safety report", "safety report",
    "emergency response", "fire safety", "confined space",
    "personal protective equipment", "ppe",
]

BLOCKED_DOMAINS = {"linkedin.com", "facebook.com", "twitter.com", "instagram.com",
                   "youtube.com", "x.com"}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SafetyResearchBot/1.0; +https://vayon.in/bot)",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}


def normalize_url(website: str) -> str | None:
    if not isinstance(website, str) or not website.strip():
        return None
    url = website.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        parsed = urlparse(url)
        if parsed.netloc in BLOCKED_DOMAINS:
            return None
        return f"{parsed.scheme}://{parsed.netloc}"
    except Exception:
        return None


def get_robots_parser(base_url: str, session: requests.Session) -> urllib.robotparser.RobotFileParser:
    rp = urllib.robotparser.RobotFileParser()
    robots_url = urljoin(base_url, "/robots.txt")
    try:
        resp = session.get(robots_url, timeout=5, headers=HEADERS)
        rp.parse(resp.text.splitlines())
    except Exception:
        pass  # If robots.txt unavailable, proceed cautiously
    return rp


def fetch_page(url: str, session: requests.Session, timeout: int = 10) -> str | None:
    try:
        resp = session.get(url, timeout=timeout, headers=HEADERS, allow_redirects=True)
        if resp.status_code == 200 and "text/html" in resp.headers.get("content-type", ""):
            return resp.text
    except Exception:
        pass
    return None


def extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    return " ".join(soup.get_text(separator=" ").split())


def find_ehs_signals(text: str) -> list[str]:
    text_lower = text.lower()
    return [kw for kw in EHS_KEYWORDS if kw in text_lower]


def crawl_company(base_url: str, session: requests.Session, delay: float) -> dict:
    result = {
        "ehs_page_url": "",
        "ehs_text_snippet": "",
        "keywords_found": "",
        "crawl_status": "no_ehs_content",
    }

    robots = get_robots_parser(base_url, session)

    best_keywords: list[str] = []
    best_url = ""
    best_snippet = ""

    for path in EHS_PATHS:
        full_url = base_url + path
        if not robots.can_fetch("*", full_url):
            continue

        html = fetch_page(full_url, session)
        time.sleep(delay)

        if not html:
            continue

        text = extract_text(html)
        keywords = find_ehs_signals(text)

        if len(keywords) > len(best_keywords):
            best_keywords = keywords
            best_url = full_url
            best_snippet = text[:500]

        # Stop early if we found a rich EHS page
        if len(keywords) >= 5:
            break

    if best_keywords:
        result["ehs_page_url"] = best_url
        result["ehs_text_snippet"] = best_snippet
        result["keywords_found"] = ", ".join(best_keywords)
        result["crawl_status"] = "enriched"

    return result


def main():
    parser = argparse.ArgumentParser(description="Crawl public company websites for EHS signals.")
    parser.add_argument("--input", required=True, help="Path to cleaned accounts CSV")
    parser.add_argument("--output", default="", help="Output path (default: <input>_enriched.csv)")
    parser.add_argument("--delay", type=float, default=1.0,
                        help="Seconds between requests per domain (default: 1.0)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print URLs to crawl without fetching")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: File not found: {input_path}")
        raise SystemExit(1)

    output_path = Path(args.output) if args.output else \
        input_path.parent / (input_path.stem + "_enriched.csv")

    df = pd.read_csv(input_path, dtype=str)
    print(f"Loaded {len(df)} accounts from {input_path}")

    if "website" not in df.columns:
        print("ERROR: No 'website' column found.")
        raise SystemExit(1)

    # Initialize output columns
    for col in ["ehs_page_url", "ehs_text_snippet", "keywords_found", "crawl_status", "crawl_date"]:
        if col not in df.columns:
            df[col] = ""

    # Only crawl rows without existing enrichment or failed
    to_crawl = df[
        (df["website"].notna()) &
        (df["website"] != "") &
        (~df["crawl_status"].isin(["enriched"]))
    ].copy()

    print(f"Accounts to crawl: {len(to_crawl)}")

    if args.dry_run:
        for _, row in to_crawl.iterrows():
            url = normalize_url(row["website"])
            print(f"  Would crawl: {url} ({row.get('company_name', '?')})")
        return

    session = requests.Session()
    session.max_redirects = 5
    today = str(date.today())
    enriched = 0

    for idx, row in to_crawl.iterrows():
        base_url = normalize_url(row["website"])
        company = row.get("company_name", f"row {idx}")

        if not base_url:
            df.at[idx, "crawl_status"] = "invalid_url"
            df.at[idx, "crawl_date"] = today
            continue

        print(f"  Crawling: {company} ({base_url})")
        result = crawl_company(base_url, session, args.delay)

        for col, val in result.items():
            df.at[idx, col] = val
        df.at[idx, "crawl_date"] = today

        if result["crawl_status"] == "enriched":
            enriched += 1
            kw_count = len(result["keywords_found"].split(", ")) if result["keywords_found"] else 0
            print(f"    Found {kw_count} keywords → {result['ehs_page_url']}")

    df.to_csv(output_path, index=False)
    print(f"\nDone. Enriched: {enriched}/{len(to_crawl)}")
    print(f"Written to: {output_path}")


if __name__ == "__main__":
    main()
