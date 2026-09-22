"""
Offline validation for automate.py, following the same pattern as
test_dry_run.py: mock every provider function with plausible fake data so
the whole pipeline (parsing -> tiering -> enrichment -> TAM -> Excel ->
dashboard HTML) can be proven correct inside this sandbox, which has no
outbound internet to the real providers.

Run against the REAL 185-company AppSec Live dataset so column-handling
edge cases (swapped Designation/Email, missing domains, etc.) are exercised
with real data, not synthetic rows.
"""
import sys
from unittest.mock import patch

# Point this at your own raw attendee export to re-run the dry test on
# your machine - the path below was only valid inside the original
# Claude session that built this package.
RAW_XLSX = "AppSec_Live_2026.xlsx"


def fake_fetch_homepage_text(domain):
    if "esecforte" in domain or "22by7" in domain:
        return {
            "domain": domain,
            "title": "Managed Security Services",
            "meta_description": "Leading value added distributor of cybersecurity services and MSSP solutions.",
            "about_url": None,
            "text": "We are a managed security services provider offering SIEM platform and VAPT.",
        }
    return {
        "domain": domain,
        "title": "Example Corp - Home",
        "meta_description": f"Example Corp ({domain}) builds software products for its industry.",
        "about_url": None,
        "text": "Example Corp builds software products for its industry. Founded in 2010.",
    }


def fake_fetch_summary(company_name):
    return {"found": True, "title": company_name, "extract": f"{company_name} is a company with about 500 employees.", "url": None}


def fake_guess_employee_count(extract_text):
    import re
    m = re.search(r"([\d,]+)\s*employees", extract_text or "")
    return int(m.group(1).replace(",", "")) if m else None


def fake_has_sec_filings(company_name):
    return {"is_public": company_name.lower() in {"amazon", "ibm india pvt ltd"}, "hit_count": 0, "sample_titles": []}


def fake_search_news(company_name, suffixes, lookback_days):
    return [{"title": f"{company_name} announces new SOC 2 certification", "link": "https://example.com/news", "pub_date": None, "query": "SOC 2"}]


def main():
    with patch("automate.website_provider.fetch_homepage_text", side_effect=fake_fetch_homepage_text), \
         patch("automate.wikipedia_provider.fetch_summary", side_effect=fake_fetch_summary), \
         patch("automate.wikipedia_provider.guess_employee_count", side_effect=fake_guess_employee_count), \
         patch("automate.sec_provider.has_sec_filings", side_effect=fake_has_sec_filings), \
         patch("automate.news_provider.search_news", side_effect=fake_search_news):
        import automate
        automate.run(
            input_path=RAW_XLSX,
            out_dir="output/dry_run_automate",
            config_path=None,
            limit=None,
            sleep_seconds=0,
        )
    print("\nDRY RUN OK - full pipeline (parse -> tier -> mock-enrich -> TAM -> Excel -> dashboard) ran end-to-end with no exceptions.")


if __name__ == "__main__":
    sys.exit(main())
