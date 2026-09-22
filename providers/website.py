"""
Scrapes a company's own public website (homepage + an 'about' page if one
is linked) for a text blob we can run keyword matching against.

No API key needed. Respects robots.txt is NOT implemented here for
simplicity - if you plan to run this at real scale, add a robots.txt
check and a rate limiter, and consider caching results.
"""
from __future__ import annotations
import requests
from bs4 import BeautifulSoup
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; GTMResearchBot/1.0; "
                  "+https://example.com/bot-info)"
}
TIMEOUT = 10


def _clean_text(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    text = soup.get_text(separator=" ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def fetch_homepage_text(domain: str) -> dict:
    """Returns {'title', 'meta_description', 'text', 'about_url'} or
    an 'error' key if the site could not be reached."""
    url = f"https://{domain}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        resp.raise_for_status()
    except requests.RequestException as e:
        return {"error": str(e), "domain": domain}

    soup = BeautifulSoup(resp.text, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    meta = soup.find("meta", attrs={"name": "description"})
    meta_description = meta["content"].strip() if meta and meta.get("content") else ""

    # try to find an About/Company link for a bit more text
    about_url = None
    for a in soup.find_all("a", href=True):
        label = (a.get_text() or "").strip().lower()
        if label in ("about", "about us", "company", "who we are"):
            href = a["href"]
            about_url = href if href.startswith("http") else url.rstrip("/") + "/" + href.lstrip("/")
            break

    text = _clean_text(soup)

    if about_url:
        try:
            about_resp = requests.get(about_url, headers=HEADERS, timeout=TIMEOUT)
            about_resp.raise_for_status()
            about_soup = BeautifulSoup(about_resp.text, "html.parser")
            text += " " + _clean_text(about_soup)
        except requests.RequestException:
            pass  # homepage text alone is fine

    return {
        "domain": domain,
        "title": title,
        "meta_description": meta_description,
        "about_url": about_url,
        "text": text[:20000],  # cap size
    }


def guess_domain(company_name: str) -> str:
    """Very rough fallback if no domain column is supplied. Strips
    common suffixes and lowercases. This is a last resort - a real
    domain column, or a paid enrichment provider, will be far more
    reliable."""
    name = re.sub(r"[,.]", "", company_name.lower())
    for suffix in [" inc", " llc", " ltd", " corp", " corporation",
                   " co", " company", " group", " holdings"]:
        if name.endswith(suffix):
            name = name[: -len(suffix)]
    name = re.sub(r"[^a-z0-9]", "", name)
    return f"{name}.com"
