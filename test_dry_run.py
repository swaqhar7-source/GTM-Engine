"""Offline dry-run: mocks every network call with plausible fake data so
we can prove the scoring/TAM/Excel-writing logic works end-to-end even
in a network-restricted sandbox. Not part of the shipped pipeline -
delete or ignore this file; it's just for local validation.
"""
import random
from unittest.mock import patch
import pipeline

random.seed(42)

FAKE_WIKI_HITS = {"Amazon", "HCL Software", "Pratt & Whitney"}


def fake_fetch_homepage_text(domain):
    return {
        "domain": domain,
        "title": f"{domain} - Home",
        "meta_description": "We are a cloud SaaS company focused on zero trust and compliance.",
        "about_url": None,
        "text": "cloud saas zero trust compliance soc devsecops platform " * 3,
    }


def fake_fetch_summary(company_name):
    if company_name in FAKE_WIKI_HITS:
        return {"found": True, "title": company_name,
                "extract": f"{company_name} is a large company with 12,000 employees.",
                "url": f"https://en.wikipedia.org/wiki/{company_name}"}
    return {"found": False}


def fake_has_sec_filings(company_name):
    return {"is_public": company_name in FAKE_WIKI_HITS, "hit_count": 1 if company_name in FAKE_WIKI_HITS else 0, "sample_titles": []}


def fake_search_news(company_name, suffixes, lookback_days):
    n = random.choice([0, 0, 1, 2, 3])
    return [{"title": f"{company_name} news {i}", "link": "https://example.com", "pub_date": None, "query": suffixes[0]} for i in range(n)]


with patch("providers.website.fetch_homepage_text", fake_fetch_homepage_text), \
     patch("providers.wikipedia.fetch_summary", fake_fetch_summary), \
     patch("providers.sec_edgar.has_sec_filings", fake_has_sec_filings), \
     patch("providers.news.search_news", fake_search_news):
    pipeline.run("output/companies.csv", "output/enriched_DRYRUN.xlsx", "config.yaml", limit=15, sleep_seconds=0)

print("Dry run complete.")
