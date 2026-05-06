"""REST endpoints for entities: list, filter, export CSV."""
import csv
import io
import datetime as dt
import logging

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ...db.database import get_db
from ...db.models import EntityModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/entities", tags=["entities"])


def _build_query(
    db: Session,
    date: str | None,
    date_from: str | None,
    date_to: str | None,
    sector: list[str] | None,
    jurisdiction: list[str] | None,
    source: str | None,
    min_score: int,
    domain_available: bool | None,
    q: str | None,
):
    query = db.query(EntityModel)

    if date:
        query = query.filter(EntityModel.date == date)
    else:
        if date_from:
            query = query.filter(EntityModel.date >= date_from)
        if date_to:
            query = query.filter(EntityModel.date <= date_to)

    if sector:
        query = query.filter(EntityModel.sector.in_(sector))
    if jurisdiction:
        query = query.filter(EntityModel.jurisdiction.in_(jurisdiction))
    if source:
        query = query.filter(EntityModel.source.contains(source))
    if min_score > 0:
        query = query.filter(EntityModel.prospect_score >= min_score)
    if domain_available is not None:
        query = query.filter(EntityModel.domain_available == domain_available)
    if q:
        pattern = f"%{q}%"
        query = query.filter(
            or_(
                EntityModel.name.ilike(pattern),
                EntityModel.description.ilike(pattern),
            )
        )

    return query


@router.get("")
def list_entities(
    db: Session = Depends(get_db),
    date: str | None = Query(None, description="Exact filing date YYYY-MM-DD"),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    sector: list[str] = Query(default=[]),
    jurisdiction: list[str] = Query(default=[]),
    source: str | None = Query(None),
    min_score: int = Query(default=0, ge=0, le=100),
    domain_available: bool | None = Query(None),
    q: str | None = Query(None, description="Search in name / description"),
    sort_by: str = Query(default="prospect_score"),
    sort_dir: str = Query(default="desc"),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=50, ge=1, le=500),
):
    query = _build_query(
        db, date, date_from, date_to,
        sector or None, jurisdiction or None,
        source, min_score, domain_available, q,
    )
    total = query.count()

    # Sorting
    col = getattr(EntityModel, sort_by, EntityModel.prospect_score)
    if sort_dir == "desc":
        query = query.order_by(col.desc())
    else:
        query = query.order_by(col.asc())

    offset = (page - 1) * per_page
    items = query.offset(offset).limit(per_page).all()

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "items": [e.to_dict() for e in items],
    }


@router.get("/export")
def export_csv(
    db: Session = Depends(get_db),
    date: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    sector: list[str] = Query(default=[]),
    jurisdiction: list[str] = Query(default=[]),
    min_score: int = Query(default=0, ge=0, le=100),
    domain_available: bool | None = Query(None),
    q: str | None = Query(None),
):
    query = _build_query(
        db, date, date_from, date_to,
        sector or None, jurisdiction or None,
        None, min_score, domain_available, q,
    )
    entities = query.order_by(EntityModel.prospect_score.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
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

    output.seek(0)
    filename = f"entities_{date or 'export'}_{dt.date.today()}.csv"
    return StreamingResponse(
        iter([output.read()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{entity_id}")
def get_entity(entity_id: int, db: Session = Depends(get_db)):
    ent = db.query(EntityModel).filter(EntityModel.id == entity_id).first()
    if not ent:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Entity not found")
    return ent.to_dict()
