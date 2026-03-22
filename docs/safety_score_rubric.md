# Safety Maturity Score Rubric

> Used by `scripts/safety_score.py` to compute a 0–100 score per account
> from keyword signals found on public company websites.

---

## Score Interpretation

| Band | Score | Meaning | Selling Approach |
|---|---|---|---|
| **Advanced** | 76–100 | Multiple certifications, awards, BBS, published metrics | VAYON: advanced audits, functional safety, training programs |
| **Established** | 51–75 | ISO 45001 certified, some programs, possibly awarded | Compete on expertise; offer gap analysis between system and shop floor |
| **Developing** | 21–50 | Some programs, ISO in progress or older OHSAS | Position as accelerator; offer ISO support + guarding baseline |
| **Basic** | 0–20 | Reactive, compliance-minimum, no visible EHS program | Highest urgency messaging; lead with risk/liability framing |

---

## Scoring Categories and Points

### Category 1: Certifications (max 30 pts)

| Keyword(s) | Points | Notes |
|---|---|---|
| `iso 45001` | 20 | Most current OHS management standard |
| `ohsas 18001` | 15 | Predecessor to ISO 45001; still valid for some older sites |
| `iso 14001` | 10 | Environmental management; often co-certified with 45001 |

> **Cap**: 30 pts. If both ISO 45001 and ISO 14001 found: 20 + 10 = 30 (capped).

---

### Category 2: Programs (max 20 pts)

| Keyword(s) | Points | Notes |
|---|---|---|
| `zero harm` | 10 | Strong cultural signal (common in MNCs) |
| `zero accident` | 8 | Strong program signal |
| `zero injury` | 8 | Variant; may overlap with zero harm |
| `behaviour-based safety` / `behavior-based safety` | 5 | Indicates mature culture program |
| `bbs` | 4 | BBS acronym (only counted if context confirms safety) |
| `safety culture` | 5 | Explicit mention of culture program |
| `safety leadership` | 4 | Leadership safety involvement signal |

> **Cap**: 20 pts. Maximum 3 program keywords counted toward cap.

---

### Category 3: Awards (max 20 pts)

| Keyword(s) | Points | Notes |
|---|---|---|
| `british safety council` | 10 | Sword of Honour, Merit, Globe of Honour |
| `safety excellence award` | 10 | Generic; industry/association award |
| `national safety council` | 8 | NSC India awards |
| `nsc award` | 8 | NSC acronym |
| `greentech award` | 8 | Environment + safety leadership award (India) |
| `safety award` | 6 | Generic safety award mention |
| `ehs award` | 6 | Generic EHS award mention |

> **Cap**: 20 pts. Best 2 awards counted.

---

### Category 4: Policy Depth (max 15 pts)

| Keyword(s) | Points | Notes |
|---|---|---|
| `annual safety report` | 5 | Formal published report |
| `safety report` | 3 | Generic report mention |
| `ehs policy` | 5 | Dedicated EHS policy document/page |
| `hse policy` | 5 | HSE policy variant |
| `health and safety policy` | 4 | Explicit policy page |
| `safety management system` | 4 | SMS documentation signal |

> **Cap**: 15 pts.

---

### Category 5: Regulatory Signals (max 10 pts)

| Keyword(s) | Points | Notes |
|---|---|---|
| `factories act` | 5 | Explicit Factories Act compliance mention |
| `pssr` | 5 | Pressure Systems Safety Regulations |
| `machinery directive` | 5 | EU Machinery Directive (relevant for MNCs) |
| `functional safety` | 5 | SIL/PLr functional safety program |
| `ce marking` | 4 | CE marking (typically for OEM machinery) |
| `risk assessment` | 3 | Active risk assessment process mentioned |

> **Cap**: 10 pts.

---

### Category 6: Incident Transparency (max 5 pts)

| Keyword(s) | Points | Notes |
|---|---|---|
| `ltifr` | 5 | Lost Time Injury Frequency Rate published |
| `trir` | 5 | Total Recordable Incident Rate published |
| `lost time injury` | 4 | LTI data published |
| `safety metrics` | 3 | Safety KPIs published |
| `safety statistics` | 3 | Safety statistics published |

> **Cap**: 5 pts. Publishing safety metrics is a strong maturity signal.

---

## Total Score

```
total_score = min(
    certifications_score     (capped at 30)
  + programs_score           (capped at 20)
  + awards_score             (capped at 20)
  + policy_depth_score       (capped at 15)
  + regulatory_score         (capped at 10)
  + transparency_score       (capped at 5),
  100
)
```

---

## Limitations and Manual Override

The keyword-based score is a **proxy** — not a definitive assessment. Known limitations:

1. **Annual reports in PDF**: Keywords in PDF files are not extracted by the crawler. If you know a company publishes an EHS annual report, manually add +5 to their score and set `iso_45001 = TRUE` if confirmed.

2. **Non-English content**: Tamil or Kannada language EHS content will be missed. Manual review recommended for local Indian companies.

3. **Indirect signals**: A company may have strong safety culture visible only at trade shows or through industry contacts — not on their website. Mark with a `notes` entry and consider adjusting priority manually.

4. **False positives**: "Safety" in the context of cybersecurity or food safety may trigger keywords. Review flagged keywords in `keywords_found` column for obvious false positives.

5. **Score 0 ≠ poor safety culture**: Many good companies simply have minimal web presence. `crawl_status = no_ehs_content` with `safety_score = 0` should trigger manual research, not automatic downgrade.

---

## Manual Adjustment Guidelines

After scoring, review all accounts with `safety_score` between 40–60 manually.
Use Perplexity or company website to verify:

- Is ISO 45001 certification current (not expired)?
- Has the company won a safety award in the last 3 years?
- Is the EHS policy page up-to-date (recent date)?

Adjust `safety_score` manually in Google Sheets if warranted, and add a note in the `notes` column explaining the adjustment.
