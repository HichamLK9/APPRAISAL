"""City of Los Angeles – Listing of Active Businesses connector.

Source: LA City Open Data (data.lacity.org)
Dataset: https://data.lacity.org/resource/r4uk-afju.json
         "Listing of Active Businesses" – individual business records with start dates.
Docs:    https://dev.socrata.com/foundry/data.lacity.org/r4uk-afju
"""
import datetime as dt
import logging

import requests

from ..config import settings
from . import register
from .base import NewEntity, get_field

logger = logging.getLogger(__name__)

_URL = settings.LA_API_URL


def _parse_date(raw: str) -> str | None:
    if not raw:
        return None
    try:
        candidate = raw[:10]
        dt.datetime.fromisoformat(candidate)
        return candidate
    except Exception:
        return None


@register("los_angeles")
def fetch_from_los_angeles(limit: int = 500) -> list[NewEntity]:
    headers = {}
    if settings.SOCRATA_APP_TOKEN:
        headers["X-App-Token"] = settings.SOCRATA_APP_TOKEN

    params = {
        "$limit": limit,
        "$order": "location_start_date DESC",
        "$where": "location_start_date IS NOT NULL",
    }

    try:
        resp = requests.get(_URL, params=params, headers=headers, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.error("LA API request failed: %s", exc)
        return []

    rows = resp.json()
    if not isinstance(rows, list):
        logger.error("LA API returned unexpected format: %s", type(rows))
        return []

    if rows:
        logger.debug("LA sample fields: %s", list(rows[0].keys()))

    entities: list[NewEntity] = []
    for row in rows:
        name = get_field(
            row,
            "dba_name", "business_name", "name",
            "primary_naics_description",
        )
        if not name:
            continue

        description = get_field(
            row,
            "primary_naics_description", "naics_description",
            "business_description", "description",
        )
        raw_sector = get_field(
            row,
            "naics", "primary_naics", "naics_code", "sic_code",
        )
        raw_date = get_field(
            row,
            "location_start_date", "location_account_start",
            "start_date", "filing_date", "registration_date",
        )
        entity_type = get_field(row, "business_type", "entity_type", "type")

        date = _parse_date(raw_date)
        if not date:
            continue

        entities.append(
            NewEntity(
                name=name,
                description=description,
                date=date,
                jurisdiction="CA",
                raw_sector=raw_sector,
                source=_URL,
                entity_type=entity_type,
                extra={"city": "Los Angeles"},
            )
        )

    return entities
