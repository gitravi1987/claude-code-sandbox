# Discovery Workflow — Perplexity & AI-Assisted Research

> Use these prompts every Monday during the Discovery session.
> Copy → paste → customize → extract → save to raw CSV.

---

## Overview

The discovery workflow has three phases:

1. **Company list generation** — find new ICP-matching accounts by segment
2. **Account snapshot** — research each shortlisted company in depth
3. **Contact identification** — find the right person to reach at each account

---

## Phase 1: Company List Generation Prompts

Use these in Perplexity AI or Claude. One prompt per segment per week (follow the rotation in `docs/sales_nav_guide.md`).

### Prompt Template (general)
```
List the top 20-30 [SEGMENT] manufacturing companies in [CITY/STATE], India
that have 500+ employees or turnover above 500 crore.
For each company provide:
- Company name (full official name)
- Headquarters city
- Approximate employee count or turnover
- Whether they are an MNC subsidiary or large Indian corporate
- Website URL if known

Focus only on companies with actual manufacturing plants (not pure trading or services).
Exclude MSMEs (under 250 crore turnover).
```

### Segment-Specific Prompts

#### Automotive — Tamil Nadu
```
List the top 25 automotive component manufacturers in Tamil Nadu, India
with 500+ employees. Include companies in Chennai, Hosur, Coimbatore,
Sriperumbudur, Oragadam, and Ambattur industrial clusters.

For each: company name, city, headcount estimate, MNC or Indian corporate,
website URL. Focus on: stamping, forgings, castings, weld assemblies,
plastics, rubber, electronics/wiring harness.
```

#### Automotive — South Karnataka
```
List the top 20 automotive component manufacturers in South Karnataka, India
with 500+ employees. Focus on Bengaluru, Peenya, Whitefield, Mysuru, and
Tumkur industrial areas.

For each: company name, city, headcount estimate, MNC or Indian corporate,
website URL.
```

#### FMCG / F&B
```
List the top 25 FMCG and food & beverage manufacturing companies in
Tamil Nadu and Karnataka with over 500 employees. Include companies in
Chennai, Coimbatore, Mysuru, Bengaluru, and Trichy.

Focus on: packaged foods, beverages, dairy, snacks, oils, spices.
For each: company name, city, headcount, website URL.
```

#### Pharma
```
List the top 20 pharmaceutical manufacturing companies in Tamil Nadu
with over 500 employees. Focus on API manufacturers, formulations plants,
and biotech facilities in Chennai, Ambattur, Oragadam, and Sriperumbudur.

For each: company name, location, headcount, product type (API/formulations),
website URL.
```

#### Metals
```
List the top 20 metals manufacturing companies in Tamil Nadu and South Karnataka
with 500+ employees. Include steel rolling, aluminium processing, copper wire,
castings, and forging units in Coimbatore, Salem, Trichy, Davangere, and Bengaluru.

For each: company name, city, product type, headcount estimate, website URL.
```

#### Chemicals
```
List the top 20 specialty chemical and paint/coatings manufacturers in
Tamil Nadu and Karnataka with 500+ employees.

For each: company name, city, product type (specialty/paint/adhesive/polymer),
headcount, website URL.
```

#### Packaging
```
List the top 20 packaging manufacturers in Tamil Nadu and Karnataka
with 500+ employees. Include corrugated, flexible packaging, rigid plastics,
glass, and label printing companies.

For each: company name, city, product type, headcount estimate, website URL.
```

#### Machinery OEMs
```
List the top 20 industrial machinery and machine tool manufacturers in
Tamil Nadu and Karnataka (especially Coimbatore and Bengaluru) with 200+
employees. Include CNC machine builders, pump manufacturers, conveyor
manufacturers, and automation equipment OEMs.

For each: company name, city, product type, headcount, website URL.
```

---

## Phase 2: Account Snapshot Prompts

Run these for each shortlisted company before making contact. Paste results into the `notes` column.

### Safety Culture Research
```
Research [COMPANY NAME]'s workplace health and safety culture.

Find and summarize:
1. ISO 45001 or OHSAS 18001 certification status
2. Any safety awards or recognitions (British Safety Council, NSC, Greentech, etc.)
3. "Zero Harm" or similar safety programs
4. EHS policy page or annual safety report
5. Any reported safety incidents or fatalities (last 5 years)
6. Dedicated EHS team mentions or leadership quotes on safety
7. Plant locations in India

Keep your answer to 150-200 words. Cite sources.
```

### Plant Expansion / Growth Signals
```
Research recent news about [COMPANY NAME] India in the last 2 years:
- New plant openings or expansions in Tamil Nadu or Karnataka
- Capacity additions or new product lines
- Major capital investments
- New MNC safety standards rollout (ISO 45001, Zero Harm, etc.)

List findings as bullet points with approximate dates.
```

### Pain Point Hypothesis
```
[COMPANY NAME] is a [SEGMENT] manufacturer in [CITY] with [SIZE] employees.
They [are ISO 45001 certified / have a Zero Harm program / have no visible EHS program].

As a machine safety expert, what are the top 3 likely machine safety risks
or compliance gaps at this type of plant? Be specific to their manufacturing
process (e.g., press shop, packaging line, chemical handling).

For each risk: name it, explain why it's common in this segment, and suggest
one engineering control or audit type that would address it.
```

---

## Phase 3: Contact Identification Prompts

Use these to find the right person at a company before looking them up on Sales Navigator.

### EHS Contact Search
```
Who is the EHS Head, Safety Manager, or HSE Director at [COMPANY NAME] India?
Find their name and title from public sources (LinkedIn, company website,
press releases, safety award citations, conference speaker lists).

If you cannot find a specific name, what is the typical EHS team structure
at a company of this size in this industry?
```

### Boardline / Email Format
```
What is the general phone number (boardline) for [COMPANY NAME]'s
[CITY] plant or head office? Also, what is the standard email format
used by employees at [COMPANY NAME] (e.g., firstname.lastname@company.com)?

Find from: company website contact page, press releases, annual report.
```

---

## Phase 4: Converting Perplexity Output to CSV

### Step 1: Extract the company list

After running Phase 1 prompts, you'll have a list like:
```
1. Sundaram Clayton Ltd — Chennai — 4,000 employees — Indian corporate — www.sundram.com
2. Wheels India Ltd — Chennai — 3,500 employees — Indian corporate — www.wheelsindia.com
...
```

### Step 2: Create a raw CSV

Open a text editor or Excel and create a file with these columns:
```
company_name,plant_locations,employee_band,website,source,notes
```

Fill in rows from the Perplexity output. Save as `data/raw/perplexity_YYYY-MM-DD.csv`.

**employee_band conversion**:
| Perplexity says | Use in CSV |
|---|---|
| "200–500 employees" | `<500` (borderline — verify before including) |
| "500–1000 employees" | `500-1000` |
| "1000–5000 employees" | `1000-5000` |
| "5000+ employees" | `5000+` |

### Step 3: Run normalize_csv.py

```bash
python scripts/normalize_csv.py \
  --input data/raw/perplexity_2026-03-31.csv \
  --source Perplexity
```

The script will:
- Infer `hq_state` (TN/KA) from city names
- Infer `segment` from company name/industry keywords
- Assign UUIDs to new records
- Flag near-duplicates (companies already in your DB)

---

## Segment-Specific EHS Pain Point Reference

Use this when personalizing messages or building your pitch hypothesis.

| Segment | Top Machine Safety Risks | Best Audit Entry Point |
|---|---|---|
| **Automotive** | Press guarding gaps, robotic cell access, welding fume + arc flash, LOTO compliance | "Press line safety audit" or "Robot cell risk assessment" |
| **FMCG/F&B** | High-speed conveyor nip points, packaging line guarding, LOTO during CIP | "Conveyor + packaging line guarding review" |
| **Pharma** | ATEX zone classification, confined space entry, chemical handling, containment | "ATEX zone documentation audit" |
| **Metals** | Overhead crane SWL compliance, hot work near combustibles, molten metal splash | "Overhead lifting equipment safety audit" |
| **Packaging** | Slitter knife safety, printing press guards, web break reachthrough | "Cutting + slitting machine guarding survey" |
| **Chemicals** | ATEX + explosive atmospheres, pressure vessel inspection, emergency isolation | "Pressure system safety review (PSSR)" |
| **Machinery OEM** | CE marking conformity, risk assessment quality, functional safety (SIL/PLr) | "CE marking readiness assessment" |

---

## Weekly Discovery Checklist

Each Monday, before starting Sales Navigator:

```
[ ] Run Phase 1 Perplexity prompt for this week's segment (see rotation in sales_nav_guide.md)
[ ] Cross-check Perplexity list vs. known accounts (avoid re-adding existing companies)
[ ] Identify top 5 new accounts from Perplexity + Sales Nav combined
[ ] Run Phase 2 account snapshot for those 5 companies
[ ] Add raw data to data/raw/accounts_YYYY-MM-DD.csv
[ ] Run normalize_csv.py
[ ] Review duplicate_flag — resolve manually before Tuesday enrichment
[ ] Note 2-3 specific pain point hypotheses in the notes column for top accounts
```

---

## AI Tool Selection Guide

| Task | Best Tool | Why |
|---|---|---|
| Company list generation | Perplexity | Real-time web search; cites sources |
| Account snapshot (safety culture) | Perplexity | Searches public web including EHS pages |
| Pain point hypothesis | Claude (chat) | Reasoning + industry knowledge synthesis |
| Message personalization | Claude (chat) | Better at tone, nuance, and copy quality |
| Dedup, scoring, syncing | Claude Code | Script execution + data manipulation |
| PDF annual reports | Claude (upload) | Multi-modal; reads EHS data from PDFs |
