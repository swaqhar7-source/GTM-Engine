"""
Google News RSS - free, no key, no auth. This is the "what is this
company doing / spending on in cybersecurity lately" signal.

RSS format is simple XML; we parse it with the standard library so we
don't need an extra 'feedparser' dependency.
"""
from __future__ import annotations
import datetime as dt
import xml.etree.ElementTree as ET
import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; GTMResearchBot/1.0)"}
TIMEOUT = 10
RSS_URL = "https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"


def search_news(company_name: str, suffixes: list[str], lookback_days: int) -> list[dict]:
    """Runs one query per suffix (e.g. '<Company> cybersecurity investment')
    and returns a de-duplicated list of {'title','link','pub_date','query'}
    for articles inside the lookback window."""
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=lookback_days)
    seen_links = set()
    results = []

    for suffix in suffixes:
        query = requests.utils.quote(f'"{company_name}" {suffix}')
        url = RSS_URL.format(query=query)
        try:
            resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            resp.raise_for_status()
        except requests.RequestException:
            continue

        try:
            root = ET.fromstring(resp.content)
        except ET.ParseError:
            continue

        for item in root.findall(".//item"):
            link = (item.findtext("link") or "").strip()
            if not link or link in seen_links:
                continue
            title = (item.findtext("title") or "").strip()
            pub_date_raw = item.findtext("pubDate")
            pub_date = None
            if pub_date_raw:
                try:
                    pub_date = dt.datetime.strptime(
                        pub_date_raw, "%a, %d %b %Y %H:%M:%S %Z"
                    ).replace(tzinfo=dt.timezone.utc)
                except ValueError:
                    pub_date = None
            if pub_date and pub_date < cutoff:
                continue
            seen_links.add(link)
            results.append({
                "title": title,
                "link": link,
                "pub_date": pub_date.isoformat() if pub_date else None,
                "query": suffix,
            })
    return results
