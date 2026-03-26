"""
sync_gsheets.py — Push cleaned/scored CSV data to Google Sheets master DB.

Usage:
    python scripts/sync_gsheets.py --sheet accounts --input data/processed/accounts_scored.csv
    python scripts/sync_gsheets.py --sheet contacts --input data/processed/contacts_clean.csv
    python scripts/sync_gsheets.py --sheet accounts --input data/processed/accounts_scored.csv --dry-run

Requirements:
    - data/credentials.json (Google service account key — gitignored)
    - GOOGLE_SHEETS_ID in .env

Upsert logic:
    - Matches on account_id (accounts sheet) or contact_id (contacts sheet).
    - Appends new rows; updates changed columns in existing rows.
    - Never deletes rows. Use status=Archived to retire records.
    - Safe to run multiple times (idempotent).
"""

import argparse
from datetime import date
from pathlib import Path

import pandas as pd

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import os

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
]

SHEET_KEY_COLUMNS = {
    "accounts": "account_id",
    "contacts": "contact_id",
    "weekly_log": "week_date",
}

SPREADSHEET_NAME = "South India Manufacturing Safety DB"


def _import_gspread():
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        return gspread, Credentials
    except (ImportError, Exception) as e:
        print(f"ERROR: Could not import gspread/google-auth: {e}")
        print("  Run: pip install gspread google-auth")
        raise SystemExit(1)


def get_client(credentials_path: str) -> "gspread.Client":
    gspread, Credentials = _import_gspread()
    creds = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
    return gspread.authorize(creds)


def get_or_create_sheet(spreadsheet, sheet_name: str):
    gspread, _ = _import_gspread()
    try:
        return spreadsheet.worksheet(sheet_name)
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=30)
        print(f"  Created new sheet: {sheet_name}")
        return ws


def sheet_to_df(worksheet: "gspread.Worksheet") -> pd.DataFrame:
    data = worksheet.get_all_records(default_blank="")
    if not data:
        return pd.DataFrame()
    return pd.DataFrame(data).astype(str)


def df_to_sheet_values(df: pd.DataFrame) -> list[list]:
    return [df.columns.tolist()] + df.fillna("").astype(str).values.tolist()


def upsert(existing_df: pd.DataFrame, new_df: pd.DataFrame, key_col: str) -> tuple[pd.DataFrame, int, int]:
    """Merge new_df into existing_df. Returns (merged_df, added_count, updated_count)."""
    added = 0
    updated = 0
    today = str(date.today())

    if existing_df.empty:
        new_df = new_df.copy()
        new_df["updated_at"] = today
        return new_df, len(new_df), 0

    existing_df = existing_df.copy()
    new_df = new_df.copy()

    # Ensure key column present in both
    if key_col not in existing_df.columns:
        existing_df[key_col] = ""
    if key_col not in new_df.columns:
        print(f"WARNING: key column '{key_col}' not found in input CSV. All rows will be appended.")
        new_df[key_col] = ""

    # Add any missing columns to existing_df
    for col in new_df.columns:
        if col not in existing_df.columns:
            existing_df[col] = ""

    existing_keys = set(existing_df[key_col].tolist())

    rows_to_add = []
    for _, row in new_df.iterrows():
        key_val = str(row.get(key_col, "")).strip()
        if not key_val or key_val not in existing_keys:
            row["updated_at"] = today
            rows_to_add.append(row)
            added += 1
        else:
            # Update existing row
            mask = existing_df[key_col] == key_val
            for col in new_df.columns:
                val = str(row.get(col, "")).strip()
                if val and col not in ("created_at", key_col):
                    existing_df.loc[mask, col] = val
            existing_df.loc[mask, "updated_at"] = today
            updated += 1

    if rows_to_add:
        append_df = pd.DataFrame(rows_to_add)
        merged = pd.concat([existing_df, append_df], ignore_index=True)
    else:
        merged = existing_df

    return merged, added, updated


def main():
    parser = argparse.ArgumentParser(description="Sync CSV data to Google Sheets master DB.")
    parser.add_argument("--sheet", required=True,
                        choices=["accounts", "contacts", "weekly_log"],
                        help="Which sheet to sync to")
    parser.add_argument("--input", required=True, help="Path to CSV file to sync")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be synced without writing to Sheets")
    parser.add_argument("--credentials", default="data/credentials.json",
                        help="Path to Google service account JSON key")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: File not found: {input_path}")
        raise SystemExit(1)

    if args.dry_run:
        new_df = pd.read_csv(input_path, dtype=str)
        print(f"Loaded {len(new_df)} rows from {input_path}")
        key_col = SHEET_KEY_COLUMNS[args.sheet]
        print(f"\nDRY RUN — would sync {len(new_df)} rows to sheet '{args.sheet}'")
        print(f"  Columns: {list(new_df.columns)}")
        if len(new_df) > 0:
            print(f"  Sample row: {new_df.iloc[0][['company_name', 'segment', 'hq_state', 'status']].to_dict() if 'company_name' in new_df.columns else new_df.iloc[0].to_dict()}")
        return

    sheets_id = os.environ.get("GOOGLE_SHEETS_ID", "")
    if not sheets_id:
        print("ERROR: GOOGLE_SHEETS_ID not set. Add it to your .env file.")
        raise SystemExit(1)

    credentials_path = args.credentials
    if not Path(credentials_path).exists():
        print(f"ERROR: Credentials file not found: {credentials_path}")
        print("  Place your Google service account JSON key at data/credentials.json")
        raise SystemExit(1)

    new_df = pd.read_csv(input_path, dtype=str)
    print(f"Loaded {len(new_df)} rows from {input_path}")

    key_col = SHEET_KEY_COLUMNS[args.sheet]
    print(f"Target sheet: {args.sheet} | Key column: {key_col}")

    print(f"Connecting to Google Sheets...")
    client = get_client(credentials_path)

    try:
        spreadsheet = client.open_by_key(sheets_id)
    except Exception as e:
        print(f"ERROR opening spreadsheet: {e}")
        raise SystemExit(1)

    worksheet = get_or_create_sheet(spreadsheet, args.sheet)
    existing_df = sheet_to_df(worksheet)
    print(f"  Existing rows in sheet: {len(existing_df)}")

    merged_df, added, updated = upsert(existing_df, new_df, key_col)

    # Write back to sheet
    values = df_to_sheet_values(merged_df)
    worksheet.clear()
    worksheet.update(values)

    print(f"\nSync complete:")
    print(f"  New rows added: {added}")
    print(f"  Existing rows updated: {updated}")
    print(f"  Total rows in sheet: {len(merged_df)}")


if __name__ == "__main__":
    main()
