"""Analytics endpoints for the dashboard."""
import datetime as dt
import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy import Integer, func
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...db.models import EntityModel
from ...classifier.sectors import SECTOR_KEYWORDS

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview")
def overview(
    db: Session = Depends(get_db),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
):
    """High-level KPIs for the selected period."""
    q = db.query(EntityModel)
    if date_from:
        q = q.filter(EntityModel.date >= date_from)
    if date_to:
        q = q.filter(EntityModel.date <= date_to)

    total = q.count()
    hot = q.filter(EntityModel.prospect_score >= 60).count()
    with_domain = q.filter(EntityModel.domain_available == True).count()
    avg_score = db.query(func.avg(EntityModel.prospect_score)).scalar() or 0

    return {
        "total_entities": total,
        "hot_prospects": hot,
        "with_com_available": with_domain,
        "avg_prospect_score": round(float(avg_score), 1),
    }


@router.get("/entities-per-day")
def entities_per_day(
    db: Session = Depends(get_db),
    days: int = Query(default=30, ge=1, le=365),
):
    """Number of entities filed per day for the last N days."""
    cutoff = (dt.date.today() - dt.timedelta(days=days)).isoformat()
    rows = (
        db.query(EntityModel.date, func.count(EntityModel.id).label("count"))
        .filter(EntityModel.date >= cutoff)
        .group_by(EntityModel.date)
        .order_by(EntityModel.date)
        .all()
    )
    return [{"date": r.date, "count": r.count} for r in rows]


@router.get("/sector-distribution")
def sector_distribution(
    db: Session = Depends(get_db),
    date: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
):
    """Entity count by sector for the selected period."""
    q = db.query(EntityModel.sector, func.count(EntityModel.id).label("count"))
    if date:
        q = q.filter(EntityModel.date == date)
    else:
        if date_from:
            q = q.filter(EntityModel.date >= date_from)
        if date_to:
            q = q.filter(EntityModel.date <= date_to)

    rows = q.group_by(EntityModel.sector).order_by(func.count(EntityModel.id).desc()).all()
    return [{"sector": r.sector, "count": r.count} for r in rows]


@router.get("/domain-availability-by-sector")
def domain_availability_by_sector(
    db: Session = Depends(get_db),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
):
    """Percentage of entities with .com available, grouped by sector."""
    q = db.query(
        EntityModel.sector,
        func.count(EntityModel.id).label("total"),
        func.sum(
            func.cast(EntityModel.domain_available == True, Integer)
        ).label("available"),
    )
    if date_from:
        q = q.filter(EntityModel.date >= date_from)
    if date_to:
        q = q.filter(EntityModel.date <= date_to)

    rows = q.filter(EntityModel.domain_available.isnot(None)).group_by(EntityModel.sector).all()

    return [
        {
            "sector": r.sector,
            "total": r.total,
            "available": int(r.available or 0),
            "pct_available": round(100 * int(r.available or 0) / r.total, 1) if r.total else 0,
        }
        for r in rows
    ]


@router.get("/top-jurisdictions")
def top_jurisdictions(
    db: Session = Depends(get_db),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    limit: int = Query(default=10, ge=1, le=50),
):
    q = db.query(
        EntityModel.jurisdiction,
        func.count(EntityModel.id).label("count"),
        func.avg(EntityModel.prospect_score).label("avg_score"),
    )
    if date_from:
        q = q.filter(EntityModel.date >= date_from)
    if date_to:
        q = q.filter(EntityModel.date <= date_to)

    rows = (
        q.group_by(EntityModel.jurisdiction)
        .order_by(func.count(EntityModel.id).desc())
        .limit(limit)
        .all()
    )
    return [
        {"jurisdiction": r.jurisdiction, "count": r.count, "avg_score": round(float(r.avg_score or 0), 1)}
        for r in rows
    ]


@router.get("/hot-prospects")
def hot_prospects(
    db: Session = Depends(get_db),
    min_score: int = Query(default=60, ge=0, le=100),
    limit: int = Query(default=20, ge=1, le=100),
    days: int = Query(default=30, ge=1, le=365),
):
    """Entities ranked by prospect score within the last N days."""
    cutoff = (dt.date.today() - dt.timedelta(days=days)).isoformat()
    rows = (
        db.query(EntityModel)
        .filter(EntityModel.date >= cutoff)
        .filter(EntityModel.prospect_score >= min_score)
        .order_by(EntityModel.prospect_score.desc())
        .limit(limit)
        .all()
    )
    return [e.to_dict() for e in rows]


@router.get("/sectors")
def list_sectors():
    """Return all known sector keys + labels."""
    labels = {
        "fintech": "Fintech",
        "artificial_intelligence": "Artificial Intelligence",
        "digital_health_biotech": "Digital Health / Biotech",
        "cybersecurity": "Cybersecurity",
        "saas_cloud_infra": "SaaS / Cloud Infra",
        "ecommerce_marketplaces": "E-commerce / Marketplaces",
        "real_estate_proptech": "Real Estate / PropTech",
        "cleantech_energy": "CleanTech / Energy",
        "fitness_wellness": "Fitness & Wellness",
        "education_creator": "Education / Creator",
        "other": "Other",
    }
    return [{"key": k, "label": v} for k, v in labels.items()]
