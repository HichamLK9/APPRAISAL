"""SQLAlchemy engine + session factory."""
import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from ..config import settings


def _resolve_db_url() -> str:
    url = settings.DATABASE_URL
    if url.startswith("sqlite:///./"):
        rel_path = url[len("sqlite:///./"):]
        abs_path = Path(__file__).parent.parent / rel_path
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{abs_path}"
    return url


_engine = create_engine(
    _resolve_db_url(),
    connect_args={"check_same_thread": False},  # SQLite only
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    from . import models  # noqa: F401 — ensure models are registered
    Base.metadata.create_all(bind=_engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
