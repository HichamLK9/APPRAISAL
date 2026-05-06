"""ORM model for business entities."""
import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class EntityModel(Base):
    __tablename__ = "entities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Core fields
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    date: Mapped[str] = mapped_column(String(10), nullable=False)  # YYYY-MM-DD
    jurisdiction: Mapped[str] = mapped_column(String(10), nullable=False)
    raw_sector: Mapped[str] = mapped_column(String(128), default="")
    source: Mapped[str] = mapped_column(String(512), default="")
    entity_type: Mapped[str] = mapped_column(String(64), default="")

    # Derived
    sector: Mapped[str] = mapped_column(String(64), default="other")

    # Prospect scoring
    prospect_score: Mapped[int] = mapped_column(Integer, default=0)
    domain_candidate: Mapped[str] = mapped_column(String(64), default="")
    domain_com: Mapped[str] = mapped_column(String(70), default="")
    domain_available: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    # Housekeeping
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )
    score_computed_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    __table_args__ = (
        # Deduplicate: same name + date + jurisdiction treated as one entity
        UniqueConstraint("name", "date", "jurisdiction", name="uq_entity_key"),
        Index("ix_entities_date", "date"),
        Index("ix_entities_sector", "sector"),
        Index("ix_entities_jurisdiction", "jurisdiction"),
        Index("ix_entities_score", "prospect_score"),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "date": self.date,
            "jurisdiction": self.jurisdiction,
            "sector": self.sector,
            "raw_sector": self.raw_sector,
            "entity_type": self.entity_type,
            "source": self.source,
            "prospect_score": self.prospect_score,
            "domain_com": self.domain_com,
            "domain_available": self.domain_available,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
