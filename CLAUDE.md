# CLAUDE.md — South India Manufacturing Safety Prospecting System

> Claude Code reads this file at the start of every session.
> Follow every instruction here unless the user explicitly overrides it.

---

## Project Purpose

This repository powers a **weekly AI-assisted prospecting workflow** for selling machine safety solutions (audits, engineering controls, integration, training) to large manufacturing companies in **Tamil Nadu and South Karnataka**.

Two companies are served from one shared system:

- **Fortress Safety** — Machine safety products and services (Regional Sales Manager)
- **VAYON Systems** — Safety engineering, audits, and integration (Co-Founder)

The master database lives in **Google Sheets** (accessed via `gspread`). Python scripts handle data cleaning, website enrichment, safety scoring, and weekly reporting. LinkedIn Sales Navigator is used manually — never automated.

---

## Ideal Customer Profile (ICP)

| Attribute | Requirement |
|---|---|
| Geography | Tamil Nadu (Chennai, Coimbatore, Hosur, Madurai, Trichy, Salem) or South Karnataka (Bengaluru, Mysuru, Hubli, Mangaluru, Davangere) |
| Type | MNC or large Indian corporate — non-MSME |
| Turnover proxy | >500 Cr (LinkedIn proxy: 500+ employees) |
| Industries | Automotive, machinery, packaging, FMCG/F&B, pharma, metals, chemicals, construction materials, textiles (large plants) |
| Safety signal | ISO 45001 / OHSAS certified OR visible EHS program (Zero Harm, safety awards, dedicated EHS page) |

**Disqualify**: MSME (<250 Cr), pure service companies, already active Fortress/VAYON accounts.

### Target Personas

| Tag | Titles | Priority |
|---|---|---|
| EHS | EHS Head, HSE Manager, Safety Manager, Safety Officer, EHS Director | Primary |
| Plant | Plant Head, Factory Manager, Site Head, Facility Head | Primary |
| Ops | VP Operations, COO, Director Operations, Operations Head | Secondary |
| Production | Production Head, Manufacturing Head, GM Production | Secondary |
| Maintenance | Maintenance Head, Engineering Manager, Reliability Manager | Secondary |
| CXO | CEO, MD, Director, President | Influencer |

---

## Directory Structure

```
/
├── CLAUDE.md                    ← this file (read every session)
├── PRD.md                       ← product requirements document
├── README.md
├── .gitignore
├── requirements.txt
│
├── scripts/
│   ├── normalize_csv.py         ← clean + dedup raw CSV exports
│   ├── crawl_enrichment.py      ← crawl public company websites for EHS signals
│   ├── safety_score.py          ← compute Safety Maturity Score (keyword, 0–100)
│   ├── sync_gsheets.py          ← push cleaned data to Google Sheets master DB
│   └── weekly_report.py         ← generate weekly priority summary
│
├── data/
│   ├── raw/                     ← GITIGNORED: raw exports (Sales Nav, industry DBs)
│   ├── processed/               ← GITIGNORED: cleaned CSVs
│   └── credentials.json         ← GITIGNORED: Google service account key
│
├── templates/
│   ├── linkedin_connection.md
│   ├── inmail.md
│   ├── email_sequence.md
│   └── whatsapp.md
│
└── docs/
    ├── safety_score_rubric.md
    └── weekly_report_YYYY-MM-DD.md   ← generated each Friday
```

---

## Google Sheets Master Database

**Spreadsheet name**: `South India Manufacturing Safety DB`
**Credentials file**: `data/credentials.json` (gitignored — never commit)
**Env var**: `GOOGLE_SHEETS_ID=<spreadsheet_id>` in `.env` (gitignored)

### Sheet: `accounts`

| Column | Type | Notes |
|---|---|---|
| account_id | TEXT | UUID, auto-generated |
| company_name | TEXT | |
| segment | TEXT | Automotive / Pharma / FMCG / Metals / Packaging / Chemicals / Machinery / Other |
| hq_state | TEXT | TN / KA |
| plant_locations | TEXT | comma-separated city names |
| employee_band | TEXT | 500-1000 / 1000-5000 / 5000+ |
| turnover_band | TEXT | 500-1000Cr / 1000-5000Cr / 5000Cr+ |
| website | TEXT | |
| safety_score | INTEGER | 0–100, keyword-based |
| iso_45001 | TEXT | TRUE / FALSE / Unknown |
| safety_awards | TEXT | comma-separated |
| ehs_page_url | TEXT | URL of EHS/safety page if found |
| ehs_text_snippet | TEXT | first 500 chars of EHS content |
| linkedin_company_url | TEXT | manual entry only |
| source | TEXT | SalesNav / Perplexity / IndustryDB / Manual |
| relevant_to | TEXT | Fortress / VAYON / Both |
| priority | TEXT | High / Medium / Low |
| status | TEXT | New / Contacted / Engaged / Qualified / Proposal / Closed-Won / Closed-Lost |
| last_contact_date | TEXT | YYYY-MM-DD |
| next_action | TEXT | free text |
| notes | TEXT | free text |
| created_at | TEXT | YYYY-MM-DD |
| updated_at | TEXT | YYYY-MM-DD |

### Sheet: `contacts`

| Column | Type | Notes |
|---|---|---|
| contact_id | TEXT | UUID, auto-generated |
| account_id | TEXT | FK to accounts sheet |
| company_name | TEXT | denormalized for readability |
| full_name | TEXT | |
| title | TEXT | |
| persona_tag | TEXT | EHS / Plant / Ops / Production / Maintenance / CXO |
| linkedin_url | TEXT | manual capture from Sales Navigator only |
| email | TEXT | from company website / boardline |
| phone | TEXT | |
| connection_status | TEXT | Not Connected / Request Sent / Connected |
| inmail_sent | TEXT | TRUE / FALSE |
| email_sent | TEXT | TRUE / FALSE |
| whatsapp_sent | TEXT | TRUE / FALSE |
| last_interaction | TEXT | YYYY-MM-DD |
| notes | TEXT | free text |

### Sheet: `weekly_log`

| Column | Notes |
|---|---|
| week_date | Monday date of the week (YYYY-MM-DD) |
| accounts_added | integer count |
| contacts_added | integer count |
| connections_sent | integer count |
| inmails_sent | integer count |
| emails_sent | integer count |
| whatsapp_sent | integer count |
| replies_received | integer count |
| meetings_booked | integer count |
| notes | free text |

---

## Python Scripts Reference

### `scripts/normalize_csv.py`
Cleans raw CSV exports from any source into standard format.

```bash
python scripts/normalize_csv.py --input data/raw/sales_nav_export.csv
python scripts/normalize_csv.py --input data/raw/sales_nav_export.csv --output data/processed/custom_name.csv
```

**What it does**:
1. Standardize column names to snake_case
2. Trim whitespace, normalize capitalization
3. Infer `hq_state` (TN/KA) and `segment` from location/company keywords
4. Fuzzy-match on `company_name` (85% threshold) — flag near-duplicates, do NOT auto-merge
5. Assign UUID `account_id` to new records
6. Timestamp `created_at`

### `scripts/crawl_enrichment.py`
Crawls public company websites for EHS/safety signals.

```bash
python scripts/crawl_enrichment.py --input data/processed/accounts_clean.csv
python scripts/crawl_enrichment.py --input data/processed/accounts_clean.csv --delay 2
```

**What it does**:
1. For each row with a `website`, fetch homepage + common EHS paths
2. Check `robots.txt` first; skip disallowed paths
3. Rate-limit: 1 req/sec default (configurable with `--delay`)
4. Extract EHS-related text via BeautifulSoup
5. Output: adds `ehs_page_url`, `ehs_text_snippet`, `keywords_found` columns

### `scripts/safety_score.py`
Computes a 0–100 Safety Maturity Score per account from enrichment data.

```bash
python scripts/safety_score.py --input data/processed/accounts_enriched.csv
```

**Scoring categories** (see `docs/safety_score_rubric.md` for full detail):
- Certifications: up to 30 pts (ISO 45001, OHSAS, ISO 14001)
- Programs: up to 20 pts (Zero Harm, BBS, Safety Culture)
- Awards: up to 20 pts (Safety Excellence, British Safety Council, NSC)
- Policy depth: up to 15 pts (EHS page, Safety Policy PDF, Annual Report)
- Regulatory signals: up to 10 pts (Factories Act, PSSR/Machinery Directive)
- Incident transparency: up to 5 pts (LTIFR/TRIR published)

### `scripts/sync_gsheets.py`
Pushes cleaned/scored CSV data to Google Sheets master DB.

```bash
python scripts/sync_gsheets.py --sheet accounts --input data/processed/accounts_scored.csv
python scripts/sync_gsheets.py --sheet contacts --input data/processed/contacts_clean.csv
```

**Requirements**: `data/credentials.json` + `GOOGLE_SHEETS_ID` in `.env`
**Upsert logic**: match on `account_id`/`contact_id` — update existing, append new. Never deletes rows.

### `scripts/weekly_report.py`
Generates a weekly priority report from the Google Sheets DB.

```bash
python scripts/weekly_report.py
python scripts/weekly_report.py --output docs/weekly_report_2026-03-24.md
```

**Output sections**:
1. This Week's Summary (counts of activity)
2. Top 10 Priority Accounts (ranked by composite score)
3. Follow-Up Due (contacts where last_interaction > 7 days, status = Contacted/Engaged)
4. New Leads to Enrich (accounts with safety_score = null)
5. Auto-append row to `weekly_log` sheet

---

## Weekly Operating Rhythm

| Day | Task | Time | Tools |
|---|---|---|---|
| **Monday** | Discovery — run Sales Nav searches, capture new accounts | 90 min | Sales Navigator, Perplexity, `normalize_csv.py` |
| **Tuesday** | Enrichment — crawl websites, compute scores, sync to Sheets | 60 min | `crawl_enrichment.py`, `safety_score.py`, `sync_gsheets.py` |
| **Wednesday** | LinkedIn outreach — connection requests + InMails | 45 min | Sales Navigator, `templates/linkedin_connection.md`, `templates/inmail.md` |
| **Thursday** | Email & phone — 3-touch sequence + telecalling | 60 min | `templates/email_sequence.md` |
| **Friday** | WhatsApp + weekly report — nurture warm contacts, generate report | 30 min | `templates/whatsapp.md`, `weekly_report.py` |

---

## Environment Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Create `.env` in project root:
   ```
   GOOGLE_SHEETS_ID=your_spreadsheet_id_here
   ```
3. Place Google service account JSON at: `data/credentials.json`
4. Create folder structure: `mkdir -p data/raw data/processed`
5. Run a test sync: `python scripts/sync_gsheets.py --sheet accounts --dry-run`

---

## Compliance Rules — STRICT

1. **No LinkedIn automation.** Never write code that logs into LinkedIn, Sales Navigator, or linkedin.com. All LinkedIn data is manually entered.
2. **Public websites only.** Scripts crawl only publicly accessible URLs (no login-walled pages).
3. **Respect robots.txt.** Check and honor `robots.txt` before crawling any path.
4. **No personal data in git.** Emails, phone numbers, and LinkedIn URLs must never be committed. All contact data lives in Google Sheets or gitignored CSVs.
5. **Credentials gitignored.** `data/credentials.json`, `.env`, and any API keys must never be committed.

---

## What Claude Code Should Do Autonomously

- Run, debug, and improve the Python scripts in `scripts/`
- Clean and normalize CSV data from any format
- Write new scripts following the patterns and schemas in this document
- Generate outreach message variations from the templates
- Update schemas if new fields are required (update this file too)
- Generate the weekly report and summary

## What Claude Code Must NOT Do

- Scrape or automate any interaction with LinkedIn or Sales Navigator
- Commit `credentials.json`, `.env`, or any API key
- Modify files in `data/raw/` (source-of-truth inputs)
- Send emails, WhatsApp messages, or make calls autonomously
- Auto-merge duplicate records (flag for human review instead)

---

## Segment Quick Reference

| Segment | Example Companies (types) | Key Pain Points |
|---|---|---|
| Automotive | Tier-1 stamping, assembly, weld shops | Robotic cell guarding, press safety, conveyor interlocks |
| Pharma | API manufacturing, formulations | ATEX zones, chemical handling, confined space |
| FMCG/F&B | Packaging lines, process plants | Lockout/tagout, conveyor guards, high-speed machinery |
| Metals | Steel rolling, casting, forging | Molten metal splash, overhead crane safety, hot work |
| Packaging | Corrugated, flexible, rigid | Printing press guards, slitter safety, ergonomics |
| Chemicals | Specialty chemicals, paints, adhesives | ATEX, pressure vessel safety, emergency shutdown |
| Machinery | Machine tools, industrial equipment OEMs | CE marking, risk assessment, functional safety (SIL/PLr) |
