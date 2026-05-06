"""Hot-prospect scoring + .com domain availability via RDAP.

Score breakdown (max 100):
  Recency   0–40  (< 7 days  = 40 | 7–30 = 28 | 30–90 = 12 | > 90 = 0)
  Sector    0–30  (top-tier sectors = 30 | other monetisable = 18 | "other" = 0)
  Domain    0–30  (.com available = 30 | taken = 0 | unknown = 0)
"""
import datetime as dt
import logging
import re
import time

import requests

from ..config import settings

logger = logging.getLogger(__name__)

# Sectors that command the highest prospect value
_TOP_SECTORS = {
    "fintech",
    "artificial_intelligence",
    "cybersecurity",
    "digital_health_biotech",
    "saas_cloud_infra",
}

_BUSINESS_SUFFIXES = re.compile(
    r"\b(llc|l\.l\.c|inc|incorporated|corp|corporation|ltd|limited|co|company|"
    r"group|holdings?|services?|solutions?|technologies?|systems?|consulting|"
    r"partners?|associates?|ventures?|enterprises?)\b",
    re.IGNORECASE,
)


def extract_domain_candidate(business_name: str) -> str | None:
    """Return a clean alphanumeric string suitable as a .com domain, or None."""
    cleaned = _BUSINESS_SUFFIXES.sub("", business_name)
    cleaned = re.sub(r"[^a-z0-9-]", "", cleaned.lower().replace(" ", ""))
    cleaned = cleaned.strip("-")
    if 3 <= len(cleaned) <= 20:
        return cleaned
    return None


def check_domain_available(domain_candidate: str, tld: str = "com") -> bool | None:
    """
    Returns True  → .com is available (RDAP 404)
            False → .com is taken   (RDAP 200)
            None  → unknown (timeout / error)

    Uses RDAP (verisign) — free, no API key.
    """
    fqdn = f"{domain_candidate}.{tld}"
    url = f"https://rdap.verisign.com/{tld}/v1/domain/{fqdn}"
    try:
        resp = requests.get(url, timeout=5, allow_redirects=True)
        if resp.status_code == 200:
            return False   # domain registered
        if resp.status_code == 404:
            return True    # domain available
        return None
    except requests.Timeout:
        logger.debug("RDAP timeout for %s", fqdn)
        return None
    except Exception as exc:
        logger.debug("RDAP error for %s: %s", fqdn, exc)
        return None


def recency_score(date_str: str) -> int:
    try:
        filing = dt.date.fromisoformat(date_str)
    except ValueError:
        return 0
    age = (dt.date.today() - filing).days
    if age < 0:
        return 40   # future date in dataset — treat as very fresh
    if age <= 7:
        return 40
    if age <= 30:
        return 28
    if age <= 90:
        return 12
    return 0


def sector_score(sector: str) -> int:
    if sector in _TOP_SECTORS:
        return 30
    if sector != "other":
        return 18
    return 0


def domain_score(available: bool | None) -> int:
    return 30 if available is True else 0


def compute_prospect_score(
    date_str: str,
    sector: str,
    domain_available: bool | None,
) -> int:
    return min(
        100,
        recency_score(date_str) + sector_score(sector) + domain_score(domain_available),
    )


def score_entities_batch(
    entities: list,  # list of DB EntityModel instances
    check_domains: bool = True,
    delay: float | None = None,
) -> None:
    """Compute and assign prospect scores in-place.  Optionally checks .com domains."""
    if delay is None:
        delay = settings.DOMAIN_CHECK_DELAY

    for ent in entities:
        # Domain candidate
        candidate = extract_domain_candidate(ent.name)
        ent.domain_candidate = candidate or ""
        ent.domain_com = f"{candidate}.com" if candidate else ""

        # Domain availability (rate-limited)
        if check_domains and candidate:
            ent.domain_available = check_domain_available(candidate)
            if delay:
                time.sleep(delay)
        elif not check_domains:
            ent.domain_available = None

        # Sector (already computed before calling this fn)
        ent.prospect_score = compute_prospect_score(
            ent.date, ent.sector, ent.domain_available
        )
