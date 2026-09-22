"""
Main GTM enrichment pipeline.

Input:  a CSV with at least a 'company' column (a 'domain' column is
        used when present - run prepare_input.py first if you're
        starting from a raw event-registration export).
Output: an Excel workbook with one row per company: enrichment
        signals, lead score/tier, and TAM/SAM/SOM estimate - plus a
        Summary sheet with dataset-wide market sizing.

Usage:
    python pipeline.py output/companies.csv output/enriched.xlsx
    python pipeline.py output/companies.csv output/enriched.xlsx --limit 20
"""
from __future__ import annotations
import argparse
import sys
import time

import pandas as pd
import yaml

from providers import website, wikipedia, sec_edgar, news, linkedin
from scoring import score_company
from tam import estimate_company_tam, aggregate_dataset_tam


def load_config(path: str = "config.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def enrich_one(company: str, domain: str | None, cfg: dict) -> dict:
    record: dict = {"company": company, "domain": domain}

    # --- website -----------------------------------------------------
    if domain:
        site = website.fetch_homepage_text(domain)
        if "error" not in site:
            record["website_title"] = site.get("title")
            record["website_meta_description"] = site.get("meta_description")
            record["website_text"] = site.get("text")
        else:
            record["website_error"] = site["error"]

    # --- wikipedia -----------------------------------------------------
    wiki = wikipedia.fetch_summary(company)
    record["wikipedia_found"] = wiki.get("found", False)
    if wiki.get("found"):
        record["wikipedia_extract"] = wiki.get("extract")
        record["wikipedia_url"] = wiki.get("url")
        record["employee_count"] = wikipedia.guess_employee_count(wiki.get("extract", ""))
    else:
        record["employee_count"] = None

    # --- SEC EDGAR (US public companies only) --------------------------
    sec = sec_edgar.has_sec_filings(company)
    record["is_public_company"] = sec.get("is_public", False)

    # --- news / buying-intent signals -----------------------------------
    hits = news.search_news(
        company, cfg["news_query_suffixes"], cfg["news_lookback_days"]
    )
    record["news_hits"] = hits
    record["news_hit_count"] = len(hits)
    record["news_headlines"] = " | ".join(h["title"] for h in hits[:5])

    # --- linkedin (stub - see providers/linkedin.py) --------------------
    li = linkedin.LinkedInProvider().enrich(company, domain)
    record["linkedin_url_guess"] = li["linkedin_url_guess"]

    # --- scoring ---------------------------------------------------------
    record.update(score_company(record, cfg))

    # --- TAM/SAM/SOM for this one company --------------------------------
    record.update(estimate_company_tam(record.get("employee_count"), cfg))

    return record


def run(input_csv: str, output_xlsx: str, config_path: str, limit: int | None,
        sleep_seconds: float):
    cfg = load_config(config_path)
    df = pd.read_csv(input_csv)
    if limit:
        df = df.head(limit)

    records = []
    total = len(df)
    for i, row in df.iterrows():
        company = row["company"]
        domain = row.get("domain") if "domain" in row and pd.notna(row.get("domain")) else None
        print(f"[{i+1}/{total}] enriching {company} ({domain or 'no domain'}) ...", file=sys.stderr)
        try:
            rec = enrich_one(company, domain, cfg)
        except Exception as e:  # keep going - one bad company shouldn't kill the run
            rec = {"company": company, "domain": domain, "error": str(e)}
        # carry through anything useful from the input (attendees, counts)
        for col in df.columns:
            if col not in rec:
                rec[col] = row[col]
        records.append(rec)
        time.sleep(sleep_seconds)  # be polite to free public endpoints

    out_df = pd.DataFrame(records)

    tam_summary = aggregate_dataset_tam(records)

    with pd.ExcelWriter(output_xlsx, engine="openpyxl") as writer:
        # Trim the huge text blobs before writing the main sheet;
        # keep them in a separate sheet for anyone who wants the detail.
        detail_cols = ["company", "website_text", "wikipedia_extract", "news_hits"]
        main_cols = [c for c in out_df.columns if c not in
                     ("website_text", "wikipedia_extract", "news_hits")]
        out_df[main_cols].to_excel(writer, sheet_name="Companies", index=False)

        detail_df = out_df[[c for c in detail_cols if c in out_df.columns]]
        detail_df.to_excel(writer, sheet_name="RawText_Detail", index=False)

        summary_rows = [
            {"metric": "Companies enriched", "value": tam_summary["company_count"]},
            {"metric": "Dataset bottoms-up est. total security spend (USD)",
             "value": tam_summary["dataset_bottoms_up_market_spend_usd"]},
            {"metric": "Dataset SAM (USD)", "value": tam_summary["dataset_sam_usd"]},
            {"metric": "Dataset SOM - next 12mo (USD)", "value": tam_summary["dataset_som_usd"]},
        ]
        pd.DataFrame(summary_rows).to_excel(writer, sheet_name="Summary", index=False)

        bucket_rows = [
            {"size_bucket": k, **v} for k, v in tam_summary["by_size_bucket"].items()
        ]
        pd.DataFrame(bucket_rows).to_excel(writer, sheet_name="TAM_by_size_bucket", index=False)

    print(f"\nDone. Wrote {len(out_df)} companies to {output_xlsx}", file=sys.stderr)
    print(f"Dataset SAM estimate: ${tam_summary['dataset_sam_usd']:,}", file=sys.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv")
    parser.add_argument("output_xlsx")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--limit", type=int, default=None, help="only process first N companies (for testing)")
    parser.add_argument("--sleep", type=float, default=1.0, help="seconds to sleep between companies (be polite to free APIs)")
    args = parser.parse_args()
    run(args.input_csv, args.output_xlsx, args.config, args.limit, args.sleep)
