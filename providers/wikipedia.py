"""
Wikipedia REST API - free, no key, generous rate limits.
Used as a rough proxy for "is this a notable/established company" and,
when available, a stated employee count from the infobox summary text.
"""
from __future__ import annotations
import re
import requests

HEADERS = {"User-Agent": "GTMResearchBot/1.0 (contact: research@example.com)"}
TIMEOUT = 10


def fetch_summary(company_name: str) -> dict:
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(company_name)}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if resp.status_code != 200:
            return {"found": False}
        data = resp.json()
        if data.get("type") == "disambiguation":
            return {"found": False, "disambiguation": True}
        return {
            "found": True,
            "title": data.get("title"),
            "extract": data.get("extract", ""),
            "url": data.get("content_urls", {}).get("desktop", {}).get("page"),
        }
    except requests.RequestException:
        return {"found": False}


EMPLOYEE_RE = re.compile(
    r"([\d,]{2,9})\s*(?:employees|staff|people)", re.IGNORECASE
)


def guess_employee_count(extract_text: str) -> int | None:
    """Very rough - looks for a number followed by 'employees' in the
    Wikipedia summary text. Returns None if nothing found."""
    m = EMPLOYEE_RE.search(extract_text or "")
    if not m:
        return None
    try:
        return int(m.group(1).replace(",", ""))
    except ValueError:
        return None
