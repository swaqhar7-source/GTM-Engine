"""
SEC EDGAR full-text search - free, no key, but SEC requires a descriptive
User-Agent with contact info on every request (they will rate-limit or
block generic/blank ones). Only useful for US-listed / SEC-reporting
companies; most event attendees will simply have no hits, which is fine.
"""
from __future__ import annotations
import requests

# NOTE: replace this with your own name/email before running at any real
# volume - SEC actively blocks generic user agents.
HEADERS = {"User-Agent": "GTM Research contact@example.com"}
TIMEOUT = 10
SEARCH_URL = "https://efts.sec.gov/LATEST/search-index?q=%22{query}%22&forms=10-K,8-K"


def has_sec_filings(company_name: str) -> dict:
    """Returns {'is_public': bool, 'hit_count': int, 'sample_titles': [...]}"""
    url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company={requests.utils.quote(company_name)}&type=10-K&dateb=&owner=include&count=10&output=atom"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException:
        return {"is_public": False, "hit_count": 0, "sample_titles": []}

    text = resp.text
    hit_count = text.count("<entry>")
    return {"is_public": hit_count > 0, "hit_count": hit_count, "sample_titles": []}
