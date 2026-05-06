"""Hawaii Business Registration connector.

Source: City & County of Honolulu Open Data
Dataset: https://data.honolulu.gov/resource/9k54-ztb8.json
Docs:    https://dev.socrata.com/foundry/data.honolulu.gov/9k54-ztb8
"""
import datetime as dt
import logging

import requests

from ..config import settings
from . import register
from .base import NewEntity, get_field

logger = logging.getLogger(__name__)

_URL = settings.HAWAII_API_URL


def _parse_date(raw: str) -> str | None:
    if not raw:
        return None
    try:
        candidate = raw[:10]
        dt.datetime.fromisoformat(candidate)
        return candidate
    except Exception:
        return None


@register("hawaii")
def fetch_from_hawaii(limit: int = 500) -> list[NewEntity]:
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
        logger.error("Hawaii API request failed: %s", exc)
        return []

    rows = resp.json()
    if not isinstance(rows, list):
        logger.error("Hawaii API returned unexpected format: %s", type(rows))
        return []

    if rows:
        logger.debug("Hawaii sample fields: %s", list(rows[0].keys()))

    entities: list[NewEntity] = []
    for row in rows:
        name = get_field(
            row,
            "business_name", "tradename", "trade_name", "dba_name",
            "entity_name", "name",
        )
        if not name:
            continue

        description = get_field(
            row,
            "naics_description", "business_description", "business_purpose",
            "activity", "description",
        )
        raw_sector = get_field(
            row,
            "naics_code", "naics_sector", "sic_code", "industry_code",
        )
        raw_date = get_field(
            row,
            "registration_date", "date_of_registration", "filing_date",
            "formation_date", "date_registered", "start_date", "created_at",
        )
        entity_type = get_field(row, "entity_type", "business_type", "type", "structure")

        date = _parse_date(raw_date)
        if not date:
            continue

        entities.append(
            NewEntity(
                name=name,
                description=description,
                date=date,
                jurisdiction="HI",
                raw_sector=raw_sector,
                source=_URL,
                entity_type=entity_type,
            )
        )

    return entities
