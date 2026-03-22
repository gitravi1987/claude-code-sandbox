"""
weekly_report.py — Generate weekly priority report from Google Sheets master DB.

Usage:
    python scripts/weekly_report.py
    python scripts/weekly_report.py --output docs/weekly_report_2026-03-28.md
    python scripts/weekly_report.py --dry-run   # use local CSV instead of Sheets

Output sections:
    1. This Week's Activity Summary
    2. Top 10 Priority Accounts
    3. Follow-Up Due (contacts last touched >7 days ago)
    4. Leads to Enrich (accounts with no safety_score)
    5. Week-over-Week Trend (last 4 weeks from weekly_log)
"""

import argparse
import os
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]

STATUS_WEIGHT = {
    "Qualified": 1.0,
    "Engaged": 0.8,
    "New": 0.6,
    "Contacted": 0.4,
    "Proposal": 0.9,
    "Closed-Won": 0.0,
    "Closed-Lost": 0.0,
    "Archived": 0.0,
}

SIZE_WEIGHT = {
    "5000+": 1.0,
    "1000-5000": 0.66,
    "500-1000": 0.33,
    "<500": 0.1,
}


def get_client(credentials_path: str):
    creds = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
    return gspread.authorize(creds)


def load_sheet(spreadsheet, sheet_name: str) -> pd.DataFrame:
    try:
        ws = spreadsheet.worksheet(sheet_name)
        data = ws.get_all_records(default_blank="")
        return pd.DataFrame(data).astype(str) if data else pd.DataFrame()
    except Exception as e:
        print(f"  WARNING: Could not load sheet '{sheet_name}': {e}")
        return pd.DataFrame()


def priority_score(row: pd.Series) -> float:
    try:
        safety = float(row.get("safety_score", 0) or 0) / 100.0
    except ValueError:
        safety = 0.0

    size = SIZE_WEIGHT.get(str(row.get("employee_band", "")), 0.0)
    status = STATUS_WEIGHT.get(str(row.get("status", "New")), 0.4)

    # Recency: days since last contact (inverted, capped at 30)
    last = str(row.get("last_contact_date", "") or "")
    recency = 0.0
    if last:
        try:
            delta = (date.today() - datetime.strptime(last, "%Y-%m-%d").date()).days
            recency = max(0.0, 1.0 - (delta / 30.0))
        except ValueError:
            pass

    return safety * 0.4 + size * 0.3 + recency * 0.2 + status * 0.1


def format_account_row(row: pd.Series, score: float) -> str:
    name = row.get("company_name", "Unknown")
    status = row.get("status", "")
    band = row.get("score_band", "")
    safety = row.get("safety_score", "?")
    next_action = row.get("next_action", "")
    relevant = row.get("relevant_to", "Both")
    return (f"| {name} | {safety} | {band} | {status} | {relevant} | "
            f"{row.get('employee_band','')} | {next_action[:60] if next_action else '—'} | {score:.2f} |")


def format_contact_row(row: pd.Series) -> str:
    name = row.get("full_name", "Unknown")
    company = row.get("company_name", "")
    title = row.get("title", "")
    last = row.get("last_interaction", "?")
    status = row.get("connection_status", "")
    return f"| {name} | {company} | {title} | {last} | {status} |"


def build_report(accounts_df: pd.DataFrame, contacts_df: pd.DataFrame,
                 log_df: pd.DataFrame) -> str:
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    lines = []

    # Header
    lines.append(f"# Weekly Sales Report — Week of {week_start.strftime('%d %b %Y')}")
    lines.append(f"*Generated: {today.strftime('%d %b %Y')}*")
    lines.append("")

    # ── Section 1: Activity Summary ──────────────────────────────────────────
    lines.append("## 1. This Week's Activity")
    lines.append("")
    if accounts_df.empty:
        lines.append("*No account data available.*")
    else:
        # Count records created this week
        def created_this_week(df, col="created_at"):
            if col not in df.columns:
                return 0
            try:
                return (
                    pd.to_datetime(df[col], errors="coerce")
                    .dt.date
                    .apply(lambda d: d is not None and d >= week_start)
                    .sum()
                )
            except Exception:
                return 0

        acc_added = created_this_week(accounts_df)
        con_added = created_this_week(contacts_df, "created_at") if not contacts_df.empty else 0

        # Count outreach this week
        def outreach_count(df, col):
            if df.empty or col not in df.columns:
                return 0
            return (df[col].str.upper() == "TRUE").sum()

        connections = outreach_count(contacts_df, "connection_status") if not contacts_df.empty else 0
        emails = outreach_count(contacts_df, "email_sent") if not contacts_df.empty else 0
        whatsapp = outreach_count(contacts_df, "whatsapp_sent") if not contacts_df.empty else 0
        inmails = outreach_count(contacts_df, "inmail_sent") if not contacts_df.empty else 0

        lines.append(f"| Metric | Count |")
        lines.append(f"|---|---|")
        lines.append(f"| Accounts in DB | {len(accounts_df)} |")
        lines.append(f"| Accounts added this week | {acc_added} |")
        lines.append(f"| Contacts in DB | {len(contacts_df)} |")
        lines.append(f"| Contacts added this week | {con_added} |")
        lines.append(f"| LinkedIn connections sent (total) | {connections} |")
        lines.append(f"| InMails sent (total) | {inmails} |")
        lines.append(f"| Emails sent (total) | {emails} |")
        lines.append(f"| WhatsApp sent (total) | {whatsapp} |")
    lines.append("")

    # ── Section 2: Top 10 Priority Accounts ──────────────────────────────────
    lines.append("## 2. Top 10 Priority Accounts")
    lines.append("")
    if accounts_df.empty:
        lines.append("*No account data available.*")
    else:
        active = accounts_df[
            ~accounts_df.get("status", pd.Series()).isin(
                ["Closed-Won", "Closed-Lost", "Archived"]
            )
        ].copy()
        active["_priority_score"] = active.apply(priority_score, axis=1)
        top10 = active.nlargest(10, "_priority_score")

        lines.append("| Company | Safety Score | Band | Status | For | Employees | Next Action | Priority Score |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for _, row in top10.iterrows():
            lines.append(format_account_row(row, row["_priority_score"]))
    lines.append("")

    # ── Section 3: Follow-Up Due ──────────────────────────────────────────────
    lines.append("## 3. Follow-Up Due")
    lines.append("*Contacts where last interaction was >7 days ago and status is Contacted or Engaged.*")
    lines.append("")
    if contacts_df.empty:
        lines.append("*No contact data available.*")
    else:
        cutoff = today - timedelta(days=7)

        def needs_followup(row):
            status = str(row.get("connection_status", "")).strip()
            if status not in ("Connected", "Request Sent"):
                return False
            last = str(row.get("last_interaction", "") or "")
            if not last:
                return True
            try:
                return datetime.strptime(last, "%Y-%m-%d").date() <= cutoff
            except ValueError:
                return False

        due = contacts_df[contacts_df.apply(needs_followup, axis=1)]
        if due.empty:
            lines.append("*No follow-ups due. Great work!*")
        else:
            lines.append(f"**{len(due)} contacts need follow-up:**")
            lines.append("")
            lines.append("| Name | Company | Title | Last Interaction | Connection Status |")
            lines.append("|---|---|---|---|---|")
            for _, row in due.iterrows():
                lines.append(format_contact_row(row))
    lines.append("")

    # ── Section 4: Leads to Enrich ────────────────────────────────────────────
    lines.append("## 4. Accounts Pending Enrichment")
    lines.append("*Accounts with no safety score — website crawl not yet run.*")
    lines.append("")
    if accounts_df.empty:
        lines.append("*No account data available.*")
    else:
        no_score = accounts_df[
            accounts_df.get("safety_score", pd.Series()).fillna("").isin(["", "nan", "None"])
        ]
        if no_score.empty:
            lines.append("*All accounts have been enriched.*")
        else:
            lines.append(f"**{len(no_score)} accounts need enrichment:**")
            lines.append("")
            lines.append("| Company | Website | Source | Created |")
            lines.append("|---|---|---|---|")
            for _, row in no_score.head(20).iterrows():
                lines.append(f"| {row.get('company_name','')} | {row.get('website','')} | "
                             f"{row.get('source','')} | {row.get('created_at','')} |")
    lines.append("")

    # ── Section 5: Week-over-Week Trend ──────────────────────────────────────
    lines.append("## 5. Week-over-Week Trend (from weekly_log)")
    lines.append("")
    if log_df.empty:
        lines.append("*No weekly log data yet. This will populate after first Friday report.*")
    else:
        recent = log_df.tail(4)
        lines.append("| Week | Accounts Added | Contacts Added | Connections | Emails | Meetings |")
        lines.append("|---|---|---|---|---|---|")
        for _, row in recent.iterrows():
            lines.append(
                f"| {row.get('week_date','')} | {row.get('accounts_added','')} | "
                f"{row.get('contacts_added','')} | {row.get('connections_sent','')} | "
                f"{row.get('emails_sent','')} | {row.get('meetings_booked','')} |"
            )
    lines.append("")

    lines.append("---")
    lines.append("*Report generated by `scripts/weekly_report.py`*")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate weekly priority report.")
    parser.add_argument("--output", default="",
                        help="Output markdown file path (default: docs/weekly_report_YYYY-MM-DD.md)")
    parser.add_argument("--credentials", default="data/credentials.json",
                        help="Path to Google service account JSON key")
    parser.add_argument("--dry-run", action="store_true",
                        help="Load from local CSVs instead of Google Sheets (for testing)")
    args = parser.parse_args()

    today = date.today()
    output_path = Path(args.output) if args.output else \
        Path("docs") / f"weekly_report_{today.strftime('%Y-%m-%d')}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        print("DRY RUN: Loading from local CSVs")
        accounts_df = pd.read_csv("data/processed/accounts_scored.csv", dtype=str) \
            if Path("data/processed/accounts_scored.csv").exists() else pd.DataFrame()
        contacts_df = pd.read_csv("data/processed/contacts_clean.csv", dtype=str) \
            if Path("data/processed/contacts_clean.csv").exists() else pd.DataFrame()
        log_df = pd.DataFrame()
    else:
        sheets_id = os.environ.get("GOOGLE_SHEETS_ID", "")
        if not sheets_id:
            print("ERROR: GOOGLE_SHEETS_ID not set in .env")
            raise SystemExit(1)
        if not GSPREAD_AVAILABLE:
            print("ERROR: gspread not installed. Run: pip install gspread google-auth")
            raise SystemExit(1)
        if not Path(args.credentials).exists():
            print(f"ERROR: Credentials file not found: {args.credentials}")
            raise SystemExit(1)

        print("Connecting to Google Sheets...")
        client = get_client(args.credentials)
        spreadsheet = client.open_by_key(sheets_id)

        accounts_df = load_sheet(spreadsheet, "accounts")
        contacts_df = load_sheet(spreadsheet, "contacts")
        log_df = load_sheet(spreadsheet, "weekly_log")
        print(f"  Loaded: {len(accounts_df)} accounts, {len(contacts_df)} contacts")

    report = build_report(accounts_df, contacts_df, log_df)

    with open(output_path, "w") as f:
        f.write(report)

    print(f"\nReport written to: {output_path}")
    print("\n--- PREVIEW (first 30 lines) ---")
    for line in report.split("\n")[:30]:
        print(line)


if __name__ == "__main__":
    main()
