"""
LIVE DEMO — not a mock.

This sandbox's shell/Python cannot reach the open internet (locked to
package registries only), so `pipeline.py`'s live HTTP calls can't run
inside this conversation. To still show a real working model, Claude
did the research these providers would normally do automatically —
via web search — for 6 real companies from your actual 185-company
list, then ran those REAL findings through the unmodified scoring.py
and tam.py modules.

Every fact in demo_records.py is sourced from an actual live web search
performed in this session (sources noted per company). Nothing here is
fabricated or randomly generated, unlike test_dry_run.py.

The same records power api.py's GET /demo endpoint, so the CLI output
below and the API response are guaranteed to match.

Run: python demo_live.py
"""
import pandas as pd
import yaml

from scoring import score_company
from tam import estimate_company_tam, aggregate_dataset_tam
from demo_records import REAL_DEMO_RECORDS

cfg = yaml.safe_load(open("config.yaml"))

# work on copies - REAL_DEMO_RECORDS is shared with api.py, don't mutate it
records = [dict(r) for r in REAL_DEMO_RECORDS]

for r in records:
    r["news_hit_count"] = len(r["news_hits"])
    r.update(score_company(r, cfg))
    r.update(estimate_company_tam(r.get("employee_count"), cfg))

df = pd.DataFrame(records)
tam_summary = aggregate_dataset_tam(records)

display_cols = ["company", "domain", "attendee_count", "lead_score", "lead_tier",
                 "news_hit_count", "is_public_company", "employee_count",
                 "size_bucket", "est_sam_usd", "icp_keywords_matched", "note"]

with pd.ExcelWriter("output/enriched_LIVE_DEMO.xlsx", engine="openpyxl") as writer:
    df[display_cols].to_excel(writer, sheet_name="Companies", index=False)
    pd.DataFrame([
        {"metric": "Companies enriched (real, hand-researched demo)", "value": len(records)},
        {"metric": "Dataset bottoms-up est. total security spend (USD)", "value": tam_summary["dataset_bottoms_up_market_spend_usd"]},
        {"metric": "Dataset SAM (USD)", "value": tam_summary["dataset_sam_usd"]},
        {"metric": "Dataset SOM - next 12mo (USD)", "value": tam_summary["dataset_som_usd"]},
    ]).to_excel(writer, sheet_name="Summary", index=False)

print(df[display_cols].to_string(index=False))
print()
print("TAM summary:", tam_summary)
