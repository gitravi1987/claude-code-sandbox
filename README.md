# South India Manufacturing Safety Prospecting System

A weekly AI-assisted prospecting system for selling machine safety solutions to large manufacturing companies in Tamil Nadu and South Karnataka.

**Served companies**: Fortress Safety | VAYON Systems

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up credentials
# Create .env in project root with: GOOGLE_SHEETS_ID=your_spreadsheet_id
# Place Google service account JSON at: data/credentials.json

# 3. Create data directories
mkdir -p data/raw data/processed

# 4. Run a test (dry run)
python scripts/sync_gsheets.py --sheet accounts --input data/processed/sample.csv --dry-run
```

---

## Weekly Workflow

| Day | Task | Key Command |
|---|---|---|
| Monday | Discover + normalize accounts | `python scripts/normalize_csv.py --input data/raw/accounts_YYYY-MM-DD.csv` |
| Tuesday | Crawl websites + compute safety scores | `python scripts/crawl_enrichment.py ...` → `python scripts/safety_score.py ...` → `python scripts/sync_gsheets.py ...` |
| Wednesday | LinkedIn outreach (manual) | Use `templates/linkedin_connection.md` |
| Thursday | Email + phone (manual) | Use `templates/email_sequence.md` |
| Friday | WhatsApp + weekly report | `python scripts/weekly_report.py` + `templates/whatsapp.md` |

---

## Documentation

- **[CLAUDE.md](CLAUDE.md)** — Claude Code operating guide (schemas, scripts, compliance rules)
- **[PRD.md](PRD.md)** — Full product requirements document
- **[docs/safety_score_rubric.md](docs/safety_score_rubric.md)** — Safety Maturity Score methodology