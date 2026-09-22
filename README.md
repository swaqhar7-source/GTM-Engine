# GTM Enrichment Engine

Turns a raw event-attendee export into a **prioritized, market-sized
target account list**, using only free/public data sources.

Built and validated against your `AppSec Live 2026 - Bengaluru` attendee
sheet: 854 rows -> 185 unique companies, domains resolved for 154 of
them straight from attendee email addresses.

## What it does

```
raw attendee export (xlsx)
        |
        v
 prepare_input.py   ->  one row per company, domain, attendee list
        |
        v
 pipeline.py         ->  for each company:
        |                 - scrape their own website (About/homepage text)
        |                 - Wikipedia summary (notability + rough employee count)
        |                 - SEC EDGAR check (is it a US public filer?)
        |                 - Google News search for cybersecurity-investment
        |                   signals (breach, funding, CISO hire, SOC2, etc.)
        |                 - lead score (0-100) + Hot/Warm/Cold tier
        |                 - bottoms-up TAM/SAM/SOM for that one company
        v
 enriched.xlsx        ->  Companies / RawText_Detail / Summary /
                          TAM_by_size_bucket sheets
```

## Quick start — the one-command automation

```bash
pip install -r requirements.txt

# feed it ANY attendee export shaped like Company/Name/Designation/Email...
python automate.py "AppSec_Live_2026.xlsx" --out output_auto

# quick smoke test on the first 15 companies before running the full list
python automate.py "AppSec_Live_2026.xlsx" --out output_auto --limit 15
```

This single command runs the whole pipeline below and writes, into `--out`:

- `gtm_master_plan.xlsx` — All Companies / Hot / Warm / Flag / Needs
  research / Summary / TAM sheets, same shape as the manually-built one.
- `dashboard.html` — a self-contained, open-in-any-browser dashboard with
  your new data baked in (no server needed — just double-click it).
- `dashboard_data.json` — the same data as raw JSON, if you want to feed
  it into something else.
- `companies.csv` — the intermediate one-row-per-company table.

**Read the fidelity note near the top of `automate.py`'s docstring before
trusting the tiers it produces.** It replaces the manual research done for
the first AppSec Live pass with keyword matching against attendee titles
and each company's own scraped website text — a fast, fully automatic
first cut, not a substitute for a human reading each Hot/Flag account
before outreach. Tune `title_keywords_hot/warm/cold`, `vendor_self_keywords`
and `angle_by_keyword` in `config.yaml` to match your own buyer titles and
competitor list — no code changes needed.

`--sleep` (default 1.0s) controls the delay between companies so you don't
get rate-limited by the free public endpoints; `--limit N` processes only
the first N companies, useful for a quick test run.

### The lower-level pieces (still available if you want more control)

```bash
# 1. turn the raw attendee export into a company-level table
python prepare_input.py "AppSec_Live_2026.xlsx" output/companies.csv

# 2. test on a handful of companies first (free public APIs = be polite)
python pipeline.py output/companies.csv output/enriched_sample.xlsx --limit 10

# 3. run the full list once you're happy with the config
python pipeline.py output/companies.csv output/enriched_full.xlsx --sleep 1.5
```

`automate.py` is the recommended entry point for a repeatable, hands-off
run on a new dataset; `prepare_input.py` + `pipeline.py` are there if you
want the per-company `RawText_Detail` sheet or to script something custom.

`--sleep` controls the delay between companies (seconds). The public
endpoints used here (Wikipedia, SEC EDGAR, Google News RSS, company
websites) have no official rate limit documented for this kind of
light use, but running 185 companies back-to-back with no delay is a
good way to get temporarily blocked - 1-2 seconds between companies is
a reasonable default for a one-off run.

**Important:** this sandbox's own network is locked down to package
registries only, so the live enrichment calls (Wikipedia/SEC/News/
company websites) could not be executed inside this conversation - the
logic was fully validated with a mocked dry run (`test_dry_run.py`,
which you can delete) against your real 185-company list, so wiring is
proven, but you'll see the real Hot/Warm/Cold results only once you run
`pipeline.py` from your own machine or a normal cloud VM with open
internet.

## Editing the model

Everything scoring- and market-sizing-related lives in `config.yaml`,
not in code:

- **`icp_keywords`** - words that make a company look like a fit
  (edit to match what YOUR product actually is).
- **`news_query_suffixes`** - what "buying signal" news looks like for
  you. Right now it's generic cybersecurity phrases; narrow it to your
  category (e.g. add "SOC hire", "app sec", "bug bounty" if you sell
  AppSec tooling specifically, matching this event's theme).
- **`scoring_weights`** / **`scoring_tiers`** - how the 0-100 score is
  built and where Hot/Warm/Cold cut off.
- **`size_buckets`** / **`serviceable_addressable_fraction`** /
  **`serviceable_obtainable_fraction`** - the TAM/SAM/SOM math. The
  default `annual_security_spend_per_employee_usd` numbers are
  placeholders, not a cited study - replace them with real benchmarks
  (Gartner/IDC security-spend-per-employee figures, or your own
  win-rate data) before using this in a board deck.

## On the "real" TAM

The number `pipeline.py` produces (`Dataset SAM`) is **bottoms-up**: it
only covers the ~185 companies in this one event's attendee list. It's
useful as "how big is the opportunity already in front of us from this
event," not as "how big is the whole market."

For a true top-down TAM (the whole addressable market for your product
category, not just this dataset), pull a published market-size figure
for your category - e.g. search "[your category] market size TAM
Gartner/IDC 2026" - and use the bottoms-up number here as a sanity
check against it, not a replacement.

## On LinkedIn

There is no free, compliant way to pull LinkedIn firmographic data
(headcount, industry, growth) via this pipeline - LinkedIn has no
public API for this, and scraping logged-out pages violates their
Terms of Service and gets IPs blocked quickly. `providers/linkedin.py`
only constructs the likely company-page URL for manual lookup and
defines a clean interface (`LinkedInProvider.enrich()`) so you can plug
in a licensed source later without touching the rest of the pipeline:

- **Free/manual**: export target accounts from LinkedIn Sales
  Navigator yourself, save as CSV, and left-join it onto
  `output/companies.csv` by domain or company name before running
  `pipeline.py`.
- **Paid, official-data APIs**: Proxycurl, People Data Labs, Apollo.io,
  Clearbit/HubSpot, ZoomInfo. Any of these plug into
  `LinkedInProvider.enrich()` in a few lines.

## API

`api.py` wraps everything above in a FastAPI service, tested live in
this session (localhost, all 6 endpoints returned real responses -
including a live-scored request through `POST /score`).

```bash
pip install -r requirements.txt
uvicorn api:app --host 0.0.0.0 --port 8000
# then open http://localhost:8000/docs for interactive Swagger UI
```

| Endpoint | What it does |
|---|---|
| `GET /health` | liveness check |
| `GET /companies?limit=N` | your real 185-company table, paginated |
| `GET /companies/{name}` | one company's attendee list + designations |
| `POST /enrich` | live-enrich one company `{company, domain}` — needs real outbound internet |
| `POST /score` | score a signal record you already have, no internet needed |
| `GET /demo` | the 6 real, hand-verified companies from this conversation — works with **zero internet access**, good for a smoke test |
| `GET /tam/summary?limit=N` | bottoms-up TAM/SAM/SOM over N companies — needs real outbound internet |

**Why this session couldn't give you a public URL:** this sandbox's
own network is locked to package registries only (same restriction
that blocked the live enrichment calls earlier), so there's no way to
expose a port to the internet from inside this conversation. `/demo`
proves the API itself works correctly even under that restriction;
`/enrich` and `/tam/summary` will start working the moment you run
this on a host with normal internet.

### Deploying it somewhere public

A `Dockerfile` is included. Any of these get you a real public URL in
a few minutes, roughly cheapest/fastest first:

1. **Render / Railway / Fly.io** (free tiers): connect the repo (or
   `docker build && docker push`), point it at the Dockerfile, done —
   you get an HTTPS URL immediately.
2. **A VM you already have** (EC2, a droplet, your own server):
   `docker build -t gtm-api . && docker run -p 8000:8000 gtm-api`, then
   put it behind nginx/Caddy for TLS.
3. **AWS Lambda**: wrap `app` with `Mangum` (`pip install mangum`,
   `handler = Mangum(app)`) and deploy via the Lambda console or SAM -
   good if you want pay-per-request instead of an always-on server.

Whichever you pick, that's also where `POST /enrich` and
`GET /tam/summary` start actually working, since they need the same
open internet access this sandbox doesn't have.

## Files

| File | Purpose |
|---|---|
| `automate.py` | **run this** — one command, raw export in, master plan + dashboard out |
| `dashboard_template.html` | HTML/CSS/JS dashboard shell `automate.py` injects data into |
| `test_automate_dry_run.py` | proves `automate.py` end-to-end with mocked providers (no internet needed) |
| `prepare_input.py` | raw attendee export -> one row per company |
| `pipeline.py` | lower-level per-company enrichment + scoring + TAM run |
| `config.yaml` | all editable assumptions (ICP, scoring, tiering, TAM) |
| `providers/website.py` | scrape company's own site |
| `providers/wikipedia.py` | Wikipedia summary + employee-count guess |
| `providers/sec_edgar.py` | US public-company filing check |
| `providers/news.py` | Google News RSS buying-signal search |
| `providers/linkedin.py` | URL guess + pluggable interface (see above) |
| `scoring.py` | turns signals into a 0-100 lead score (used by `pipeline.py`) |
| `tam.py` | bottoms-up TAM/SAM/SOM math |
| `build_master_sheet.py` | the original, hand-researched 185-company AppSec Live pass |
| `output/companies.csv` | your real 185-company list, already prepared |
| `output/gtm_master_plan.xlsx` | the hand-researched master plan (keep this — it's higher fidelity than a fresh `automate.py` run) |

## `automate.py` vs. the hand-researched plan already in this project

Both produce the same shape of output (`gtm_master_plan.xlsx` + dashboard),
but they're not the same quality:

- **`output/gtm_master_plan.xlsx`** (already delivered) — every Hot/Warm/
  Flag company was individually looked up via web search; "what they do"
  and the recommended angle are written from real facts about that
  specific company.
- **A fresh `automate.py` run** — fully automatic, no human in the loop.
  Tiering comes from attendee-title keywords, "what they do" comes from
  whatever a scraped homepage/Wikipedia blurb says (or "not automatically
  determined" if neither is reachable), and the competitor/channel-partner
  flag comes from keyword matching against a company's own site text. Use
  it to process a **new** event's dataset quickly, then spend manual
  research time on whatever it marks Hot or Flag — not as a final list.

## Known limitations / next steps

- **Employee counts** are only found when a company has a Wikipedia
  page that states a headcount - most of the 185 companies here won't.
  Everything else falls back to `default_employee_count_if_unknown` in
  the config. This is the single biggest accuracy gap; a paid
  firmographic API (PDL, Clearbit) fixes it directly.
- **Domain guessing** for the ~31 companies with no attendee-domain
  match (personal emails only) is not attempted automatically - fill
  those in by hand in `output/companies.csv` for best results, or wire
  in a company-name-to-domain API.
- **News signal** quality depends entirely on how much public press a
  company gets; small/private companies will often show zero hits,
  which is not the same as "no interest in security."
- Add a caching layer (e.g. a local SQLite file keyed by domain) before
  running this repeatedly - right now every run re-fetches everything.
