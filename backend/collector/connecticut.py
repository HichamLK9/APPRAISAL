"""Connecticut Secretary of State Business Registry connector.

Source: Connecticut Open Data (data.ct.gov)
Dataset: https://data.ct.gov/resource/n7gm-hh35.json  (CT Business Registry - Master)
Docs:    https://dev.socrata.com/foundry/data.ct.gov/n7gm-hh35
"""
import datetime as dt
import logging

import requests

from ..config import settings
from . import register
from .base import NewEntity, get_field

logger = logging.getLogger(__name__)

_URL = settings.CONNECTICUT_API_URL


def _parse_date(raw: str) -> str | None:
    if not raw:
        return None
    try:
        candidate = raw[:10]
        dt.datetime.fromisoformat(candidate)
        return candidate
    except Exception:
        return None


@register("connecticut")
def fetch_from_connecticut(limit: int = 500) -> list[NewEntity]:
    headers = {}
    if settings.SOCRATA_APP_TOKEN:
        headers["X-App-Token"] = settings.SOCRATA_APP_TOKEN

    params = {
        "$limit": limit,
        "$order": ":created_at DESC",
    }

    try:
        resp = requests.get(_URL, params=params, headers=headers, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.error("Connecticut API request failed: %s", exc)
        return []

    rows = resp.json()
    if not isinstance(rows, list):
        logger.error("Connecticut API returned unexpected format: %s", type(rows))
        return []

    if rows:
        logger.debug("Connecticut sample fields: %s", list(rows[0].keys()))

    entities: list[NewEntity] = []
    for row in rows:
        name = get_field(
            row,
            "business_name", "name", "entity_name",
            "trade_name", "organization_name",
        )
        if not name:
            continue

        description = get_field(
            row,
            "business_description", "naics_description", "purpose",
            "business_type", "type",
        )
        raw_sector = get_field(
            row,
            "naics_code", "naics_sector", "sic_code", "industry",
        )
        raw_date = get_field(
            row,
            "date_filed", "filing_date", "date_of_organization",
            "registration_date", "formation_date", "created_date",
        )
        entity_type = get_field(
            row,
            "entity_type", "business_type", "type", "structure", "category",
        )
        city = get_field(row, "city", "town", "municipality", "mailing_city")
        state = get_field(row, "state", "mailing_state", "jurisdiction")
        jurisdiction = state.upper() if state else "CT"
        if city:
            jurisdiction = "CT"  # normalise — CT dataset may mix states

        date = _parse_date(raw_date)
        if not date:
            continue

        entities.append(
            NewEntity(
                name=name,
                description=description,
                date=date,
                jurisdiction=jurisdiction,
                raw_sector=raw_sector,
                source=_URL,
                entity_type=entity_type,
            )
        )

    return entities
