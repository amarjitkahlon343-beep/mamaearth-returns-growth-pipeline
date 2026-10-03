# Mamaearth Returns & Growth Intelligence Pipeline

Capstone — Data Analytics with AI & Gen AI · E&ICT Academy IIT Roorkee  
One public GitHub repository. Every number in this brief is produced by running the three layers below against the committed seed data.

## Repository structure

```
<repo>/
├── README.md
├── sql/
│   ├── schema.sql
│   ├── seed_data.sql
│   └── reports.sql
├── data/
│   ├── customers.csv
│   ├── products.csv
│   └── orders.csv
├── analysis/
│   ├── clean_and_eda.py
│   └── visualize.py
├── visualizations/
│   ├── return_rate_by_payment.png
│   └── monthly_revenue_trend.png
└── narrator/
    ├── findings.json
    └── generate_narrative.py
```

## How the three layers connect

1. **SQL layer** loads the same CSVs into SQLite and answers relational questions on the *raw* 180 rows (gross revenue ₹99,860.20).
2. **Python layer** re-reads the same CSVs, cleans them (payment casing, 5 duplicates, imputations, IQR flags), and writes verified numbers to `narrator/findings.json` (cleaned revenue ₹97,358.30).
3. **GenAI layer** reads *only* `findings.json` and produces an SCR narrative (online Gemini or offline template). No layer invents a number the previous layer did not compute.

---

## 1. SQL layer — schema, seed, reports

Requires SQLite 3 (or any engine that accepts the syntax in `schema.sql`).

```bash
# Create empty DB and apply schema
sqlite3 mamaearth.db < sql/schema.sql

# Load seed (45 customers, 16 products, 180 orders)
sqlite3 mamaearth.db < sql/seed_data.sql

# Sanity counts
sqlite3 mamaearth.db "SELECT COUNT(*) FROM customers;"   # → 45
sqlite3 mamaearth.db "SELECT COUNT(*) FROM products;"    # → 16
sqlite3 mamaearth.db "SELECT COUNT(*) FROM orders;"      # → 180

# Run all Task 3 reports (a–i); expected outputs are comments above each query
sqlite3 mamaearth.db < sql/reports.sql
```

If you use `.import` instead of `seed_data.sql`, run after import:

```sql
UPDATE orders SET discount_pct = NULL WHERE discount_pct = '';
UPDATE orders SET rating = NULL WHERE rating = '';
```

---

## 2. Python analysis layer — clean, EDA, charts, findings.json

```bash
pip install pandas matplotlib

# Task 1–10 of Part 2; also writes narrator/findings.json (Part 3 Task 1)
python analysis/clean_and_eda.py

# Task 11 — regenerates the two PNGs under visualizations/
python analysis/visualize.py
```

`clean_and_eda.py` prints every intermediate acceptance value (shape, payment counts, dropped order_ids, median rating, cleaned total ₹97,358.30, reconciliation paragraph, IQR bounds, return rates, segmentation, correlations, both monthly series).  
`findings.json` is written by this script — never hand-typed — so it cannot drift from Part 2.

---

## 3. GenAI narrative layer — online or offline

```bash
# Offline path (no API key) — deterministic SCR template, always gradable
python narrator/generate_narrative.py

# Online path — free Gemini key from Google AI Studio
export GEMINI_API_KEY="your-free-key-here"
python narrator/generate_narrative.py
```

- **With `GEMINI_API_KEY` (or `GOOGLE_API_KEY`) set**: calls `google-genai` with `temperature=0.0`, explicit `max_output_tokens`, and timeout ≥ 10s; returns a structured `{status, narrative, tokens}` dict; on any failure falls back offline.
- **With no key**: runs `generate_scr_narrative_offline` only.

Both paths write `narrator/sample_output.txt` and run the Task 5 numeric accuracy checker (pass/fail line per figure). The grader verifies the saved sample, not a live API call.

Optional dependency for the online path only:

```bash
pip install google-genai
```

---

## Key verified figures

| Figure | Value |
|--------|-------|
| Raw total revenue (Part 1) | 99,860.20 |
| Cleaned total revenue (Part 2) | 97,358.30 |
| Duplicate reconciliation delta | 2,501.90 |
| COD / CARD / UPI return rates | 44.4% / 14.7% / 18.9% |
| Highest-risk segment | COD + Tier-2 at 54.5% |
| True peak month (outlier-corrected) | March 20,318.90 |

A reader who has never seen this repo can reproduce every number above by following this README top to bottom.
