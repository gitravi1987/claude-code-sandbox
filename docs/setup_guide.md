# Google Sheets Setup Guide

> Complete this once before running `sync_gsheets.py` or `weekly_report.py`.
> Estimated time: 20–30 minutes.

---

## Step 1: Create the Google Spreadsheet

1. Go to [sheets.google.com](https://sheets.google.com) and sign in with your business Google account.
2. Click **+ Blank spreadsheet**.
3. Rename it: click "Untitled spreadsheet" at the top → type `South India Manufacturing Safety DB` → press Enter.
4. Note the spreadsheet ID from the URL:
   ```
   https://docs.google.com/spreadsheets/d/THIS_IS_YOUR_SPREADSHEET_ID/edit
   ```
   Copy and save this ID — you'll need it in Step 4.

---

## Step 2: Create the Three Sheets with Headers

### Sheet 1: `accounts`

1. The default tab is called "Sheet1" — rename it: right-click the tab → Rename → type `accounts`.
2. Click cell **A1** and paste this entire row (tab-separated — easiest to copy from below into row 1):

```
account_id	company_name	segment	hq_state	plant_locations	employee_band	turnover_band	website	safety_score	iso_45001	safety_awards	ehs_page_url	ehs_text_snippet	linkedin_company_url	source	relevant_to	priority	status	last_contact_date	next_action	notes	created_at	updated_at
```

**Tip**: Paste into A1. Google Sheets will auto-split on tabs into separate columns.

### Sheet 2: `contacts`

1. Click the **+** button at the bottom to add a new sheet → rename it `contacts`.
2. Click cell **A1** and paste:

```
contact_id	account_id	company_name	full_name	title	persona_tag	linkedin_url	email	phone	connection_status	inmail_sent	email_sent	whatsapp_sent	last_interaction	notes
```

### Sheet 3: `weekly_log`

1. Add another sheet → rename it `weekly_log`.
2. Click cell **A1** and paste:

```
week_date	accounts_added	contacts_added	connections_sent	inmails_sent	emails_sent	whatsapp_sent	replies_received	meetings_booked	notes
```

---

## Step 3: Create a Google Service Account

A **service account** is a special Google account that lets Python scripts access your spreadsheet without requiring browser login.

### 3a. Go to Google Cloud Console

1. Open [console.cloud.google.com](https://console.cloud.google.com).
2. If you don't have a project: click **Select a project** → **New Project** → name it `safety-prospecting` → Create.
3. Select your project from the top dropdown.

### 3b. Enable APIs

1. In the left menu: **APIs & Services → Library**.
2. Search for **"Google Sheets API"** → click it → click **Enable**.
3. Go back to Library, search for **"Google Drive API"** → click it → click **Enable**.

### 3c. Create Service Account

1. Go to **APIs & Services → Credentials**.
2. Click **+ Create Credentials → Service account**.
3. Fill in:
   - **Service account name**: `safety-prospecting-bot`
   - **Service account ID**: auto-fills (leave as is)
   - Click **Create and Continue** → skip optional steps → click **Done**.

### 3d. Download JSON Key

1. In the **Service accounts** list, click on the account you just created.
2. Go to the **Keys** tab.
3. Click **Add Key → Create new key → JSON → Create**.
4. A `.json` file will download automatically.
5. Rename it to `credentials.json`.
6. Move it to your project folder: `data/credentials.json`.

> **IMPORTANT**: Never commit this file. It is already in `.gitignore`.

### 3e. Share the Spreadsheet with the Service Account

1. Open the downloaded `credentials.json` in a text editor.
2. Find the line: `"client_email": "something@project.iam.gserviceaccount.com"`
3. Copy that email address.
4. Open your Google Spreadsheet.
5. Click **Share** (top right) → paste the service account email → set role to **Editor** → click **Send**.

---

## Step 4: Create Your `.env` File

In the root of your project folder, create a file named `.env` (no extension):

```
GOOGLE_SHEETS_ID=your_spreadsheet_id_here
```

Replace `your_spreadsheet_id_here` with the ID you copied in Step 1.

> **IMPORTANT**: Never commit `.env`. It is already in `.gitignore`.

---

## Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Step 6: Test the Connection

Run a dry-run sync to verify everything is connected:

```bash
python scripts/create_sample_data.py
python scripts/sync_gsheets.py --sheet accounts --input data/processed/sample_accounts.csv --dry-run
```

Expected output:
```
Loaded 20 rows from data/processed/sample_accounts.csv
Target sheet: accounts | Key column: account_id
DRY RUN — would sync 20 rows to sheet 'accounts'
```

If you see that output, your setup is complete.

### Verify with a real sync (optional but recommended):

```bash
python scripts/sync_gsheets.py --sheet accounts --input data/processed/sample_accounts.csv
```

Check your Google Spreadsheet — the `accounts` sheet should now have 20 rows of sample data.

---

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `GOOGLE_SHEETS_ID not set` | Missing `.env` file or wrong env var name | Create `.env` with `GOOGLE_SHEETS_ID=...` |
| `Credentials file not found` | credentials.json not at `data/credentials.json` | Move the downloaded JSON to `data/credentials.json` |
| `403 Forbidden` | Service account not shared on spreadsheet | Re-do Step 3e — share the sheet with the service account email |
| `gspread.exceptions.SpreadsheetNotFound` | Wrong spreadsheet ID or no access | Check the ID in `.env` matches the URL; verify the sheet is shared with service account |
| `ModuleNotFoundError: gspread` | Dependencies not installed | Run `pip install -r requirements.txt` |

---

## Quick Reference: Column Headers (copy-paste)

### accounts sheet (row 1)
```
account_id	company_name	segment	hq_state	plant_locations	employee_band	turnover_band	website	safety_score	iso_45001	safety_awards	ehs_page_url	ehs_text_snippet	linkedin_company_url	source	relevant_to	priority	status	last_contact_date	next_action	notes	created_at	updated_at
```

### contacts sheet (row 1)
```
contact_id	account_id	company_name	full_name	title	persona_tag	linkedin_url	email	phone	connection_status	inmail_sent	email_sent	whatsapp_sent	last_interaction	notes
```

### weekly_log sheet (row 1)
```
week_date	accounts_added	contacts_added	connections_sent	inmails_sent	emails_sent	whatsapp_sent	replies_received	meetings_booked	notes
```
