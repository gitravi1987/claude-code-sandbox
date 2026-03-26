# Sales Navigator Guide — South India Manufacturing Safety Prospecting

> This guide covers saved search setup, weekly search execution, and CSV export steps
> for the South India manufacturing ICP. Human-in-the-loop only — no automation.

---

## Part 1: Saved Search Setup (Do Once)

### Account Searches — Create 8 Saved Searches

Create one saved search per segment. Name them exactly as shown so they're easy to find.

**Common filters for ALL account searches:**

| Filter | Setting |
|---|---|
| Geography | Tamil Nadu, Karnataka |
| Company headcount | 501–1,000 \| 1,001–5,000 \| 5,001–10,000 \| 10,001+ |

---

#### Search 1: `TN-KA_Automotive`
| Filter | Value |
|---|---|
| Industry | Automotive |
| Keywords | stamping OR forging OR assembly OR weld OR components OR "auto parts" |

#### Search 2: `TN-KA_FMCG_FnB`
| Filter | Value |
|---|---|
| Industry | Food & Beverages; Consumer Goods |
| Keywords | manufacturing OR packaging OR processing OR plant |

#### Search 3: `TN-KA_Pharma`
| Filter | Value |
|---|---|
| Industry | Pharmaceuticals |
| Keywords | manufacturing OR API OR formulation OR plant |

#### Search 4: `TN-KA_Metals`
| Filter | Value |
|---|---|
| Industry | Mining & Metals; Steel |
| Keywords | rolling OR casting OR forging OR foundry OR steel OR aluminium |

#### Search 5: `TN-KA_Packaging`
| Filter | Value |
|---|---|
| Industry | Packaging and Containers |
| Keywords | corrugated OR flexible OR printing OR label OR container |

#### Search 6: `TN-KA_Chemicals`
| Filter | Value |
|---|---|
| Industry | Chemicals |
| Keywords | specialty OR paint OR coating OR adhesive OR polymer |

#### Search 7: `TN-KA_Machinery`
| Filter | Value |
|---|---|
| Industry | Industrial Machinery; Mechanical or Industrial Engineering |
| Keywords | machine tool OR CNC OR pump OR valve OR conveyor OR automation |

#### Search 8: `TN-KA_All_Large` (catch-all)
| Filter | Value |
|---|---|
| Industry | Manufacturing (all sub-types) |
| Headcount | 1,001–5,000 \| 5,001–10,000 \| 10,001+ only |
| Keywords | EHS OR "ISO 45001" OR "zero harm" OR "safety excellence" |

---

### Lead Searches — Create 6 Saved Searches

These are **person-level** searches for the target personas. Run these against your Account Lists.

#### Lead Search 1: `EHS_Heads_Primary`
| Filter | Value |
|---|---|
| Title | EHS Head OR HSE Manager OR Safety Manager OR Safety Officer OR EHS Director |
| Seniority | Manager \| Director \| VP \| CXO |
| Geography | Tamil Nadu, Karnataka |

#### Lead Search 2: `Plant_Factory_Heads`
| Filter | Value |
|---|---|
| Title | Plant Head OR Factory Manager OR Site Head OR Facility Head OR Plant Manager |
| Seniority | Director \| VP \| Manager |

#### Lead Search 3: `Operations_Leadership`
| Filter | Value |
|---|---|
| Title | VP Operations OR COO OR "Director Operations" OR "Operations Head" OR "Head of Operations" |
| Seniority | VP \| CXO \| Director |

#### Lead Search 4: `Production_Heads`
| Filter | Value |
|---|---|
| Title | Production Head OR "Manufacturing Head" OR "GM Production" OR "Head of Manufacturing" |
| Seniority | Manager \| Director \| VP |

#### Lead Search 5: `Maintenance_Engineering`
| Filter | Value |
|---|---|
| Title | Maintenance Head OR "Engineering Manager" OR "Reliability Manager" OR "Plant Engineer" |
| Seniority | Manager \| Director |

#### Lead Search 6: `CXO_Influencers`
| Filter | Value |
|---|---|
| Title | CEO OR MD OR President OR "Managing Director" |
| Seniority | CXO |
| Geography | Tamil Nadu, Karnataka |

---

## Part 2: Enabling Alerts

For each saved search (both account and lead), enable **alerts**:

1. Open a saved search.
2. Click the bell icon (🔔) next to the search name.
3. Set frequency: **Weekly** (not daily — avoids noise).
4. You'll receive a digest every Monday of new accounts/leads matching your filters.

---

## Part 3: Weekly Discovery Process (Monday, 90 min)

### Step 1: Review Alerts (15 min)
1. Open Sales Navigator → **Alerts** tab.
2. Review new accounts/leads added since last Monday.
3. Quick scan: Does the company look large enough? Is the role right?
4. Mark interesting ones with a **Note** in Sales Navigator (optional, helps memory).

### Step 2: Run This Week's Priority Segment Search (20 min)
Follow the rotation schedule:

| Week | Primary Search | Secondary Search |
|---|---|---|
| 1, 5, 9... | `TN-KA_Automotive` | `TN-KA_Machinery` |
| 2, 6, 10... | `TN-KA_FMCG_FnB` | `TN-KA_Packaging` |
| 3, 7, 11... | `TN-KA_Pharma` | `TN-KA_Chemicals` |
| 4, 8, 12... | `TN-KA_Metals` | `TN-KA_All_Large` |

For each search:
- Sort by: **Recently Updated** (shows newly active/changed companies)
- Filter: added in last 30 days (or "not in any list")
- Review top 20–30 results
- Add best 10–15 to your **Account List** (see Part 4)

### Step 3: Run Lead Searches for New Accounts (25 min)
For each new account added:
1. Open the company profile in Sales Navigator.
2. Click **"Find leads at this company"**.
3. Filter by: Title = EHS / Plant / Operations (use Lead Search 1–3).
4. For each relevant person: click their name → review → if strong fit, **Save to Lead List**.

### Step 4: Export to CSV (10 min)
1. Open your **Lead List** (or **Account List**).
2. Click the **Export** button (top right of the list).
3. Sales Navigator will email you the CSV within a few minutes.
4. Download it and save to: `data/raw/sales_nav_YYYY-MM-DD.csv`

> **Export limit**: ~2,500 records/month on standard plan. Use conservatively — export only lists you've curated, not raw search results.

### Step 5: Run Normalize Script (10 min)
```bash
python scripts/normalize_csv.py \
  --input data/raw/sales_nav_2026-03-30.csv \
  --source SalesNav
```

Review output: check `duplicate_flag` column for any near-duplicates before syncing.

---

## Part 4: Account & Lead List Structure

Maintain these permanent lists in Sales Navigator:

| List Name | Purpose | Max Size |
|---|---|---|
| `Priority_TN_Automotive` | Top automotive accounts in TN | 100 |
| `Priority_TN_FMCG_Pharma` | Top FMCG + Pharma in TN | 100 |
| `Priority_KA_All` | Top accounts in Karnataka | 100 |
| `Contacted_2026` | All accounts where outreach has begun | 200 |
| `EHS_Leads_Active` | EHS/Safety contacts to reach this month | 200 |
| `Plant_Leads_Active` | Plant/Factory heads to reach this month | 200 |
| `Follow_Up_Queue` | Warm leads waiting for follow-up | 100 |

**Workflow**: New discovery → Priority List → after outreach → Contacted_2026.

---

## Part 5: Sales Navigator CSV Column Mapping

When you export from Sales Navigator, the column names differ from our schema.
`normalize_csv.py` handles most of this automatically, but here's the mapping for reference:

| Sales Navigator Column | Our Schema Column | Notes |
|---|---|---|
| Company Name | company_name | Auto-mapped |
| LinkedIn Company Page URL | linkedin_company_url | Auto-mapped |
| Company Headcount | employee_band | Auto-converted to band (500-1000, etc.) |
| Industry | segment | Auto-mapped; manual review recommended |
| Headquarters | hq_state + plant_locations | State inferred from city name |
| Website | website | Auto-mapped |
| First Name + Last Name | full_name | Concatenated in contacts sheet |
| Title | title | Auto-mapped |
| LinkedIn URL | linkedin_url | In contacts sheet |

---

## Part 6: Quality Checklist Before Syncing

Before running `sync_gsheets.py`, verify the cleaned CSV:

- [ ] No blank `company_name` rows
- [ ] `hq_state` is TN or KA for all rows (blank = unknown region, may be outside ICP)
- [ ] `employee_band` is in correct format (500-1000 / 1000-5000 / 5000+)
- [ ] `segment` is populated (Other = needs manual review)
- [ ] `duplicate_flag` column reviewed — no unresolved duplicates
- [ ] No personal email addresses or phone numbers in the file (contacts CSV only)
- [ ] `website` column has valid URLs (not just domain names without http)

---

## Part 7: Limitations and Workarounds

| Limitation | Workaround |
|---|---|
| Sales Nav shows profiles, not financials | Use Tofler / Zauba Corp to verify turnover band |
| Indian company names in Tamil/Kannada | Search by registered English name; check MCA21 portal |
| Small companies (MSME) appear in search | Strict headcount filter ≥501; cross-check if in doubt |
| EHS titles may use local variations | Use OR operators: "Safety Manager" OR "HSE In-charge" OR "Safety Engineer" |
| Phone/email not in Sales Nav | Get boardline from company website "Contact Us" page |
