"""Lead scoring: turns the raw enrichment signals for one company into a
single 0-100 score and a Hot/Warm/Cold tier, using the weights in
config.yaml.
"""
from __future__ import annotations


def score_company(record: dict, cfg: dict) -> dict:
    w = cfg["scoring_weights"]
    icp_keywords = [k.lower() for k in cfg["icp_keywords"]]

    score = 0.0
    breakdown = {}

    # 1. Recent cybersecurity-related news at all?
    news_hits = record.get("news_hits", [])
    if news_hits:
        score += w["recent_cyber_news"]
        breakdown["recent_cyber_news"] = w["recent_cyber_news"]

        vol_component = min(len(news_hits), 5) / 5 * w["news_volume"]
        score += vol_component
        breakdown["news_volume"] = round(vol_component, 1)
    else:
        breakdown["recent_cyber_news"] = 0
        breakdown["news_volume"] = 0

    # 2. Public company (SEC filer)
    if record.get("is_public_company"):
        score += w["is_public_company"]
        breakdown["is_public_company"] = w["is_public_company"]
    else:
        breakdown["is_public_company"] = 0

    # 3. ICP keyword matches on website/about text
    text = (record.get("website_text") or "").lower()
    matched = {kw for kw in icp_keywords if kw in text}
    record["icp_keywords_matched"] = sorted(matched)
    if icp_keywords:
        kw_component = len(matched) / len(icp_keywords) * w["icp_keyword_match"]
    else:
        kw_component = 0
    score += kw_component
    breakdown["icp_keyword_match"] = round(kw_component, 1)

    # 4. Wikipedia profile found (maturity/notability proxy)
    if record.get("wikipedia_found"):
        score += w["has_wikipedia_profile"]
        breakdown["has_wikipedia_profile"] = w["has_wikipedia_profile"]
    else:
        breakdown["has_wikipedia_profile"] = 0

    # 5. Employee count known from any source
    if record.get("employee_count"):
        score += w["employee_count_known"]
        breakdown["employee_count_known"] = w["employee_count_known"]
    else:
        breakdown["employee_count_known"] = 0

    score = round(min(score, 100), 1)

    tiers = cfg["scoring_tiers"]
    if score >= tiers["hot"]:
        tier = "Hot"
    elif score >= tiers["warm"]:
        tier = "Warm"
    else:
        tier = "Cold"

    return {"lead_score": score, "lead_tier": tier, "score_breakdown": breakdown}
