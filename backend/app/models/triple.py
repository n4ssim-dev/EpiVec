from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Triple(Base):
    """Triplet de connaissance (sujet, prédicat, objet) issu de l'ingestion."""

    __tablename__ = "triples"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subject: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    predicate: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    object: Mapped[str] = mapped_column(String(500), nullable=False)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
