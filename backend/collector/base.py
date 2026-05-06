"""Shared data model for all collectors."""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class NewEntity:
    name: str
    description: str
    date: str          # ISO YYYY-MM-DD
    jurisdiction: str  # State abbreviation or 'US'
    raw_sector: str
    source: str
    entity_type: str = ""
    extra: dict[str, Any] = field(default_factory=dict)


def get_field(row: dict, *keys: str, default: str = "") -> str:
    """Try multiple field-name variants (exact, then case-insensitive)."""
    for key in keys:
        if key in row and row[key] not in (None, "", "null"):
            return str(row[key]).strip()
    row_lower = {k.lower(): v for k, v in row.items()}
    for key in keys:
        val = row_lower.get(key.lower())
        if val not in (None, "", "null"):
            return str(val).strip()
    return default
