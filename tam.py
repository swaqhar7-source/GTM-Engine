"""
Bottom-up TAM/SAM/SOM for the companies actually in your uploaded
dataset (e.g. one event's attendee list). This is NOT the total market
size for your category worldwide - it's "how big is the opportunity
sitting inside the accounts we already have a foot in the door with."

To get a true top-down TAM (whole category, whole world/region), pull a
published market-size figure for your product category (Gartner, IDC,
a VC market map, etc.) and treat the number this module produces as a
sanity check / bottoms-up cross-reference against it, not a replacement.
"""
from __future__ import annotations


def _size_bucket(employee_count: int | None, cfg: dict) -> tuple[str, dict]:
    buckets = cfg["size_buckets"]
    n = employee_count or cfg["default_employee_count_if_unknown"]
    for name, b in buckets.items():
        if b["max_employees"] is None or n <= b["max_employees"]:
            return name, b
    # fallback to the largest bucket
    last_name = list(buckets.keys())[-1]
    return last_name, buckets[last_name]


def estimate_company_tam(employee_count: int | None, cfg: dict) -> dict:
    bucket_name, bucket = _size_bucket(employee_count, cfg)
    n = employee_count or cfg["default_employee_count_if_unknown"]
    est_total_security_spend = n * bucket["annual_security_spend_per_employee_usd"]
    sam = est_total_security_spend * cfg["serviceable_addressable_fraction"]
    som = sam * cfg["serviceable_obtainable_fraction"]
    return {
        "size_bucket": bucket_name,
        "employee_count_used": n,
        "employee_count_was_estimated": employee_count is None,
        "est_total_security_spend_usd": round(est_total_security_spend),
        "est_sam_usd": round(sam),
        "est_som_usd": round(som),
    }


def aggregate_dataset_tam(records: list[dict]) -> dict:
    total_spend = sum(r.get("est_total_security_spend_usd", 0) for r in records)
    total_sam = sum(r.get("est_sam_usd", 0) for r in records)
    total_som = sum(r.get("est_som_usd", 0) for r in records)
    by_bucket = {}
    for r in records:
        b = r.get("size_bucket", "unknown")
        by_bucket.setdefault(b, {"companies": 0, "sam_usd": 0})
        by_bucket[b]["companies"] += 1
        by_bucket[b]["sam_usd"] += r.get("est_sam_usd", 0)

    return {
        "dataset_bottoms_up_market_spend_usd": total_spend,
        "dataset_sam_usd": total_sam,
        "dataset_som_usd": total_som,
        "by_size_bucket": by_bucket,
        "company_count": len(records),
    }
