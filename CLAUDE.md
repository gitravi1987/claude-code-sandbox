# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Purpose

Weekly AI-assisted prospecting system for selling machine safety solutions (audits, engineering controls, integration, training) to large manufacturers in Tamil Nadu and South Karnataka.

Two companies share one pipeline: **Fortress Safety** (products/services) and **VAYON Systems** (engineering/audits). Master database is Google Sheets. Python scripts handle normalization, website enrichment, safety scoring, and reporting. LinkedIn Sales Navigator is used **manually only — never automated**.

---

## Commands

```bash
# Install
pip install -r requirements.txt

# Create local data directories
mkdir -p data/raw data/processed

# Generate test data (no credentials needed)
python scripts/create_sample_data.py
python scripts/create_sample_data.py --rows 50 --output data/processed/custom.csv

# 1. Normalize raw CSV (Sales Nav, Perplexity, industry DB, manual)
python scripts/normalize_csv.py --input data/raw/sales_nav_2026-04-28.csv
python scripts/normalize_csv.py --input data/raw/FILE.csv --output data/processed/custom_clean.csv

# 2. Crawl company websites for EHS signals
python scripts/crawl_enrichment.py --input data/processed/accounts_clean.csv
python scripts/crawl_enrichment.py --input data/processed/accounts_clean.csv --delay 2
python scripts/crawl_enrichment.py --input data/processed/accounts_clean.csv --dry-run   # preview only

# 3. Compute Safety Maturity Score (0–100)
python scripts/safety_score.py --input data/processed/accounts_enriched.csv
python scripts/safety_score.py --input data/processed/accounts_enriched.csv --explain    # show per-signal breakdown

# 4. Sync to Google Sheets (requires credentials.json + .env)
python scripts/sync_gsheets.py --sheet accounts --input data/processed/accounts_scored.csv
python scripts/sync_gsheets.py --sheet contacts --input data/processed/contacts.csv
python scripts/sync_gsheets.py --sheet accounts --input FILE.csv --dry-run               # no credentials needed

# 5. Generate weekly report
python scripts/weekly_report.py
python scripts/weekly_report.py --output docs/weekly_report_2026-04-28.md
python scripts/weekly_report.py --dry-run --output docs/weekly_report_2026-04-28.md      # reads local CSVs, no Sheets

# Full pipeline (typical Tuesday run)
python scripts/normalize_csv.py --input data/raw/sales_nav_2026-04-28.csv
python scripts/crawl_enrichment.py --input data/processed/accounts_2026-04-28_clean.csv --delay 2
python scripts/safety_score.py --input data/processed/accounts_2026-04-28_clean_enriched.csv
python scripts/sync_gsheets.py --sheet accounts --input data/processed/accounts_2026-04-28_clean_enriched_scored.csv
```

---

## Pipeline Architecture

Linear, file-based pipeline. Each script reads one CSV and writes another — no shared state between scripts.

```
data/raw/*.csv
  → normalize_csv.py         → data/processed/*_clean.csv
  → crawl_enrichment.py      → data/processed/*_enriched.csv
  → safety_score.py          → data/processed/*_scored.csv
  → sync_gsheets.py          → Google Sheets (master DB)
  → weekly_report.py         → docs/weekly_report_YYYY-MM-DD.md
```

**Key design invariants:**
- **Idempotent**: every script skips already-processed rows (re-runnable)
- **Dry-run**: `sync_gsheets.py` and `crawl_enrichment.py` support `--dry-run` (no credentials, no writes)
- **Upsert, never delete**: `sync_gsheets.py` matches on `account_id`/`contact_id`, updates existing, appends new — rows are retired via `status="Archived"`, never removed
- **Flag, don't merge**: `normalize_csv.py` flags fuzzy duplicates (85% threshold) via `duplicate_flag=True` — human review required before syncing

---

## Google Sheets Setup

**Auth**: `data/credentials.json` (Google service account JSON key) + `GOOGLE_SHEETS_ID=...` in `.env`.  
**Spreadsheet name**: `South India Manufacturing Safety DB`  
**Sheets**: `accounts`, `contacts`, `weekly_log`  
See `docs/setup_guide.md` for full step-by-step Google Cloud Console instructions.

**accounts** columns: `account_id`, `company_name`, `segment`, `hq_state`, `plant_locations`, `employee_band` (500-1000/1000-5000/5000+), `turnover_band`, `website`, `safety_score`, `iso_45001` (TRUE/FALSE/Unknown), `safety_awards`, `ehs_page_url`, `ehs_text_snippet`, `linkedin_company_url`, `source`, `relevant_to` (Fortress/VAYON/Both), `priority` (High/Medium/Low), `status` (New/Contacted/Engaged/Qualified/Proposal/Closed-Won/Closed-Lost/Archived), `last_contact_date`, `next_action`, `notes`, `created_at`, `updated_at`

**contacts** columns: `contact_id`, `account_id` (FK), `company_name`, `full_name`, `title`, `persona_tag` (EHS/Plant/Ops/Production/Maintenance/CXO), `linkedin_url`, `email`, `phone`, `connection_status` (Not Connected/Request Sent/Connected), `inmail_sent`, `email_sent`, `whatsapp_sent`, `last_interaction`, `notes`

**weekly_log** columns: `week_date`, `accounts_added`, `contacts_added`, `connections_sent`, `inmails_sent`, `emails_sent`, `whatsapp_sent`, `replies_received`, `meetings_booked`, `notes`

---

## Safety Score (0–100)

Keyword-based proxy computed from `ehs_text_snippet`, `keywords_found`, and enrichment columns. See `docs/safety_score_rubric.md` for keyword lists.

| Category | Max pts | Top signals |
|---|---|---|
| Certifications | 30 | ISO 45001 (20), OHSAS 18001 (15), ISO 14001 (10) |
| Programs | 20 | Zero Harm (10), BBS (5), Safety Culture (5) |
| Awards | 20 | British Safety Council (10), NSC/Greentech (8) |
| Policy depth | 15 | Annual Safety Report (5), EHS Policy page (5) |
| Regulatory | 10 | Factories Act (5), Functional Safety/CE Marking (4–5) |
| Transparency | 5 | LTIFR published (5), TRIR published (5) |

Score bands: **Advanced** 76–100 · **Established** 51–75 · **Developing** 21–50 · **Basic** 0–20

Manual review recommended for scores in the 40–60 range.

---

## ICP and Personas

**Target accounts**: Non-MSME manufacturers, >500 Cr turnover (500+ employees proxy), TN + South KA.  
Segments: Automotive, Machinery, Packaging, FMCG/F&B, Pharma, Metals, Chemicals, Textiles (large plants).  
Disqualify: MSME (<250 Cr), pure services, existing Fortress/VAYON accounts.

**Personas** (for contact sourcing and message personalization):
- **EHS** (primary): EHS Head, HSE Manager, Safety Manager, Safety Officer, EHS Director
- **Plant** (primary): Plant Head, Factory Manager, Site Head, Facility Head
- **Ops** (secondary): VP Operations, COO, Director Operations
- **Production** (secondary): Production Head, Manufacturing Head, GM Production
- **Maintenance** (secondary): Maintenance Head, Engineering Manager, Reliability Manager
- **CXO** (influencer): CEO, MD, Director, President

---

## Compliance Rules (Strict)

1. **No LinkedIn automation.** Never write code that logs into or scrapes LinkedIn/Sales Navigator. All LinkedIn data is manually entered.
2. **Public websites only.** Scripts crawl only publicly accessible URLs — no login-walled pages.
3. **Respect `robots.txt`.** Check and honor before crawling any path.
4. **No personal data in git.** Emails, phone numbers, and LinkedIn profile URLs must never be committed. Contact data lives in Google Sheets or gitignored CSVs only.
5. **Credentials gitignored.** `data/credentials.json`, `.env`, and any API keys must never be committed.
6. **Never auto-merge duplicates.** Set `duplicate_flag=True` and require human review before syncing.
7. **Never modify `data/raw/`.** These are source-of-truth inputs.

---

## Segment Pain Points (for message generation)

| Segment | Key Pain Points |
|---|---|
| Automotive | Robotic cell guarding, press safety, conveyor interlocks, LOTO |
| Pharma | ATEX zones, chemical handling, confined space entry |
| FMCG/F&B | Lockout/tagout, conveyor guards, high-speed packaging lines |
| Metals | Molten metal splash, overhead crane safety, hot work |
| Packaging | Printing press guards, slitter safety, ergonomics |
| Chemicals | ATEX, pressure vessel safety, emergency shutdown |
| Machinery OEM | CE marking, risk assessment, functional safety (SIL/PLr, ISO 13849) |

Outreach templates are in `templates/`. Research and discovery prompts are in `docs/discovery_workflow.md`.
