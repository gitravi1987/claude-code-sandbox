# PRD: South India Manufacturing Safety Prospecting System

**Version**: 1.0
**Date**: March 2026
**Owner**: Regional Sales Manager (Fortress Safety) | Co-Founder (VAYON Systems)
**Status**: Active — Week 1

---

## 1. Problem Statement

Large manufacturing plants in Tamil Nadu and South Karnataka have significant unmet needs around machine safety — but they are hard to reach systematically. The current prospecting process is:

- **Unstructured**: No repeatable system to find, qualify, and approach the right companies.
- **Persona-blind**: Outreach reaches the wrong person (procurement vs. EHS head) or arrives with generic messaging.
- **Commodity-positioned**: Safety products are pitched as one-off purchases rather than as solutions to systemic man-machine interface risks.
- **No institutional memory**: Each sales call starts from scratch; no database of signals, history, or intent.

The result: low conversion, long sales cycles, and missed opportunities in a market increasingly regulation-driven (Factories Act amendments, ISO 45001 mandates from MNC HQs, post-accident liability exposure).

---

## 2. Goals

### Primary Goals

1. Build a **proprietary "South India Manufacturing Safety" database** of 500+ large manufacturing accounts with enriched safety-culture signals, decision-maker contacts, and outreach history — within 12 weeks.
2. Establish a **repeatable weekly prospecting rhythm** (Mon–Fri) that generates 20+ qualified conversations per month.
3. Enable **concept-based selling**: arrive at every call with an account-specific hypothesis about safety gaps, not a product catalog.

### Success Metrics

| Metric | Week 4 Target | Week 12 Target |
|---|---|---|
| Accounts in DB | 100 | 500 |
| Contacts identified | 200 | 1,000 |
| LinkedIn connections sent/week | 30 | 50 |
| LinkedIn response rate | — | >15% |
| Email open rate | — | >30% |
| Qualified conversations/month | — | 20+ |
| Accounts with safety score | 50% | 90% |
| Meetings booked/month | — | 8+ |

---

## 3. ICP Definition

### Company Profile

| Attribute | Requirement |
|---|---|
| Geography | Tamil Nadu: Chennai, Coimbatore, Hosur, Madurai, Trichy, Salem, Ambattur, Oragadam |
| | South Karnataka: Bengaluru, Mysuru, Hubli, Mangaluru, Davangere, Tumkur |
| Type | MNC or large Indian corporate — non-MSME |
| Turnover | >500 Cr (LinkedIn proxy: 500+ employees) |
| Industries | Automotive & components, machinery, packaging, FMCG/F&B, pharma, metals, chemicals, construction materials, textiles (large plants only) |
| Safety signal | ISO 45001 / OHSAS certified OR visible EHS program (Zero Harm, safety awards, dedicated EHS page) |

### Disqualify If

- MSME (turnover <250 Cr)
- Pure service companies (no plant operations)
- Already active/existing Fortress Safety or VAYON accounts
- Pharma/chemical companies without machinery-intensive operations

### Target Personas

| Tag | Titles | Fortress Relevance | VAYON Relevance |
|---|---|---|---|
| EHS | EHS Head, HSE Manager, Safety Manager, Safety Officer, EHS Director | High | High |
| Plant | Plant Head, Factory Manager, Site Head, Facility Head | High | High |
| Ops | VP Operations, COO, Director Operations, Operations Head | Medium | High |
| Production | Production Head, Manufacturing Head, GM Production | Medium | Medium |
| Maintenance | Maintenance Head, Engineering Manager, Reliability Manager | High | Medium |
| CXO | CEO, MD, Director, President | Influencer | Influencer |

---

## 4. Functional Requirements

### Module 1: Account Discovery

**Goal**: Systematically identify all large manufacturing accounts in TN + South KA matching the ICP.

**Sources**:

| Source | Method | Notes |
|---|---|---|
| LinkedIn Sales Navigator | Native saved searches + account lists | Manual export only; max 2,500 contacts/month on standard plan |
| Perplexity AI | "List top 50 [segment] manufacturers in [city] with >1000 employees" | Names + basic context; verify independently |
| India industry databases | CMIE Prowess, Tofler, Zauba Corp, MCA21 portal | Turnover verification, registered office |
| Industry associations | CII, ACMA, FICCI, NASSCOM Manufacturing member lists | Public directories |
| Press / news | "New plant inaugurated in Hosur 2025", "[Company] safety award" | Google News, Perplexity |

**Discovery Process** (Monday):

1. In Sales Navigator, run 2–3 saved searches (rotate segments weekly — see rotation below).
2. Filter for accounts added/updated in the last 7 days.
3. For each high-fit account: note company name, website, LinkedIn Company URL, headcount bracket.
4. Save 10–20 new accounts to `data/raw/accounts_YYYY-MM-DD.csv`.
5. Run `normalize_csv.py` to clean and flag duplicates.

**Segment Rotation (Weekly)**:

| Week | Primary Segment | Secondary Segment |
|---|---|---|
| 1 | Automotive (Chennai/Hosur cluster) | Machinery OEMs |
| 2 | FMCG/F&B (Coimbatore, Trichy) | Packaging |
| 3 | Pharma (Ambattur, Oragadam) | Chemicals |
| 4 | Metals (Bengaluru, Hosur) | Automotive (KA) |
| Repeat | — | — |

**Sales Navigator Search Configuration**:

```
Geography:  Tamil Nadu OR Karnataka
Industry:   [Segment-specific]
Headcount:  501-1000 OR 1001-5000 OR 5001-10000 OR 10001+
Keywords:   [optional] "EHS" OR "HSE" OR "safety" OR "ISO 45001"
Seniority:  Director, VP, CXO, Manager (for lead searches)
Roles:      [see Target Personas above]
```

---

### Module 2: Data Ingestion & Normalization

**Goal**: Transform heterogeneous raw data from multiple sources into a clean, deduplicated, standardized format.

**Script**: `scripts/normalize_csv.py`

**Inputs**: Any CSV with company data (Sales Navigator export, Perplexity list, manual entry).

**Processing Steps**:

1. Standardize column names to snake_case (e.g., "Company Name" → `company_name`).
2. Trim whitespace; normalize capitalization (title case for names, upper for states).
3. Infer `hq_state` (TN / KA) from city/address keywords.
4. Infer `segment` from company name and description keywords (auto-tag, then human-verify).
5. Fuzzy-match `company_name` at 85% threshold — flag near-duplicates with a `duplicate_flag` column. Do NOT auto-merge.
6. Assign UUID `account_id` to new records (blank `account_id` = new record).
7. Set `created_at = today`, `status = New`, `source` from `--source` flag.

**Output**: `data/processed/<input_stem>_clean.csv`

**CLI**:
```bash
python scripts/normalize_csv.py \
  --input data/raw/accounts_2026-03-24.csv \
  --source SalesNav
```

---

### Module 3: External Enrichment & Safety Scoring

**Goal**: Crawl public company websites to detect EHS maturity signals and compute a 0–100 Safety Maturity Score per account.

**Scripts**: `scripts/crawl_enrichment.py`, `scripts/safety_score.py`

#### Crawl Logic (`crawl_enrichment.py`)

For each account with a `website`:

1. Fetch homepage and attempt these paths:
   - `/about`, `/about-us`
   - `/sustainability`, `/esg`
   - `/health-safety`, `/ehs`, `/hse`, `/safety`, `/health`
   - `/csr`, `/environment`, `/responsibility`
2. Before crawling: check `<domain>/robots.txt`; skip disallowed paths.
3. Rate-limit: 1 request/second per domain (configurable with `--delay`); timeout 10s per request.
4. Parse HTML with BeautifulSoup; extract visible text.
5. Search for EHS keywords (see rubric); record which were found.
6. Save: `ehs_page_url` (best URL found), `ehs_text_snippet` (first 500 chars), `keywords_found` (comma-separated).

**Output columns added**: `ehs_page_url`, `ehs_text_snippet`, `keywords_found`, `crawl_date`, `crawl_status`

#### Safety Maturity Score (`safety_score.py`)

Keyword-based, 0–100 scale. See `docs/safety_score_rubric.md` for full keyword list.

| Category | Max Points | Top Signals |
|---|---|---|
| Certifications | 30 | ISO 45001 (+20), OHSAS 18001 (+15), ISO 14001 (+10) |
| Programs | 20 | Zero Harm (+10), Zero Accident (+8), Behaviour-Based Safety (+5) |
| Awards | 20 | Safety Excellence Award (+10), British Safety Council (+10), NSC Award (+8), Greentech (+8) |
| Policy depth | 15 | Dedicated EHS page (+5), Safety Policy PDF (+5), Annual Safety Report (+5) |
| Regulatory | 10 | Factories Act compliance (+5), PSSR/Machinery Directive (+5), CE marking (+5) |
| Transparency | 5 | LTIFR/TRIR/safety metrics published (+5) |

**Score interpretation**:
- 0–20: Low maturity — likely reactive, compliance-minimum → highest urgency messaging
- 21–50: Developing — some programs, ISO in progress → position as accelerator
- 51–75: Established — ISO certified, some awards → compete on expertise, integration
- 76–100: Advanced — multiple awards, BBS, published metrics → target VAYON for audits + training

**Output columns added**: `safety_score`, `iso_45001`, `safety_awards`, `score_band`

---

### Module 4: Lead Database

**Goal**: A single, shared, always-current master database for both Fortress Safety and VAYON Systems.

**Storage**: Google Sheets (shared document) accessed via `gspread` Python library.

**Spreadsheet name**: `South India Manufacturing Safety DB`
**Required sheets**: `accounts`, `contacts`, `weekly_log`

**Access**: Both Fortress and VAYON team members share one spreadsheet. Accounts tagged with `relevant_to = Fortress / VAYON / Both`. Filter by `relevant_to` when viewing company-specific pipelines.

**Sync script** (`sync_gsheets.py`):
- Upsert: match on `account_id` / `contact_id`; append new rows; update changed columns in existing rows.
- Never hard-deletes rows. Use `status = Archived` to retire stale records.
- Idempotent: safe to run multiple times.

**`weekly_log` sheet** (append-only):

| Column | Notes |
|---|---|
| week_date | Monday date (YYYY-MM-DD) |
| accounts_added | count |
| contacts_added | count |
| connections_sent | count |
| inmails_sent | count |
| emails_sent | count |
| whatsapp_sent | count |
| replies_received | count |
| meetings_booked | count |
| notes | free text |

---

### Module 5: Weekly Outreach Workflow

**Goal**: Execute personalized, value-first multi-channel outreach positioning Fortress/VAYON as machine safety thought leaders — not commodity vendors.

**Guiding Principle**: Concept-based selling. Lead with a hypothesis about the account's safety gap. Reference something specific to their plant, segment, or recent activity.

#### Wednesday — LinkedIn Outreach

**Connection Request** (≤300 characters):
```
Hi [Name], I work with [segment] plants in TN & Karnataka on machine safety —
reducing man-machine interface risks. Your work at [Company] caught my attention.
Would love to connect. — [Your name], Fortress Safety / VAYON Systems
```

**InMail** (2nd/3rd degree leads):
- Subject: `Quick question on [Company]'s machine safety approach`
- Body: 3 paragraphs — (1) specific signal observed (ISO cert / award / plant expansion), (2) relevant pain point for their segment, (3) soft ask for 15-min call

**Engagement tip**: Comment thoughtfully on 3–5 target contacts' posts each week. Do not just like — add a safety insight relevant to their post.

#### Thursday — Email Sequence (3-Touch)

See `templates/email_sequence.md` for full copy. Summary:

| Touch | Timing | Angle |
|---|---|---|
| 1 | Day 1 | Industry insight + soft ask (no hard sell) |
| 2 | Day 5 | Mini case study (similar plant, measurable outcome) |
| 3 | Day 10 | Final check-in + graceful exit / future re-engagement |

**Phone (Thursday)**:
- Call boardline; ask for EHS Head or Plant Head by name if known, by title if not.
- Voicemail script: 20 seconds — who you are, why you're calling (specific safety context), single CTA.

#### Friday — WhatsApp (Warm Contacts Only)

Send only to contacts who are Connected on LinkedIn OR have had prior interaction.

Message types (rotate weekly):
1. Safety insight: 3-sentence tip relevant to their industry
2. Mini case study: 2–3 sentences, outcome-focused, no jargon
3. Seminar / webinar invite: upcoming workshop on a safety topic

See `templates/whatsapp.md` for copy variants.

---

### Module 6: Reporting & Prioritization

**Goal**: Every Friday, generate a 1-page summary of the week's activity and next week's priority list.

**Script**: `scripts/weekly_report.py`

**Prioritization Formula**:
```
priority_score = (safety_score / 100) * 0.4
              + size_weight * 0.3        # 500-1000=0.33, 1000-5000=0.66, 5000+=1.0
              + recency_weight * 0.2     # days since last contact, inverted, capped at 30 days
              + status_weight * 0.1      # New=0.6, Contacted=0.4, Engaged=0.8, Qualified=1.0
```

**Weekly Report Sections**:
1. **This Week's Activity** — accounts added, contacts identified, outreach sent, replies, meetings
2. **Top 10 Priority Accounts** — ranked by priority_score, with status and next action
3. **Follow-Up Due** — contacts where last_interaction > 7 days AND status ∈ {Contacted, Engaged}
4. **Leads to Enrich** — accounts with no safety_score (crawl not yet run)
5. **Week-over-Week Trend** — compare this week's totals vs. prior 4 weeks

Output: Markdown file saved to `docs/weekly_report_YYYY-MM-DD.md` + row appended to `weekly_log` sheet.

---

## 5. Non-Functional Requirements

### LinkedIn Terms of Service

- No automated login to LinkedIn or Sales Navigator — ever.
- No scraping of linkedin.com (profiles, search results, company pages).
- No use of third-party LinkedIn scraping tools (Phantombuster, Dux-Soup, etc.).
- Sales Navigator CSV export: maximum 2,500 records/month on standard plan. Use judiciously.
- All LinkedIn-sourced data is manually reviewed before entry into the database.

### Data Privacy (India DPDP Act 2023)

- Contact data (name, email, phone, LinkedIn URL) sourced only from official company websites, press releases, or direct business interactions.
- No personal data committed to this Git repository.
- Google Sheets access restricted to business Google accounts of the team.
- Data is used solely for B2B prospecting; not shared with third parties.

### System Robustness

- All scripts handle missing `website` gracefully: skip crawl, set `safety_score = null`.
- All scripts handle HTTP errors (404, 403, timeout, SSL) without crashing; log error and continue.
- `sync_gsheets.py` is idempotent — safe to run multiple times.
- `normalize_csv.py` never modifies files in `data/raw/`.

### Performance Targets

| Operation | Target |
|---|---|
| Crawl 100 accounts | < 10 minutes |
| Normalize 500 rows | < 30 seconds |
| Sync 100 rows to Sheets | < 2 minutes |
| Generate weekly report | < 60 seconds |

---

## 6. Technical Stack

| Layer | Technology | Rationale |
|---|---|---|
| Language | Python 3.11+ | Ubiquitous, best library support |
| Data manipulation | pandas | CSV normalization, dedup, joins |
| Web crawling | requests + BeautifulSoup4 | Lightweight, no JavaScript needed for EHS pages |
| Fuzzy matching | difflib (stdlib) | No extra dependency; sufficient for company name dedup |
| Google Sheets | gspread + google-auth | Official API; free tier sufficient |
| Config/secrets | python-dotenv | Standard; keeps credentials out of code |
| AI assistance | Claude (strategy, copy), Perplexity (research) | External tools, not in codebase |

---

## 7. Repository Directory Structure

```
/
├── CLAUDE.md                    ← Claude Code operating guide
├── PRD.md                       ← this document
├── README.md                    ← quick start guide
├── .gitignore
├── requirements.txt
│
├── scripts/
│   ├── normalize_csv.py
│   ├── crawl_enrichment.py
│   ├── safety_score.py
│   ├── sync_gsheets.py
│   └── weekly_report.py
│
├── data/
│   ├── raw/                     ← GITIGNORED
│   └── processed/               ← GITIGNORED
│
├── templates/
│   ├── linkedin_connection.md
│   ├── inmail.md
│   ├── email_sequence.md
│   └── whatsapp.md
│
└── docs/
    ├── safety_score_rubric.md
    └── weekly_report_YYYY-MM-DD.md   ← generated
```

---

## 8. Weekly Operating Rhythm (Detailed)

### Monday — Account Discovery (90 min)

1. Open Sales Navigator → run 2–3 saved searches for this week's segments.
2. Filter for new/updated accounts in last 7 days.
3. For each high-fit account (ICP match): copy to `data/raw/accounts_YYYY-MM-DD.csv`.
4. Run `python scripts/normalize_csv.py --input data/raw/accounts_YYYY-MM-DD.csv --source SalesNav`.
5. Review `duplicate_flag` column; resolve manually if needed.
6. Use Perplexity: "Summarize [Company]'s safety culture, plant locations, and recent EHS news" for top 5 accounts — paste notes into `notes` column.

### Tuesday — Research & Enrichment (60 min)

1. Run `python scripts/crawl_enrichment.py --input data/processed/accounts_clean.csv`.
2. Run `python scripts/safety_score.py --input data/processed/accounts_enriched.csv`.
3. Review scores: manually correct any obvious misses (e.g., ISO 45001 in annual report PDF not detected).
4. Set `priority` for each new account (High/Medium/Low) based on score band + ICP fit.
5. Add 2–3 key contacts per High-priority account (LinkedIn research → manual entry into contacts sheet).
6. Run `python scripts/sync_gsheets.py --sheet accounts --input data/processed/accounts_scored.csv`.
7. Run `python scripts/sync_gsheets.py --sheet contacts --input data/processed/contacts_new.csv`.

### Wednesday — LinkedIn Outreach (45 min)

1. Open Google Sheets → filter `accounts`: priority=High, status=New.
2. For each: open LinkedIn profile → send personalized connection request (use template, 1–2 custom lines).
3. Update contact: `connection_status = Request Sent`, `last_interaction = today`.
4. Review pending requests >7 days old — send InMail to those who haven't accepted.
5. Engage with 3–5 posts from target contacts (add a safety insight comment — not just a like).
6. Update Google Sheets after session.

### Thursday — Email & Phone (60 min)

1. Filter contacts: email ≠ blank, `email_sent = FALSE`, priority = High or Medium.
2. Send Touch 1 email — personalized with their industry/segment context (1–2 custom sentences).
3. Log: set `email_sent = TRUE`, `last_interaction = today`, update `notes` with subject line used.
4. Telecalling: 5–10 calls to boardline numbers; script in `templates/email_sequence.md`.
5. Log all call outcomes in `notes` column.

### Friday — WhatsApp & Weekly Report (30 min)

1. Filter contacts: `connection_status = Connected` OR prior positive interaction.
2. Send WhatsApp message (rotate: insight / mini case study / seminar invite).
3. Log: set `whatsapp_sent = TRUE`, `last_interaction = today`.
4. Run `python scripts/weekly_report.py --output docs/weekly_report_$(date +%Y-%m-%d).md`.
5. Review report: adjust priorities for next week.
6. Plan Monday's discovery segment (follow rotation schedule).

---

## 9. Future Enhancements

| Enhancement | Priority | Description |
|---|---|---|
| AI account snapshots | High | Use Claude API to generate 1-page account briefings from crawled EHS text |
| MCA/Prowess financial integration | High | Confirm turnover band from MCA annual filings |
| Safety incident news alerts | Medium | Daily Google Alerts / Perplexity search for "[company] accident OR safety" |
| Notion mirror | Medium | Sync Google Sheets → Notion for CRM-style kanban view |
| Streamlit dashboard | Low | Visual pipeline, safety score distribution, week-over-week trends |
| WhatsApp Business API | Low | Structured templates via Meta Business Platform |
| Email automation (SMTP) | Low | Touch 2/3 auto-send after set delay (ensure DPDP Act compliance) |
| Multi-user CRM graduation | Medium | Move to HubSpot or Zoho once pipeline exceeds 50 active accounts |

---

## 10. Open Questions

1. **Google Sheets access**: Should both Fortress and VAYON team members have edit access to the same sheet, or view-only for one party filtered by `relevant_to`?
2. **CRM graduation point**: At what pipeline stage (number of active accounts / meetings per month) should this move to a dedicated CRM (HubSpot, Zoho)?
3. **Industry DB subscriptions**: Does the team have access to CMIE Prowess, Tofler Pro, or Dun & Bradstreet for turnover verification?
4. **Sales Navigator plan tier**: Core / Advanced / Advanced Plus — affects monthly export limits and CRM sync options.
5. **DPDP Act compliance**: Should a data processing notice be drafted before storing contact details of Indian residents?
6. **WhatsApp Business**: Is the outreach happening via personal WhatsApp or WhatsApp Business? (Affects template restrictions and API eligibility.)
