"""APScheduler – daily collection + scoring job."""
import csv
import datetime as dt
import logging
import os
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from ..collector import collect_all
from ..classifier.sectors import classify_sector
from ..config import settings
from ..db.database import SessionLocal
from ..db.models import EntityModel
from ..scorer.prospect import extract_domain_candidate, score_entities_batch

logger = logging.getLogger(__name__)

_scheduler = BackgroundScheduler(timezone="UTC")


def run_daily_collection(target_date: str | None = None) -> int:
    """Collect, classify, score and persist entities for the given date.

    Returns the number of new entities stored.
    """
    if target_date is None:
        target_date = settings.TARGET_DATE or dt.date.today().isoformat()

    logger.info("=== Daily collection started for %s ===", target_date)

    raw_entities = collect_all(
        limit=settings.DEFAULT_LIMIT,
        enabled_sources=settings.ENABLED_SOURCES,
    )

    if not raw_entities:
        logger.warning("No entities collected from any source.")
        return 0

    # Filter by target date
    dated = [e for e in raw_entities if e.date == target_date]
    logger.info("%d entities after date filter (%s)", len(dated), target_date)

    if not dated:
        logger.warning("No entities found for date %s.", target_date)
        return 0

    db = SessionLocal()
    new_count = 0
    new_models: list[EntityModel] = []

    try:
        for ent in dated:
            sector = classify_sector(ent.name, ent.description, ent.raw_sector)
            domain_candidate = extract_domain_candidate(ent.name) or ""
            model = EntityModel(
                name=ent.name,
                description=ent.description,
                date=ent.date,
                jurisdiction=ent.jurisdiction,
                raw_sector=ent.raw_sector,
                source=ent.source,
                entity_type=ent.entity_type,
                sector=sector,
                domain_candidate=domain_candidate,
                domain_com=f"{domain_candidate}.com" if domain_candidate else "",
            )
            # Use merge to ignore duplicates (unique constraint)
            existing = (
                db.query(EntityModel)
                .filter(
                    EntityModel.name == model.name,
                    EntityModel.date == model.date,
                    EntityModel.jurisdiction == model.jurisdiction,
                )
                .first()
            )
            if not existing:
                db.add(model)
                new_models.append(model)
                new_count += 1

        db.commit()
        for m in new_models:
            db.refresh(m)

        logger.info("Stored %d new entities. Computing prospect scores…", new_count)

        # Score new entities (includes domain RDAP check — rate-limited)
        if new_models:
            score_entities_batch(new_models, check_domains=True)
            for m in new_models:
                m.score_computed_at = dt.datetime.utcnow()
            db.commit()

    except Exception as exc:
        logger.error("Error during collection job: %s", exc, exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()

    # Export CSV
    _export_csv(target_date)

    logger.info("=== Daily collection finished: %d new entities ===", new_count)
    return new_count


def _export_csv(target_date: str) -> None:
    export_dir = Path(settings.OUTPUT_CSV_DIR)
    export_dir.mkdir(parents=True, exist_ok=True)
    output_path = export_dir / f"entities_{target_date}.csv"

    db = SessionLocal()
    try:
        entities = (
            db.query(EntityModel)
            .filter(EntityModel.date == target_date)
            .order_by(EntityModel.prospect_score.desc())
            .all()
        )
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "date", "name", "jurisdiction", "entity_type",
                "sector", "raw_sector", "prospect_score",
                "domain_com", "domain_available", "description", "source",
            ])
            for e in entities:
                writer.writerow([
                    e.date, e.name, e.jurisdiction, e.entity_type,
                    e.sector, e.raw_sector, e.prospect_score,
                    e.domain_com, e.domain_available, e.description, e.source,
                ])
        logger.info("CSV exported → %s (%d rows)", output_path, len(entities))
    finally:
        db.close()


def start_scheduler() -> None:
    if _scheduler.running:
        return

    _scheduler.add_job(
        run_daily_collection,
        trigger=CronTrigger(
            hour=settings.SCHEDULER_HOUR,
            minute=settings.SCHEDULER_MINUTE,
            timezone="UTC",
        ),
        id="daily_collection",
        replace_existing=True,
        misfire_grace_time=3600,
    )
    _scheduler.start()
    logger.info(
        "Scheduler started — daily collection at %02d:%02d UTC",
        settings.SCHEDULER_HOUR,
        settings.SCHEDULER_MINUTE,
    )
