"""
GTM Enrichment API — FastAPI wrapper around pipeline.py / scoring.py / tam.py.

Run locally:
    pip install -r requirements.txt
    uvicorn api:app --host 0.0.0.0 --port 8000

Then:
    GET  /health
    GET  /companies?limit=20        -> your real 185-company table (prepared)
    GET  /companies/{company}       -> lookup one row by name
    POST /enrich                    -> live-enrich one company {company, domain}
    POST /score                     -> score a raw signal record you already have
    GET  /tam/summary?limit=185     -> bottoms-up TAM/SAM/SOM over N companies
                                        (uses live enrichment - needs open internet)
    GET  /demo                      -> the 6 real, hand-verified companies from
                                        this conversation (works with NO internet -
                                        good for proving the API responds at all
                                        from inside a locked-down environment)

Interactive docs once running: http://localhost:8000/docs
"""
from __future__ import annotations
from typing import Optional

import pandas as pd
import yaml
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from pipeline import enrich_one, load_config
from scoring import score_company
from tam import estimate_company_tam, aggregate_dataset_tam
from demo_records import REAL_DEMO_RECORDS  # the 6 hand-verified companies

app = FastAPI(
    title="GTM Enrichment Engine API",
    description="Enriches event-attendee companies with public signals, "
                 "scores them Hot/Warm/Cold, and estimates TAM/SAM/SOM.",
    version="0.1.0",
)

CFG = load_config("config.yaml")
COMPANIES_DF = pd.read_csv("output/companies.csv")


class EnrichRequest(BaseModel):
    company: str
    domain: Optional[str] = None


class ScoreRequest(BaseModel):
    # any subset of the signal fields scoring.py understands
    website_text: Optional[str] = ""
    news_hits: Optional[list] = []
    is_public_company: Optional[bool] = False
    wikipedia_found: Optional[bool] = False
    employee_count: Optional[int] = None


@app.get("/health")
def health():
    return {"status": "ok", "companies_loaded": len(COMPANIES_DF)}


@app.get("/companies")
def list_companies(limit: int = 20):
    rows = COMPANIES_DF.head(limit).to_dict(orient="records")
    return {"count": len(rows), "companies": rows}


@app.get("/companies/{company}")
def get_company(company: str):
    match = COMPANIES_DF[COMPANIES_DF["company"].str.lower() == company.lower()]
    if match.empty:
        raise HTTPException(404, f"'{company}' not found in output/companies.csv")
    return match.iloc[0].to_dict()


@app.post("/enrich")
def enrich(req: EnrichRequest):
    """Live enrichment - requires this server to have real internet access
    (Wikipedia, SEC EDGAR, Google News, the company's own website). Will
    error out if run somewhere network-locked."""
    try:
        record = enrich_one(req.company, req.domain, CFG)
    except Exception as e:
        raise HTTPException(502, f"enrichment failed (needs outbound internet): {e}")
    record.pop("website_text", None)  # trim huge blob for the API response
    return record


@app.post("/score")
def score(req: ScoreRequest):
    record = req.dict()
    return score_company(record, CFG)


@app.get("/demo")
def demo():
    """No internet required - the 6 companies Claude hand-researched live
    via web search in this conversation, run through the real scoring/TAM
    code. Proves the API and its logic work end-to-end even when this
    process itself can't reach the open internet."""
    records = []
    for r in REAL_DEMO_RECORDS:
        rec = dict(r)
        rec["news_hit_count"] = len(rec["news_hits"])
        rec.update(score_company(rec, CFG))
        rec.update(estimate_company_tam(rec.get("employee_count"), CFG))
        rec.pop("website_text", None)
        rec.pop("news_hits", None)
        records.append(rec)
    return {"count": len(records), "companies": records,
            "tam_summary": aggregate_dataset_tam(records)}


@app.get("/tam/summary")
def tam_summary(limit: int = 185):
    """Live version over the real dataset - needs outbound internet."""
    df = COMPANIES_DF.head(limit)
    records = []
    for _, row in df.iterrows():
        try:
            rec = enrich_one(row["company"], row.get("domain"), CFG)
        except Exception:
            continue
        records.append(rec)
    if not records:
        raise HTTPException(502, "no companies could be enriched - check outbound internet access")
    return aggregate_dataset_tam(records)
