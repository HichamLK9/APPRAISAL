"""Auto-discovering collector registry.

Each module in this package that defines a function named `fetch_from_<name>`
is automatically registered and called by `collect_all()`.
"""
import importlib
import logging
import pkgutil
from pathlib import Path
from typing import Callable, Iterable

from .base import NewEntity

logger = logging.getLogger(__name__)

_REGISTRY: dict[str, Callable[..., Iterable[NewEntity]]] = {}


def register(name: str):
    """Decorator that registers a collector under the given source name."""
    def decorator(fn: Callable):
        _REGISTRY[name] = fn
        return fn
    return decorator


def _auto_import():
    pkg_dir = Path(__file__).parent
    for _, module_name, _ in pkgutil.iter_modules([str(pkg_dir)]):
        if module_name == "base":
            continue
        try:
            importlib.import_module(f".{module_name}", package=__package__)
        except Exception as exc:
            logger.warning("Failed to load collector module '%s': %s", module_name, exc)


def collect_all(
    limit: int = 500,
    enabled_sources: list[str] | None = None,
) -> list[NewEntity]:
    _auto_import()
    all_entities: list[NewEntity] = []
    for name, fn in _REGISTRY.items():
        if enabled_sources and name not in enabled_sources:
            logger.debug("Source '%s' not in enabled list — skipped.", name)
            continue
        try:
            logger.info("Collecting from source '%s' …", name)
            batch = list(fn(limit=limit))
            logger.info("  → %d entities from '%s'", len(batch), name)
            all_entities.extend(batch)
        except Exception as exc:
            logger.error("Collector '%s' failed: %s", name, exc, exc_info=True)
    return all_entities
