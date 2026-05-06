"""Wyoming Secretary of State – Apify scraper connector.

Actor: parseforge/wyoming-business-scraper
Docs:  https://apify.com/parseforge/wyoming-business-scraper

Requires WYOMING_APIFY_TOKEN in environment.
If the token is absent the connector is silently skipped.
"""
import datetime as dt
import logging
import time

import requests

from ..config import settings
from . import register
from .base import NewEntity, get_field

logger = logging.getLogger(__name__)

_APIFY_BASE = "https://api.apify.com/v2"


def _parse_date(raw: str) -> str | None:
    if not raw:
        return None
    try:
        candidate = raw[:10]
        dt.datetime.fromisoformat(candidate)
        return candidate
    except Exception:
        return None


def _run_actor(token: str, actor: str, input_body: dict) -> str | None:
    """Start an Apify actor synchronously and return the default dataset ID."""
    url = f"{_APIFY_BASE}/acts/{actor}/runs?token={token}&timeout=120"
    try:
        resp = requests.post(url, json=input_body, timeout=60)
        resp.raise_for_status()
        return resp.json()["data"]["defaultDatasetId"]
    except Exception as exc:
        logger.error("Apify actor start failed: %s", exc)
        return None


def _wait_for_run(token: str, actor: str, run_id: str, max_wait: int = 180) -> bool:
    """Poll until the run finishes or timeout."""
    url = f"{_APIFY_BASE}/actor-runs/{run_id}?token={token}"
    for _ in range(max_wait // 5):
        time.sleep(5)
        try:
            data = requests.get(url, timeout=15).json()["data"]
            status = data.get("status", "")
            if status == "SUCCEEDED":
                return True
            if status in ("FAILED", "ABORTED", "TIMED-OUT"):
                logger.error("Apify run ended with status: %s", status)
                return False
        except Exception:
            pass
    logger.error("Apify run timed out after %ds", max_wait)
    return False


def _fetch_dataset(token: str, dataset_id: str, limit: int) -> list[dict]:
    url = (
        f"{_APIFY_BASE}/datasets/{dataset_id}/items"
        f"?token={token}&limit={limit}&format=json"
    )
    try:
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        logger.error("Apify dataset fetch failed: %s", exc)
        return []


@register("wyoming")
def fetch_from_wyoming_apify(limit: int = 200) -> list[NewEntity]:
    token = settings.WYOMING_APIFY_TOKEN
    if not token:
        logger.info("WYOMING_APIFY_TOKEN not set — Wyoming source skipped.")
        return []

    actor = settings.WYOMING_APIFY_ACTOR

    # Run actor synchronously via the Apify synchronous API
    sync_url = (
        f"{_APIFY_BASE}/acts/{actor}/run-sync-get-dataset-items"
        f"?token={token}&timeout=120"
    )
    actor_input = {
        "maxItems": limit,
        "dateFrom": "",  # let the actor use its default (most recent)
    }

    try:
        resp = requests.post(sync_url, json=actor_input, timeout=150)
        resp.raise_for_status()
        rows = resp.json()
    except Exception as exc:
        logger.error("Wyoming Apify sync run failed: %s", exc)
        return []

    if not isinstance(rows, list):
        logger.error("Wyoming Apify returned unexpected format: %s", type(rows))
        return []

    if rows:
        logger.debug("Wyoming Apify sample fields: %s", list(rows[0].keys()))

    entities: list[NewEntity] = []
    for row in rows:
        name = get_field(row, "name", "entityName", "business_name")
        if not name:
            continue

        entity_type = get_field(
            row, "entityType", "entity_type", "type", "businessType"
        )
        raw_date = get_field(
            row,
            "formationDate", "formation_date", "filingDate",
            "filing_date", "inceptionDate",
        )
        status = get_field(row, "status", "entityStatus")
        description = f"{entity_type} – {status}".strip(" –")

        date = _parse_date(raw_date)
        if not date:
            continue

        entities.append(
            NewEntity(
                name=name,
                description=description,
                date=date,
                jurisdiction="WY",
                raw_sector="",
                source=f"https://apify.com/{actor}",
                entity_type=entity_type,
            )
        )

    return entities
