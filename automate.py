"""
automate.py - one-command GTM automation.

    python automate.py attendees.xlsx --out output --sleep 1.5 [--limit 20]

Feed it any raw event-attendee export shaped like:
    Company | Name | Designation | Email | Contact Number
(column order/casing doesn't matter as long as those headers exist - see
prepare_input.py for the exact rules, including automatic Designation/Email
swap-detection, which this script reuses unchanged.)

It reproduces, automatically, the same kind of output that was built by
hand for the AppSec Live 2026 dataset earlier in this project:

  1. prepare_input.build_company_table()
         raw attendee rows -> one row per company, with a best-guess
         domain (from attendee emails) and the attendee list.

  2. Keyword tiering (100% offline, no internet needed)
         attendee job titles -> Hot / Warm / Cold / No Signal + a
         recommended sales angle, driven entirely by config.yaml
         (title_keywords_hot/warm/cold, angle_by_keyword). Edit that
         file, not this script, to match your own buyer titles.

  3. Live enrichment (best-effort, needs real outbound internet):
       - scrape the company's own website              (providers/website.py)
       - Wikipedia summary + employee-count guess       (providers/wikipedia.py)
       - SEC EDGAR public-filer check                   (providers/sec_edgar.py)
       - Google News cybersecurity-signal search         (providers/news.py)
     The scraped website text is also checked against
     vendor_self_keywords - a hit forces the tier to "Flag" (they sell
     something in this space themselves: a competitor, peer, or channel
     partner, not a normal lead).

  4. Bottoms-up TAM/SAM/SOM per company (tam.py), using whatever
     employee-count signal step 3 found (or the config default).

  5. Writes the same shape of deliverable as before:
       - <out>/gtm_master_plan.xlsx   (All Companies / Hot / Warm / Flag /
                                        Needs research / Summary sheets)
       - <out>/dashboard_data.json
       - <out>/dashboard.html         (self-contained, ready to open/share)

READ THIS BEFORE TRUSTING THE OUTPUT
-------------------------------------
This automatic pass is lower-fidelity than a human researching each
company. Keyword matching will miss nuance, miss competitors who don't use
the exact vendor_self_keywords phrasing, and can mis-tier a company whose
attendee titles happen to be generic. Treat "Hot" and "Flag" here as a fast
first cut to prioritize where to spend manual research time next - not as
a final call. Spot-check every Hot and every Flag before using this list
for outreach.

This sandbox's own shell cannot reach company websites, Wikipedia, SEC
EDGAR or Google News (its network is locked to package registries only) -
so step 3 (live enrichment) has to be run from your own machine or a
normal cloud VM with open internet. Steps 1, 2, 4 and 5 need no internet
at all and will run anywhere, immediately, on any dataset you feed in.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import pandas as pd
import yaml

from prepare_input import build_company_table
from providers import website as website_provider
from providers import wikipedia as wikipedia_provider
from providers import sec_edgar as sec_provider
from providers import news as news_provider
from tam import estimate_company_tam, aggregate_dataset_tam

HERE = Path(__file__).resolve().parent


def load_config(path: str = None) -> dict:
    path = path or str(HERE / "config.yaml")
    with open(path, "r") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------
# Step 2: offline keyword tiering (no internet required)
# ---------------------------------------------------------------------

def tier_and_angle_from_attendees(attendees_text: str, cfg: dict) -> dict:
    """Looks for hot/warm/cold title keywords in the attendee list text.
    Hot beats warm beats cold - order matters, matching build_master_sheet.py's
    original logic. Returns {'tier', 'signal_keywords', 'recommended_angle'}."""
    text = (attendees_text or "").lower()

    hot = [kw for kw in cfg.get("title_keywords_hot", []) if kw in text]
    warm = [kw for kw in cfg.get("title_keywords_warm", []) if kw in text]
    cold = [kw for kw in cfg.get("title_keywords_cold", []) if kw in text]

    if hot:
        tier, hits = "Hot", hot
    elif warm:
        tier, hits = "Warm", warm
    elif cold:
        tier, hits = "Cold", cold
    else:
        tier, hits = "No Signal", []

    angle = None
    for rule in cfg.get("angle_by_keyword", []):
        if any(kw in hits for kw in rule.get("match", [])):
            angle = rule["angle"]
            break
    if angle is None:
        angle = (
            cfg.get("default_angle_with_signal")
            if hits
            else cfg.get("default_angle_no_signal")
        )

    return {"tier": tier, "signal_keywords": hits, "recommended_angle": angle}


def detect_vendor_flag(website_text: str, cfg: dict) -> str | None:
    """Checks a company's own scraped website text for phrases that mean
    THEY sell something in this space - i.e. flag as competitor/peer/
    channel-partner instead of scoring as a normal lead."""
    text = (website_text or "").lower()
    for kw in cfg.get("vendor_self_keywords", []):
        if kw in text:
            return f"Company's own site mentions '{kw}' - possible competitor/peer/channel partner, verify before treating as a standard lead."
    return None


# ---------------------------------------------------------------------
# Step 3: live, best-effort enrichment (needs real internet)
# ---------------------------------------------------------------------

def enrich_company(company: str, domain: str | None, cfg: dict) -> dict:
    """Best-effort automatic research for one company. Every provider call
    is wrapped so a network failure (expected inside this sandbox, possible
    anywhere on a flaky connection) degrades to 'not found' instead of
    crashing the whole run."""
    result = {
        "what_they_do": None,
        "employee_count": None,
        "is_public_company": False,
        "recent_news": [],
        "vendor_flag": None,
        "research_depth": "Automated",
    }

    site = {}
    if domain:
        try:
            site = website_provider.fetch_homepage_text(domain) or {}
        except Exception:
            site = {}
    if site and not site.get("error"):
        blurb = site.get("meta_description") or site.get("title") or ""
        if blurb:
            result["what_they_do"] = blurb.strip()[:400]
        result["vendor_flag"] = detect_vendor_flag(site.get("text", ""), cfg)

    try:
        wiki = wikipedia_provider.fetch_summary(company) or {}
    except Exception:
        wiki = {}
    if wiki.get("found"):
        if not result["what_they_do"] and wiki.get("extract"):
            result["what_they_do"] = wiki["extract"][:400]
        result["employee_count"] = wikipedia_provider.guess_employee_count(
            wiki.get("extract", "")
        )

    try:
        sec = sec_provider.has_sec_filings(company) or {}
    except Exception:
        sec = {}
    result["is_public_company"] = bool(sec.get("is_public"))

    try:
        news = news_provider.search_news(
            company, cfg.get("news_query_suffixes", []), cfg.get("news_lookback_days", 365)
        )
    except Exception:
        news = []
    result["recent_news"] = news or []

    if not result["what_they_do"]:
        result["what_they_do"] = (
            "Not automatically determined - no reachable website/Wikipedia "
            "summary found. Needs a manual look."
        )

    return result


def build_signal_text(row: dict) -> str:
    parts = []
    if row.get("recent_news"):
        titles = "; ".join(n["title"] for n in row["recent_news"][:2])
        parts.append(f"Recent news: {titles}")
    if row.get("is_public_company"):
        parts.append("SEC-reporting public company.")
    if row.get("signal_keywords"):
        parts.append("Attendee title signal: " + ", ".join(row["signal_keywords"]))
    return " ".join(parts) if parts else "No automated signal found - needs manual research."


# ---------------------------------------------------------------------
# Step 4 + 5: TAM, Excel, dashboard JSON/HTML
# ---------------------------------------------------------------------

MASTER_COLUMNS = [
    "tier", "company", "domain", "attendee_count", "what_they_do",
    "signal", "recommended_angle", "flag", "attendees", "research_depth",
]


def write_master_excel(records: list[dict], out_path: Path, tam_summary: dict) -> None:
    df = pd.DataFrame(records)[MASTER_COLUMNS + ["est_total_security_spend_usd", "est_sam_usd", "est_som_usd", "size_bucket"]]
    df = df.sort_values(
        by="tier",
        key=lambda s: s.map({"Hot": 0, "Warm": 1, "Cold": 2, "Flag": 3, "No Signal": 4}),
    )

    summary = df["tier"].value_counts().rename_axis("tier").reset_index(name="count")
    tam_df = pd.DataFrame(
        [{"metric": k, "value": v} for k, v in tam_summary.items() if not isinstance(v, dict)]
    )
    by_bucket_df = pd.DataFrame(
        [{"size_bucket": k, **v} for k, v in tam_summary.get("by_size_bucket", {}).items()]
    )

    with pd.ExcelWriter(out_path) as writer:
        df.to_excel(writer, sheet_name="All Companies", index=False)
        df[df.tier == "Hot"].to_excel(writer, sheet_name="Hot", index=False)
        df[df.tier == "Warm"].to_excel(writer, sheet_name="Warm", index=False)
        df[df.tier == "Flag"].to_excel(writer, sheet_name="Flag (not standard sales)", index=False)
        df[df.tier.isin(["Cold", "No Signal"])].to_excel(writer, sheet_name="Needs research", index=False)
        summary.to_excel(writer, sheet_name="Summary", index=False)
        tam_df.to_excel(writer, sheet_name="TAM_Summary", index=False)
        by_bucket_df.to_excel(writer, sheet_name="TAM_by_size_bucket", index=False)


def write_dashboard(records: list[dict], out_dir: Path) -> Path:
    dash_records = [{k: r.get(k) for k in MASTER_COLUMNS} for r in records]
    data_json_path = out_dir / "dashboard_data.json"
    with open(data_json_path, "w") as f:
        json.dump({"companies": dash_records}, f, indent=2, default=str)

    template_path = HERE / "dashboard_template.html"
    html = template_path.read_text()
    html = html.replace("__DATA_JSON__", json.dumps({"companies": dash_records}, default=str))
    out_html = out_dir / "dashboard.html"
    out_html.write_text(html)
    return out_html


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def run(input_path: str, out_dir: str, config_path: str | None, limit: int | None, sleep_seconds: float) -> None:
    cfg = load_config(config_path)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    print(f"[1/5] Parsing '{input_path}' into a company-level table...")
    companies_df = build_company_table(input_path)
    companies_df.to_csv(out / "companies.csv", index=False)
    if limit:
        companies_df = companies_df.head(limit)
    print(f"      -> {len(companies_df)} companies to process"
          f"{f' (limited to first {limit})' if limit else ''}")

    records = []
    total = len(companies_df)
    for i, row in enumerate(companies_df.itertuples(index=False), start=1):
        company, domain = row.company, row.domain
        print(f"[2-4/5] ({i}/{total}) {company} ...", end=" ", flush=True)

        tiering = tier_and_angle_from_attendees(row.attendees, cfg)
        enrichment = enrich_company(company, domain, cfg)

        tier = enrichment["vendor_flag"] and "Flag" or tiering["tier"]
        flag = enrichment["vendor_flag"] or ""

        tam = estimate_company_tam(enrichment["employee_count"], cfg)

        rec = {
            "tier": tier,
            "company": company,
            "domain": domain or "",
            "attendee_count": row.attendee_count,
            "what_they_do": enrichment["what_they_do"],
            "recommended_angle": tiering["recommended_angle"],
            "flag": flag,
            "attendees": row.attendees,
            "research_depth": enrichment["research_depth"],
            "signal_keywords": tiering["signal_keywords"],
            "recent_news": enrichment["recent_news"],
            "is_public_company": enrichment["is_public_company"],
            **tam,
        }
        rec["signal"] = build_signal_text(rec)
        records.append(rec)
        print(f"tier={tier}")

        if sleep_seconds and i < total:
            time.sleep(sleep_seconds)

    print("[5/5] Writing outputs...")
    tam_summary = aggregate_dataset_tam(records)
    write_master_excel(records, out / "gtm_master_plan.xlsx", tam_summary)
    dashboard_path = write_dashboard(records, out)

    print()
    print(f"Done. {total} companies processed.")
    print(f"  - {out / 'gtm_master_plan.xlsx'}")
    print(f"  - {dashboard_path}")
    print(f"  - {out / 'dashboard_data.json'}")
    tier_counts = pd.Series([r['tier'] for r in records]).value_counts().to_dict()
    print(f"  Tier breakdown: {tier_counts}")


def main():
    parser = argparse.ArgumentParser(description="One-command GTM automation: raw attendee export -> master account plan + dashboard.")
    parser.add_argument("input", help="Raw attendee export (.xlsx or .csv) with Company/Name/Designation/Email columns")
    parser.add_argument("--out", default="output_auto", help="Output directory (default: output_auto)")
    parser.add_argument("--config", default=None, help="Path to config.yaml (default: the one next to this script)")
    parser.add_argument("--limit", type=int, default=None, help="Only process the first N companies (useful for a quick test)")
    parser.add_argument("--sleep", type=float, default=1.0, help="Seconds to sleep between companies (be polite to free public endpoints)")
    args = parser.parse_args()

    run(args.input, args.out, args.config, args.limit, args.sleep)


if __name__ == "__main__":
    main()
