"""
LinkedIn has NO free public API for company firmographic data, and
scraping logged-out LinkedIn company pages is against their Terms of
Service, unreliable (heavy bot detection) and will get your IP
blocked. This module does NOT scrape LinkedIn.

What it does instead:
1. Constructs the *likely* LinkedIn company URL so a human (or a
   licensed data provider) can quickly look it up.
2. Defines the `LinkedInProvider` interface so you can drop in a real,
   compliant data source later without touching the rest of the
   pipeline. Good options, roughly cheapest -> most complete:
     - Manual: export a list from LinkedIn Sales Navigator yourself and
       join it in by domain/company name (see README).
     - Proxycurl, People Data Labs, Clearbit/HubSpot, Apollo.io,
       ZoomInfo - all paid, all have official APIs that are allowed to
       return LinkedIn-derived firmographic data.
     - LinkedIn's own Marketing Developer Platform APIs, if you can get
       approved as a partner (rarely feasible for a single company).

To wire one in: implement `enrich(company_name, domain) -> dict` below
and swap it in `pipeline.py`.
"""
from __future__ import annotations
import re


def guess_linkedin_url(company_name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", company_name.lower()).strip("-")
    return f"https://www.linkedin.com/company/{slug}/"


class LinkedInProvider:
    """Stub. Replace `enrich` with a call to a real, licensed API."""

    def enrich(self, company_name: str, domain: str | None) -> dict:
        return {
            "linkedin_url_guess": guess_linkedin_url(company_name),
            "employee_count": None,
            "industry": None,
            "note": "No LinkedIn API configured - see providers/linkedin.py",
        }
