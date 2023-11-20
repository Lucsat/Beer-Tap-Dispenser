"""Modelo de representación de la tabla de dispensadores."""
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

# Evitamos el conflicto de detección de tipos entre mypy o pylance y sqlalchemy
# (ver https://docs.sqlalchemy.org/en/14/orm/extensions/mypy.html)
if TYPE_CHECKING:
    from .usage import Usage


class DispenserSpendingLine(Base):
    """Contiene la descripción de la tabla de dispensadores."""

    __tablename__ = "dis_dispenser"

    id: Mapped[int] = mapped_column(
        "dis_id", Integer, primary_key=True, index=True, autoincrement=True
    )
    reference: Mapped[str] = mapped_column(
        "dis_reference", String(length=36), index=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        "dis_created_at", DateTime(timezone=True), default=datetime.utcnow
    )
    flow_volume: Mapped[float] = mapped_column("dis_flow_volume", Float, nullable=False)

    usages: Mapped[List["Usage"]] = relationship(  # noqa: F821
        back_populates="dispenser"
    )
