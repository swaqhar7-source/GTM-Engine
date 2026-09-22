"""The 6 real, hand-researched companies used in demo_live.py and api.py's
/demo endpoint. Sourced from live web search on 2026-09-22 - see notes per
record for citations. Not randomly generated.
"""

REAL_DEMO_RECORDS = [
    {
        "company": "Herkey",
        "domain": "herkey.com",
        "attendee_count": 8,
        "website_text": (
            "HerKey formerly JobsForHer India's largest career engagement "
            "platform for women 4.5 million plus community jobs returnships "
            "upskilling recruitment hr tech platform"
        ),
        "wikipedia_found": False,
        "employee_count": None,
        "is_public_company": False,
        "news_hits": [],
        "note": "HR-tech / careers platform for women, not itself a security vendor. "
                "Source: herkey.com/about-us, LinkedIn, Crunchbase listing.",
    },
    {
        "company": "EffiGo",
        "domain": "effigoglobal.com",
        "attendee_count": 7,
        "website_text": (
            "EffiGO trusted procurement partner with technology automating "
            "purchasing for enterprise businesses purchase order management "
            "supplier relationship saas platform"
        ),
        "wikipedia_found": False,
        "employee_count": None,
        "is_public_company": False,
        "news_hits": [],
        "note": "B2B procurement-automation SaaS. No cybersecurity-specific news found. "
                "Source: effigoglobal.com, Tracxn/PitchBook/ZoomInfo listings.",
    },
    {
        "company": "Alfahive",
        "domain": "alfahive.com",
        "attendee_count": 5,
        "website_text": (
            "Alfahive automating cyber risk quantification AI consulting "
            "cyber risk management CISOs cyber risk automation third party "
            "cyber risk assessment"
        ),
        "wikipedia_found": False,
        "employee_count": None,
        "is_public_company": False,
        "news_hits": [],
        "note": "IMPORTANT: Alfahive is itself a cyber-risk-quantification vendor - "
                "a peer/potential-competitor in the security space, not a typical "
                "buyer. Flag for manual review before treating as a sales target. "
                "Source: alfahive.com product/use-case pages, Tracxn.",
    },
    {
        "company": "Ninjacart",
        "domain": "ninjacart.com",
        "attendee_count": 5,
        "website_text": (
            "Ninjacart b2b agri-tech supply chain fresh produce farmers "
            "retailers logistics technology platform"
        ),
        "wikipedia_found": False,
        "employee_count": None,
        "is_public_company": False,
        "news_hits": [],
        "note": "Agri-tech supply chain unicorn. No cybersecurity-specific news "
                "surfaced in this search pass - does not mean no interest, "
                "just no public signal found today.",
    },
    {
        "company": "Mudrex Inc",
        "domain": "mudrex.com",
        "attendee_count": 5,
        "website_text": (
            "Mudrex crypto exchange India security compliance SOC2 ISO 27001 "
            "safest crypto exchange trade bitcoin compliance page"
        ),
        "wikipedia_found": False,
        "employee_count": None,
        "is_public_company": False,
        "news_hits": [
            {"title": "Ensuring Security and Compliance on Mudrex in 2025", "link": "https://mudrex.com/learn/security-and-compliance-on-mudrex/", "pub_date": None, "query": "security compliance"},
        ],
        "note": "Crypto exchange with a dedicated public Compliance page discussing "
                "SOC 2 / ISO 27001 - a genuine, if soft, security-investment signal "
                "typical of regulated fintech/crypto. Source: mudrex.com/compliance.",
    },
    {
        "company": "Amazon",
        "domain": "amazon.com",
        "attendee_count": 6,
        "website_text": (
            "Amazon Web Services AWS security bulletins cloud saas zero trust "
            "compliance identity endpoint incident response managed security "
            "devsecops platform enterprise"
        ),
        "wikipedia_found": True,
        "employee_count": 1550000,
        "is_public_company": True,
        "news_hits": [
            {"title": "Amazon (AMZN) Partners in Expanding Cybersecurity Initiative", "link": "https://www.gurufocus.com/news/8921094", "pub_date": None, "query": "security partnership"},
            {"title": "Amazon (AMZN) Embraces New Cybersecurity Standards for Defense Contractors", "link": "https://www.gurufocus.com/news/8839878", "pub_date": None, "query": "compliance certification"},
            {"title": "Amazon to invest up to $50 billion to expand AI and supercomputing infrastructure for US government agencies", "link": "https://www.aboutamazon.com/news/company-news/amazon-ai-investment-us-federal-agencies", "pub_date": None, "query": "cybersecurity investment"},
            {"title": "Anthropic Secures $5B From Amazon While NSA Quietly Uses Its Restricted Cybersecurity AI", "link": "https://theaiinsider.tech/2026/04/21/", "pub_date": None, "query": "cybersecurity investment"},
        ],
        "note": "NASDAQ: AMZN, SEC filer, ~1.55M employees globally (real published "
                "figure, not a Wikipedia scrape). Very strong, very recent "
                "cybersecurity-investment news volume. In practice AWS/Amazon is "
                "an outlier account - qualify by BU/region before treating the "
                "whole company as one TAM line item. Sources: GuruFocus, "
                "aboutamazon.com, theaiinsider.tech (all live web search, 2026-09-22).",
    },
]

