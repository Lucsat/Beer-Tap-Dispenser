"""Modelo de representación de la tabla de usos de los dispensadores."""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

# Evitamos el conflicto de detección de tipos entre mypy o pylance y sqlalchemy
# (ver https://docs.sqlalchemy.org/en/14/orm/extensions/mypy.html)
if TYPE_CHECKING:
    from .dispenser import DispenserSpendingLine


class Usage(Base):
    """Contiene la descripción de la tabla de usos realizados a los dispensadores."""

    __tablename__ = "usa_usage"

    id: Mapped[int] = mapped_column(
        "usa_id", Integer, primary_key=True, index=True, autoincrement=True
    )
    opened_at: Mapped[datetime] = mapped_column(
        "usa_opened_at", DateTime(timezone=True), default=datetime.utcnow
    )
    closed_at: Mapped[datetime] = mapped_column(
        "usa_closed_at", DateTime(timezone=True), default=None, nullable=True
    )
    dispenser_id = mapped_column(
        "dis_id", Integer, ForeignKey("dis_dispenser.dis_id"), nullable=False
    )

    dispenser: Mapped["DispenserSpendingLine"] = relationship(  # noqa: F821
        back_populates="usages"
    )
