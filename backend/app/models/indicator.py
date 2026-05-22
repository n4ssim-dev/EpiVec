from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Indicator(Base):
    """Série temporelle épidémiologique (cas, décès, hospitalisations…) par maladie et région."""

    __tablename__ = "indicators"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    disease: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    region_code: Mapped[str] = mapped_column(
        String(20), ForeignKey("regions.code"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    metric: Mapped[str] = mapped_column(String(100))  # cases | deaths | hospitalizations | rt
    value: Mapped[float] = mapped_column(Float)
    source: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
