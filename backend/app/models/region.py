from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Region(Base):
    __tablename__ = "regions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    level: Mapped[str] = mapped_column(String(20))  # country | region | department
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("regions.id"), nullable=True)

    parent: Mapped["Region | None"] = relationship(
        "Region", back_populates="children", remote_side="Region.id"
    )
    children: Mapped[list["Region"]] = relationship("Region", back_populates="parent")
