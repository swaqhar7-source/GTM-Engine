"""
Compiles the master GTM account-plan spreadsheet across all 185 companies:
  - Batch 1 (16 companies): full live-research plans (from the project doc)
  - Batch 2 (57 companies with a security-relevant title in their attendee
    list): live-researched company identity + tier/angle
  - Remainder (~112 companies): no security signal in attendee titles ->
    tiered "Cold"/"No Signal" honestly, not faked as researched

Output: output/gtm_master_plan.xlsx
"""
import pandas as pd

df_all = pd.read_csv("output/companies.csv")

# ---------------------------------------------------------------- BATCH 1
# the 16 companies already given full plans in the project doc
BATCH1 = {
    "Amazon": dict(tier="Warm", what_they_do="AWS/Amazon - NASDAQ:AMZN, ~1.55M employees, SEC filer.",
        signal="Heavy recent cybersecurity-investment news (AWS security bulletins, $50B gov AI infra, Anthropic security AI deal).",
        angle="Cyber risk quantification / vuln prioritization, practitioner-level pitch to Head of AppSec - not a whole-company deal.",
        flag="", research_depth="Web-researched"),
    "Herkey": dict(tier="Warm", what_they_do="India's largest career-engagement platform for women (ex-JobsForHer), 4.5M+ community.",
        signal="No cyber-specific news; large 8-person eng delegation signals org-wide AppSec interest.",
        angle="Identity & data-protection (DPDP Act) - candidate PII at scale; CTO is a real champion.",
        flag="", research_depth="Web-researched"),
    "EffiGo": dict(tier="Warm", what_they_do="B2B procurement-automation SaaS (PO management, supplier tooling).",
        signal="No cyber news; SaaS vendor selling to enterprises will hit vendor-security-questionnaire friction.",
        angle="GRC/compliance as sales-enablement ('close enterprise deals faster with SOC2 readiness'); CEO attended personally.",
        flag="", research_depth="Web-researched"),
    "ALLEN": dict(tier="Hot", what_they_do="India's largest exam-coaching/edtech brand (JEE/NEET), Bodhi Tree/Sofina-backed.",
        signal="Millions of students' PII + payments; named VP of IT & Cybersecurity attended.",
        angle="GRC/compliance + identity, direct to VP Cybersecurity - likely already budget-holder.",
        flag="", research_depth="Web-researched"),
    "AXA Global Business Services": dict(tier="Warm", what_they_do="AXA Group's India captive/GCC shared-services center, 30 years old.",
        signal="Insurance = regulated; captive centers often standardize compliance evidence centrally.",
        angle="Compliance-evidence automation for a captive - qualify: budget likely routes through global AXA procurement.",
        flag="", research_depth="Web-researched"),
    "Alfahive": dict(tier="Flag", what_they_do="Cyber-risk-quantification / AI-consulting vendor - sells directly to CISOs.",
        signal="Same category as a cyber-risk-quantification platform offering.",
        angle="Route to partnerships/BD, not direct sales - peer/competitor in this category.",
        flag="Competitor/peer overlap", research_depth="Web-researched"),
    "Mudrex Inc": dict(tier="Hot", what_they_do="Indian crypto exchange with a public Security & Compliance page (SOC2/ISO27001 context).",
        signal="Named CISO attended (Sandeep Belagavi).",
        angle="CISO-to-CISO: SOC-as-a-service / SIEM consolidation, framed as audit-ready evidence for exchange licensing.",
        flag="", research_depth="Web-researched"),
    "Ninjacart": dict(tier="Warm", what_they_do="B2B agri-tech supply-chain unicorn (farmer-to-retailer produce logistics).",
        signal="Entire delegation is DevOps/DevSecOps - no CISO; no cyber news found.",
        angle="Cloud-native/DevSecOps tooling (container/IaC/pipeline security), not GRC or SIEM.",
        flag="", research_depth="Web-researched"),
    "HCL Software": dict(tier="Warm", what_they_do="HCLTech's software product division; HCLTech itself also sells cybersecurity services.",
        signal="Named CISO (Pradeep M S) + 3 product-security engineers - securing HCL's OWN products.",
        angle="Product-security tooling pitch to the CISO directly ('secure your own product portfolio').",
        flag="Coopetition nuance - internal buyer, not their services arm", research_depth="Web-researched"),
    "InCred Financial Services": dict(tier="Warm", what_they_do="Fast-growing India NBFC (personal/education/business loans), tech-driven lender.",
        signal="RBI-regulated - mandatory cybersecurity framework compliance is non-optional.",
        angle="GRC/compliance (RBI framework) + cloud security; Head of Cloud Infra is the practical entry point.",
        flag="", research_depth="Web-researched"),
    "Pratt & Whitney": dict(tier="Warm", what_they_do="RTX/Raytheon aerospace-engine manufacturer; recent $100M+ MRO expansion.",
        signal="Attendees are software/PLM engineers, not named cyber titles - weaker direct signal than industry-level OT/ICS trend suggests.",
        angle="Enter via product-security/secure-SDLC for engineering software; ask who owns OT/ICS security separately.",
        flag="Lower confidence than initial industry-level read", research_depth="Web-researched"),
    "Reach": dict(tier="Warm", what_they_do="White-label mobile & connectivity platform for brands (MVNO-style telecom platform).",
        signal="Head of DevSecOps attended - real internal investment in the function already.",
        angle="Cloud security / identity (subscriber PII, fraud), pitched to Head of DevSecOps.",
        flag="", research_depth="Web-researched"),
    "Tatvacare": dict(tier="Hot", what_they_do="Indian digital-healthcare/EMR company, uses Azure OpenAI in its stack.",
        signal="Handles PHI; DPDP Act + healthcare sensitivity; AI-in-stack adds AI-governance angle.",
        angle="GRC/compliance (health-data protection) + cloud security, to Director of Engineering.",
        flag="", research_depth="Web-researched"),
    "Truvisor": dict(tier="Flag", what_they_do="Cybersecurity value-added distributor - exclusive Rapid7 distributor for ASEAN/India, partners with Vectra/Utimaco.",
        signal="All-commercial delegation (Sales Manager, no engineers) confirms distributor read.",
        angle="Channel/partnership conversation, not a sales target.",
        flag="Distributor - route to partnerships", research_depth="Web-researched"),
    "symplr": dict(tier="Hot", what_they_do="US healthcare operations/compliance software (credentialing, workforce compliance); recently HITRUST r2 certified.",
        signal="Senior AppSec Architect + Senior Cloud Architect attended - mature compliance program, real budget precedent.",
        angle="Continuous compliance / CSPM - 'reduce manual effort of maintaining HITRUST re-certification.'",
        flag="", research_depth="Web-researched"),
    "DP World": dict(tier="Hot", what_they_do="Global ports/logistics/supply-chain operator (70+ countries).",
        signal="Sole attendee is Global VP - Cyber Engineering/Architecture (IT/OT) - globally-scoped cyber exec at critical infra operator. (DP World Australia suffered a major port cyberattack in Nov 2023, well documented industry event.)",
        angle="Cyber-risk-quantification for IT/OT convergence risk, direct to this VP - single best lead in the dataset.",
        flag="Attendee count is only 1 - proves count is a weak priority proxy", research_depth="Web-researched"),
}

# ---------------------------------------------------------------- BATCH 2
# 57 companies with a security-relevant attendee title, now enriched with
# real web research on company identity (2026-09-22 search pass)
IDENTITY = {
    "aliceblue": "Discount stockbroking/trading platform in India (Alice Blue Financial Services).",
    "rakuten india": "India arm of Rakuten - Japanese e-commerce, fintech and telecom conglomerate.",
    "exotel": "Indian cloud telephony / CPaaS (communications platform) provider.",
    "unisys": "Global IT services company that ALSO sells its own cybersecurity/digital-workplace services.",
    "at&t": "Global telecom carrier - India unit likely GCC/engineering, not the telecom customer business.",
    "envoy global": "US corporate immigration-services company (visa/relocation management for enterprises).",
    "cumulocity": "Independent IoT platform (formerly part of Software AG, completed a management buyout).",
    "exeevo": "Life-sciences/pharma CRM software (recently acquired by Valsoft Corporation).",
    "olyv": "Olyv is the consumer brand of SmartCoin - an Indian micro-lending/fintech app.",
    "criticalog india pvt ltd": "Indian critical/time-sensitive logistics and supply-chain solutions provider.",
    "alten india pvt.ltd": "India arm of ALTEN Group - global engineering/R&D consulting.",
    "astera labs": "US semiconductor company - AI/connectivity chips (PCIe/CXL), NASDAQ-listed, high-growth.",
    "aurobindo pharma limited": "Major Indian pharmaceutical manufacturer (generics, API, formulations).",
    "cleartax": "Indian tax/e-invoicing fintech SaaS platform (now branding toward rulebound.ai), full-stack fintech.",
    "covalensedigital solutions": "IT services / digital engineering + IoT solutions provider.",
    "dmi finance private limited": "India NBFC / digital lender (fintech-driven lending).",
    "diageo": "Global spirits & beverages multinational (Johnnie Walker, Smirnoff, etc.) - India unit likely GCC/ops.",
    "essentra": "UK industrial components manufacturer (plastic/rubber components, filters).",
    "frontline fintech": "Ambiguous/generic name - identity not confidently confirmed via search; verify before outreach.",
    "apollo groups": "Ambiguous/generic name (could be several unrelated \"Apollo\" companies) - identity not confidently confirmed via search; verify before outreach. Attendee is a named CISO (Fahad Khan), so worth the 5-minute verification.",
    "jazzman": "Likely JazzX AI - US AI platform automating mortgage-lifecycle workflows.",
    "kanerika": "Data engineering, analytics and AI consulting firm (US/India).",
    "ramoji group": "Indian media/entertainment conglomerate (Ramoji Film City and related businesses).",
    "tata elxsi": "Tata Group's design/technology services arm (auto, media, healthcare, telecom engineering).",
    "zanmai labs pvt ltd": "Legal entity behind CoinDCX - one of India's largest crypto exchanges.",
    "jana bank (janalakshmi financial services)": "Jana Small Finance Bank - regulated Indian small finance bank (ex-microfinance).",
    "amadeus": "Global travel-technology / GDS (reservation systems) provider for airlines and travel.",
    "discover dollar": "AI-driven audit-recovery / overpayment-detection software for enterprises (Discover Dollar Technologies).",
    "meesho": "Major Indian social-commerce/e-commerce unicorn.",
    "abb": "Global industrial automation & robotics multinational.",
    "genpact": "Global professional services / BPO and IT services company.",
    "happiest minds technologies": "Indian IT services company (\"Born Digital, Born Agile\").",
    "happiest minds": "Indian IT services company (\"Born Digital, Born Agile\").",
    "indian air force": "Indian government defense/military branch - handle with standard B2B/B2G sales process, extra procurement scrutiny expected.",
    "korn ferry international": "Global HR/organizational and executive-search consulting firm.",
    "ltimindtree": "Major Indian IT services company (Larsen & Toubro / Mindtree merger).",
    "lumen technologies india pvt ltd": "US telecom/network infrastructure company - India unit likely GCC/engineering.",
    "propertyguru group": "Southeast Asia's leading online property marketplace (Singapore-listed).",
    "wells fargo": "Major US bank - India unit is a GCC/technology center, not the retail bank itself.",
    "wells fargo ": "Major US bank - India unit is a GCC/technology center, not the retail bank itself.",
    "greytip software pvt. ltd.": "Indian HR & payroll SaaS provider.",
    "chargebee": "Global subscription billing / revenue management SaaS platform.",
    "keka hr": "Indian HR & payroll SaaS platform.",
    "tredence": "Data analytics and AI consulting firm.",
    "cognizant technology solutions": "Global IT services and consulting major.",
    "ephicacy lifescience analytics": "Clinical/pharma data analytics and biometrics CRO.",
    "fis goobal": "Likely FIS Global (financial-services technology/payments company) - name appears misspelled in source data.",
    "honeywell technology solutions": "Honeywell's India technology/engineering center (industrial, aerospace, building tech).",
    "indecomm business services": "US mortgage-servicing BPO/automation provider.",
    "liminal": "Digital-asset custody & wallet-infrastructure security company for crypto institutions.",
    "marvell technology": "Major US semiconductor company (data infrastructure chips).",
    "nestle": "Global food & beverage multinational - India unit likely GCC/ops.",
    "shell": "Global energy major - India unit likely GCC/engineering/ops.",
    "toyota connected india": "Toyota's connected-car / mobility software arm.",
    "triveni turbine ltd": "Leading Indian industrial steam-turbine manufacturer.",
    "wd": "Western Digital - global data storage/semiconductor company.",
    "[24]7.ai": "AI-driven customer engagement / contact-center platform company.",
}

IDENTITY_BY_DOMAIN = {
    "epsilon.com": "Global marketing/adtech and data-driven customer experience company.",
    "happiestminds.com": "Indian IT services company (\"Born Digital, Born Agile\").",
    "media.net": "Global advertising-technology (ad exchange / contextual ads) company.",
    "gomoder.com": "Enterprise software/IT consulting firm (identity not fully confirmed - verify).",
    "payu.in": "Major India/global digital payments and fintech company (Prosus-owned).",
    "raksha.co.in": "Likely an Indian insurance/insurtech or security-named firm - identity not fully confirmed, verify before outreach.",
    "tesco.com": "UK grocery retail giant - India unit is a GCC/technology center.",
    "wdc.com": "Western Digital - global data storage & semiconductor company.",
    "blubirch.com": "Indian reverse-logistics / returns-management tech platform for e-commerce.",
    "brightmoney.co": "US/India personal-finance app (AI-driven debt payoff and financial planning).",
    "motorola.com": "Motorola Mobility (a Lenovo company) - consumer smartphones; India unit is R&D/engineering.",
    "nielsen.com": "Global media measurement and consumer/market research company.",
    "omegahms.com": "Healthcare revenue-cycle-management (RCM) BPO/technology company (recently acquired ApexonHealth, Vasta Global).",
    "propertyguru.tech": "Southeast Asia's leading online property marketplace (Singapore-listed) - tech/engineering arm.",
    "radisys.com": "Telecom/network infrastructure software and hardware company.",
    "se.com": "Schneider Electric - global energy management & industrial automation multinational.",
    "shadowfax.in": "Indian last-mile logistics/delivery platform for e-commerce and D2C.",
    "feelvaleo.com": "Digital health / wellness platform (identity not fully confirmed - verify).",
    "wwt.com": "World Wide Technology - major US IT solutions integrator/reseller.",
    "zoomcar.com": "Indian self-drive car-sharing/rental platform.",
    "22by7.in": "Indian cybersecurity & networking solutions VAR (Information Security practice).",
    "6dtech.co.in": "IT services/technology consulting firm (identity not fully confirmed - verify).",
    "acko.tech": "Indian digital-first insurance (insurtech) company.",
    "allianceproit.com": "IT reseller/solutions provider (identity not fully confirmed - verify).",
    "alliancroroit.com": "IT reseller/solutions provider (identity not fully confirmed - verify; note domain typo vs allianceproit.com).",
    "angelone.in": "Major Indian retail stockbroking/fintech platform (listed).",
    "in.bosch.com": "Bosch - global engineering/technology multinational; India unit is a large GCC/engineering center.",
    "bialairport.com": "Bangalore International Airport Limited - airport operator.",
    "bluspring.com": "Technology/consulting firm (identity not fully confirmed - verify).",
    "captainfresh.com": "B2B seafood/perishables marketplace and supply-chain platform.",
    "cumi.murugappa.com": "Carborundum Universal - Murugappa Group industrial abrasives/ceramics manufacturer.",
    "cisco.com": "Cisco - global networking, security, and collaboration technology giant (also a security vendor itself).",
    "cogostech.com": "Logistics-tech / freight-management platform.",
    "coupa.com": "Global business-spend-management (procurement/expense) SaaS platform.",
    "edubestu.com": "Ed-tech company (identity not fully confirmed - verify).",
    "entrust.com": "Entrust - global identity, PKI and digital-security vendor (itself a security vendor).",
    "fisglobal.com": "FIS Global - major financial-services technology and payments company.",
    "fsstech.com": "FSS (Financial Software and Systems) - Indian payments technology company.",
    "epifi.com": "Fi Money - Indian neobank/fintech app.",
    "fivetran.com": "Global data-integration/ELT SaaS platform.",
    "in.fcm.travel": "Flight Centre / FCM Travel - global corporate travel management company.",
    "greytip.com": "Indian HR & payroll SaaS provider.",
    "grexit.com": "Hiver - Gmail-based helpdesk/customer-service SaaS platform.",
    "ibm.com": "IBM - global enterprise technology, consulting and cybersecurity giant.",
    "ivalue.co.in": "iValue Infosolutions - major Indian cybersecurity value-added distributor (recently IPO'd), architecting India's cybersecurity stack.",
    "incred.com": "Fast-growing India NBFC (personal/education/business loans), tech-driven lender.",
    "quantumnblackai.in": "JPMorgan Chase & Co. - India unit tied to QuantumBlack/AI - large GCC/technology center.",
    "jumpcloud.com": "JumpCloud - cloud directory/identity-and-access-management (IAM) vendor (itself a security vendor).",
    "kipi.ai": "Data, analytics and AI consulting firm.",
    "kotak.com": "Kotak Mahindra Bank - major Indian private-sector bank.",
    "lemonpeak.com": "IT/software consulting firm (identity not fully confirmed - verify).",
    "liberalsecurity.com": "LiberalSecurity - Indian information-security, VAPT & GRC compliance services company (itself a security vendor).",
    "loginradius.com": "LoginRadius - customer identity and access management (CIAM) vendor (itself a security vendor).",
    "merckgroup.com": "Merck KGaA - global science & technology (pharma/life sciences/materials) multinational.",
    "micronel.net": "Engineering services firm (identity not fully confirmed - verify).",
    "nic.in": "National Informatics Centre - Indian government IT/e-governance body; standard public-sector sales process expected.",
    "people.inc": "HR-tech or staffing company (identity not fully confirmed - verify).",
    "pwc.com": "PwC - global professional-services and consulting firm.",
    "rahinfotech.com": "RAH Infotech - leading Indian IT & cybersecurity solutions distributor (partners with Utimaco, OPSWAT, others).",
    "techlogicconcepts.in": "A Samsung partner/reseller (\"S&S Tech Logic Concepts\") - identity not fully confirmed, verify.",
    "stfox.com": "Saint Fox Consulting - IT/technology consulting firm.",
    "scapia.cards": "Indian travel-focused fintech/credit-card startup.",
    "non.se.com": "Schneider Electric (domain typo of se.com) - global energy management & industrial automation multinational.",
    "tatvacare.in": "Indian digital-healthcare/EMR company, uses Azure OpenAI in its stack.",
    "technosport.in": "Sportswear/apparel manufacturer (identity not fully confirmed - verify).",
    "terraterri.com": "Sustainability/agri-tech or environmental company (identity not fully confirmed - verify).",
    "traya.health": "Indian D2C haircare/wellness brand.",
    "tredence.com": "Data analytics and AI consulting firm.",
    "truvisor.io": "Cybersecurity value-added distributor - exclusive Rapid7 distributor for ASEAN/India, partners with Vectra/Utimaco.",
    "tuta.io": "Tuta - German end-to-end encrypted email provider (itself a security/privacy vendor).",
    "viyuventures.co": "Venture/investment or consulting firm (identity not fully confirmed - verify).",
    "zohomail.in": "Company uses a Zoho-hosted email domain - underlying company identity not confirmed via domain alone.",
    "ysecit.com": "YSecIT Software - IT/software company; \"Yu-Pay\" suggests a payments product line.",
    "esecforte.com": "eSec Forte Technologies - CERT-In empanelled Indian cybersecurity services company (itself a security vendor).",
}

IDENTITY_BY_NAME = {
    "agilon health": "US value-based primary-care platform for healthcare providers.",
    "bhel": "Bharat Heavy Electricals Limited - major Indian state-owned power/heavy-engineering PSU.",
    "capgemini": "Global IT services and consulting major.",
    "checkmarx": "Checkmarx - application security testing (SAST/SCA) vendor (itself a direct AppSec competitor).",
    "concertai": "US healthcare/life-sciences AI and real-world-data company.",
    "ey": "EY (Ernst & Young) - global professional-services and consulting firm.",
    "everforth quinnox": "IT services/consulting firm (identity not fully confirmed - verify).",
    "encycdata": "Data/analytics company (identity not fully confirmed - verify).",
    "ibm india pvt ltd": "IBM - global enterprise technology, consulting and cybersecurity giant; India GCC/engineering unit.",
    "idfc first bank": "Major Indian private-sector bank.",
    "jpmorgan chase & co.": "Global investment bank and financial-services giant; India unit is a large GCC/technology center.",
    "jpmorganchase": "Global investment bank and financial-services giant; India unit is a large GCC/technology center.",
    "jiohotstar": "Merged Indian streaming platform (JioCinema + Disney+ Hotstar).",
    "lowes": "US home-improvement retail giant; India unit is a GCC/technology center.",
    "maersk": "Global shipping and logistics giant.",
    "mphasis": "Indian IT services and BPO company.",
    "samsung research": "Samsung's R&D/engineering center.",
    "scientific games india pvt ltd": "Global gaming/lottery technology company - India engineering unit.",
    "statestreet corporation": "Major US financial-services and asset-management/custody bank.",
    "esecforte": "eSec Forte Technologies - CERT-In empanelled Indian cybersecurity services company (itself a security vendor).",
    "ivalue infosolutions ltd": "iValue Infosolutions - major Indian cybersecurity value-added distributor (recently IPO'd).",
    "alfahive": "Cyber-risk-quantification / AI-consulting vendor - sells directly to CISOs (same company as \"Alfahive\" above, duplicate row from source data).",
}

MASHREQ_NOTE = "Major UAE-based bank (Mashreq Bank) - India unit likely a GCC/technology center."
IDENTITY_BY_DOMAIN["mashreq.com"] = MASHREQ_NOTE

TIER_NOTES = {
    "unisys": "Coopetition nuance - Unisys sells its own security services; these are likely internal buyers.",
    "at&t": "Verify whether India delegation has local buying authority (likely a GCC, not the carrier business).",
    "liminal": "Peer/competitor in the crypto-custody-security category - flag for partnerships review.",
    "wells fargo": "Regulated bank GCC - long enterprise procurement cycle likely.",
    "wells fargo ": "Regulated bank GCC - long enterprise procurement cycle likely.",
    "indian air force": "Government/defense - route through appropriate public-sector sales process.",
    "frontline fintech": "Company identity not confidently confirmed - verify before investing outreach effort.",
    "apollo groups": "Company identity not confidently confirmed - verify before investing outreach effort.",
    "esecforte": "CERT-In empanelled cybersecurity services company - peer/competitor overlap, route to partnerships.",
    "ivalue infosolutions ltd": "Major cybersecurity value-added distributor - channel/partnership conversation, not a sales target.",
    "alfahive": "Same company as \"Alfahive\" (duplicate row, different casing) - cyber-risk-quantification vendor, peer/competitor.",
}
FORCE_FLAG_NAMES = {"esecforte", "ivalue infosolutions ltd", "alfahive"}

# domain-keyed flags for companies discovered to be security vendors/VARs/
# distributors while researching the "unresearched" long tail - same
# treatment as Alfahive/Truvisor/Liminal: route to partnerships, not sales.
COMPETITOR_OR_CHANNEL_DOMAINS = {
    "22by7.in": "Cybersecurity/networking VAR - channel conversation, not a sales target.",
    "ivalue.co.in": "Major cybersecurity value-added distributor - channel/partnership conversation, not a sales target.",
    "rahinfotech.com": "Cybersecurity solutions distributor - channel/partnership conversation, not a sales target.",
    "liberalsecurity.com": "Information-security/GRC services vendor - peer/competitor overlap, route to partnerships.",
    "tuta.io": "Encrypted-email/privacy vendor - adjacent security vendor, low sales-target priority.",
    "entrust.com": "Identity/PKI security vendor - peer/competitor overlap, route to partnerships.",
    "jumpcloud.com": "Cloud IAM vendor - peer/competitor overlap in identity, route to partnerships.",
    "loginradius.com": "CIAM vendor - peer/competitor overlap in identity, route to partnerships.",
    "cisco.com": "Cisco sells its own security portfolio - likely internal buyer, but verify which team attended before treating as a standard target.",
    "esecforte.com": "CERT-In empanelled cybersecurity services company - peer/competitor overlap, route to partnerships.",
}

SEC_KEYWORDS_HOT = {"ciso", "dpo"}
SEC_KEYWORDS_WARM = {"cyber", "cyber security", "cybersecurity", "security", "infosec",
                      "information security", "compliance", "risk", "vulnerability",
                      "appsec", "application security", "red team", "iam", "identity"}
SEC_KEYWORDS_COLD = {"devsecops", "secops", "soc analyst"}


def signal_score_and_keywords(attendees):
    if not isinstance(attendees, str):
        return 0, []
    text = attendees.lower()
    all_kw = SEC_KEYWORDS_HOT | SEC_KEYWORDS_WARM | SEC_KEYWORDS_COLD
    hits = [k for k in all_kw if k in text]
    score = len(set(hits))
    if any(k in hits for k in SEC_KEYWORDS_HOT):
        score += 3
    return score, hits


def tier_from_keywords(keywords):
    kwset = set(keywords)
    if kwset & SEC_KEYWORDS_HOT:
        return "Hot"
    if kwset & SEC_KEYWORDS_WARM:
        return "Warm"
    if kwset & SEC_KEYWORDS_COLD:
        return "Cold"
    return "No Signal"


def angle_from_keywords(keywords, tier):
    kwset = set(keywords)
    if "ciso" in kwset or "dpo" in kwset:
        return "GRC/compliance or SIEM/SOC - direct to named security/privacy leader."
    if "iam" in kwset or "identity" in kwset:
        return "Identity & access management."
    if "appsec" in kwset or "application security" in kwset or "red team" in kwset:
        return "AppSec / vulnerability management, cyber risk quantification."
    if "compliance" in kwset or "risk" in kwset:
        return "GRC/compliance."
    if kwset & SEC_KEYWORDS_COLD:
        return "Cloud security / DevSecOps tooling (CSPM, container/IaC security)."
    if tier == "No Signal":
        return "No security signal in attendee titles - needs individual research before an angle can be set."
    return "General cybersecurity platform conversation - qualify further."


rows = []
for _, r in df_all.iterrows():
    name = r["company"]
    key = name.strip().lower()
    domain = r["domain"] if pd.notna(r["domain"]) else None
    row = {
        "company": name,
        "domain": domain,
        "attendee_count": int(r["attendee_count"]),
        "attendees": r["attendees"],
    }

    if name in BATCH1:
        b = BATCH1[name]
        row.update({
            "tier": b["tier"],
            "what_they_do": b["what_they_do"],
            "signal": b["signal"],
            "recommended_angle": b["angle"],
            "flag": b["flag"],
            "research_depth": b["research_depth"],
            "batch": 1,
        })
    else:
        score, keywords = signal_score_and_keywords(r["attendees"])
        tier = tier_from_keywords(keywords)

        identity = None
        if domain and domain in IDENTITY_BY_DOMAIN:
            identity = IDENTITY_BY_DOMAIN[domain]
        elif key in IDENTITY:
            identity = IDENTITY[key]
        elif key in IDENTITY_BY_NAME:
            identity = IDENTITY_BY_NAME[key]

        chan_flag = COMPETITOR_OR_CHANNEL_DOMAINS.get(domain, "") if domain else ""
        name_flag = TIER_NOTES.get(key, "")
        force_flag = key in FORCE_FLAG_NAMES
        flag = chan_flag or name_flag
        # a confirmed competitor/channel overrides the keyword-based tier -
        # these are routing decisions, not lead-quality scores
        effective_tier = "Flag" if (chan_flag or force_flag) else tier

        if identity is not None:
            row.update({
                "tier": effective_tier,
                "what_they_do": identity,
                "signal": ("Security-relevant title(s) in attendee list: " + ", ".join(sorted(set(keywords)))) if keywords else "",
                "recommended_angle": ("Channel/partnership conversation - not a direct sales target." if (chan_flag or force_flag) else angle_from_keywords(keywords, effective_tier)),
                "flag": flag,
                "research_depth": "Web-researched",
                "batch": 2,
            })
        else:
            row.update({
                "tier": tier,
                "what_they_do": "",
                "signal": ("Security-relevant title(s) in attendee list: " + ", ".join(sorted(set(keywords)))) if keywords else "No security-relevant title in attendee list.",
                "recommended_angle": angle_from_keywords(keywords, tier),
                "flag": name_flag,
                "research_depth": "Attendee-signal only - not individually web-researched yet",
                "batch": 3 if tier != "No Signal" else 0,
            })
    rows.append(row)

out = pd.DataFrame(rows)

tier_order = {"Hot": 0, "Warm": 1, "Cold": 2, "Flag": 3, "No Signal": 4}
out["_tier_sort"] = out["tier"].map(tier_order).fillna(5)
out = out.sort_values(["_tier_sort", "attendee_count"], ascending=[True, False]).drop(columns="_tier_sort")

cols = ["tier", "company", "domain", "attendee_count", "what_they_do", "signal",
        "recommended_angle", "flag", "attendees", "research_depth", "batch"]
out = out[cols]

with pd.ExcelWriter("output/gtm_master_plan.xlsx", engine="openpyxl") as writer:
    out.to_excel(writer, sheet_name="All Companies", index=False)
    out[out["tier"] == "Hot"].to_excel(writer, sheet_name="Hot", index=False)
    out[out["tier"] == "Warm"].to_excel(writer, sheet_name="Warm", index=False)
    out[out["tier"] == "Flag"].to_excel(writer, sheet_name="Flag (not standard sales)", index=False)
    out[out["tier"] == "No Signal"].to_excel(writer, sheet_name="Needs research", index=False)

    summary = out["tier"].value_counts().reindex(["Hot", "Warm", "Cold", "Flag", "No Signal"]).fillna(0).astype(int)
    summary_df = summary.reset_index()
    summary_df.columns = ["tier", "count"]
    summary_df.to_excel(writer, sheet_name="Summary", index=False)

print(out["tier"].value_counts())
print()
print("Total companies:", len(out))
out.to_json("output/gtm_master_plan.json", orient="records", indent=1)
EOF_MARKER = True
