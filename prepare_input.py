"""
Turns a raw event attendee export (one row per person: Company, Name,
Designation, Email, Contact Number - the AppSec Live format) into one
row per COMPANY, with:
  - a best-guess company domain (from attendee email addresses)
  - the list of attendees + their designations (this is your warm-intro
    signal - you already have names of security leaders at each account)
  - an attendee_count (bigger delegations = bigger event investment =
    often a soft signal of a bigger/more engaged security org)

Usage:
    python prepare_input.py attendees.xlsx companies.csv
"""
from __future__ import annotations
import sys
import re
from collections import defaultdict, Counter
import pandas as pd

FREE_EMAIL_DOMAINS = {
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com",
    "protonmail.com", "rediffmail.com", "yahoo.co.in", "live.com", "aol.com",
}


def domain_from_email(email: str) -> str | None:
    if not isinstance(email, str) or "@" not in email:
        return None
    domain = email.split("@")[-1].strip().lower()
    return domain or None


def _fix_swapped_email_designation(designation, email):
    """This particular export has the Designation/Email columns swapped
    on most rows (whichever field actually contains '@' is the real
    email, regardless of which header it sits under). Detect per-row
    rather than trusting the header."""
    des_str = str(designation) if pd.notna(designation) else ""
    email_str = str(email) if pd.notna(email) else ""
    des_is_email = "@" in des_str
    email_is_email = "@" in email_str
    if email_is_email and not des_is_email:
        return des_str or None, email_str  # already correct
    if des_is_email and not email_is_email:
        return email_str or None, des_str  # swapped -> fix
    if des_is_email and email_is_email:
        # both look like emails (shouldn't happen) - keep as labeled
        return des_str, email_str
    return (des_str or None), None  # neither is an email


def build_company_table(raw_path: str) -> pd.DataFrame:
    df = pd.read_excel(raw_path) if raw_path.lower().endswith((".xlsx", ".xls")) else pd.read_csv(raw_path)
    df = df[["Company", "Name", "Designation", "Email", "Contact Number"]].copy()
    df = df.dropna(subset=["Company"])
    df["Company"] = df["Company"].astype(str).str.strip()
    df = df[df["Company"] != ""]

    grouped = defaultdict(lambda: {"attendees": [], "domains": Counter()})
    for _, row in df.iterrows():
        company = row["Company"]
        name = row.get("Name")
        designation, email = _fix_swapped_email_designation(
            row.get("Designation"), row.get("Email")
        )
        entry = grouped[company]
        entry["attendees"].append(
            f"{name} ({designation})" if designation else str(name)
        )
        dom = domain_from_email(email)
        if dom and dom not in FREE_EMAIL_DOMAINS:
            entry["domains"][dom] += 1

    out_rows = []
    for company, data in grouped.items():
        best_domain = data["domains"].most_common(1)[0][0] if data["domains"] else None
        out_rows.append({
            "company": company,
            "domain": best_domain,
            "domain_source": "attendee_email" if best_domain else "not_found",
            "attendee_count": len(data["attendees"]),
            "attendees": "; ".join(data["attendees"]),
        })

    out_df = pd.DataFrame(out_rows).sort_values(
        ["attendee_count", "company"], ascending=[False, True]
    )
    return out_df.reset_index(drop=True)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python prepare_input.py <raw_attendees.xlsx> <companies_out.csv>")
        sys.exit(1)
    table = build_company_table(sys.argv[1])
    table.to_csv(sys.argv[2], index=False)
    print(f"Wrote {len(table)} unique companies to {sys.argv[2]}")
    print(f"  - domain found via attendee email: {(table['domain_source']=='attendee_email').sum()}")
    print(f"  - domain NOT found (personal email only): {(table['domain_source']=='not_found').sum()}")
