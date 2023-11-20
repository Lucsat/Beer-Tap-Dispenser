"""Esquemas de representación de datos de la API de los dispensadores."""
from datetime import datetime

from pydantic import BaseModel, Field


class DispenserUsageBase(BaseModel):
    """Base de los esquemas de representación de datos"""


class DispenserUsageOut(DispenserUsageBase):
    """Base de los esquemas de representación de datos de salida"""

    opened_at: datetime = Field(
        json_schema_extra={
            "title": "Fecha y hora de petición de apertura.",
            "description": (
                "Fecha y hora de la petición de apertura del dispensador "
                "en formato ISO 8601 / UTC."
            ),
            "example": "2022-01-01T02:00:00Z",
        }
    )
    closed_at: datetime | None = Field(
        default=None,
        json_schema_extra={
            "title": "Fecha y hora de petición de cierre.",
            "description": (
                "Fecha y hora de la petición de cierre del dispensador "
                "en formato ISO 8601 / UTC."
            ),
            "example": "2022-01-01T02:00:50Z",
        },
    )
    flow_volume: float = Field(
        json_schema_extra={
            "title": "Volumen de suministro de líquido.",
            "description": "Número de litros por segundo de salida del dispensador.",
            "example": 0.064,
        },
    )
    total_spent: float = Field(
        json_schema_extra={
            "title": "Cantidad total en euros despachada.",
            "description": (
                "Cantidad de líquido despachada por el uso, "
                "definitiva o particial hasta el momento de la consulta."
            ),
            "example": 39.2,
        },
    )
