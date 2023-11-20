"""Esquemas de representación de datos de la API de los dispensadores."""
from datetime import datetime
from typing import Final, List, Literal

from pydantic import BaseModel, Field

from app.schemas.usage import DispenserUsageOut

DISPENSER_STATUS_OPEN: Final[str] = "open"
DISPENSER_STATUS_CLOSE: Final[str] = "close"


class DispenserSpendingLineBase(BaseModel):
    """Base de los esquemas de representación de datos"""


class DispenserSpendingLineIn(DispenserSpendingLineBase):
    """Base de los esquemas de representación de datos de entrada"""


class DispenserSpendingLineCreateIn(DispenserSpendingLineIn):
    """Esquema de petición para la creación de un dispensador."""

    flow_volume: float = Field(
        json_schema_extra={
            "title": "Volumen inicial del dispensador.",
            "description": (
                "Número de litros por segundo de salida de líquidos del dispensador."
            ),
            "example": 0.0653,
        },
    )


class DispenserSpendingLineUpdateIn(DispenserSpendingLineIn):
    """Esquema de petición para la actualización de estado de un dispensador."""

    status: Literal["open", "close"] = Field(
        json_schema_extra={
            "title": "Nuevo estado del dispensador.",
            "description": (
                "Estado al que se quiere cambiar el dispensador. Puede ser open o "
                "close."
            ),
            "example": "open",
        },
    )
    updated_at: datetime = Field(
        json_schema_extra={
            "title": "Fecha y hora de petición.",
            "description": (
                "Fecha y hora de la petición de cambio de estado del dispensador "
                "en formato ISO 8601 / UTC."
            ),
            "example": "2022-01-01T02:00:00Z",
        }
    )


class DispenserSpendingLineOut(DispenserSpendingLineBase):
    """Base de los esquemas de representación de datos de salida"""


class DispenserSpendingLineAggregateOut(DispenserSpendingLineOut):
    """Esquema de respuesta de la API de consulta agregada de un dispensador"""

    amount: float = Field(
        json_schema_extra={
            "title": "Cantidad total en euros despachada.",
            "description": (
                "Suma total de las cantidades despachadas por todos "
                "los usos realizados en el dispensador."
            ),
            "example": 57.678,
        },
    )
    usages: List[DispenserUsageOut] = []


class DispenserSpendingLineCreateOut(DispenserSpendingLineOut):
    """Esquema de respuesta de la API de creación de un dispensador"""

    id: str = Field(
        pattern=r"^[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}$",
        json_schema_extra={
            "title": "Referencia externa del dispensador",
            "description": (
                "UUID Versión 4 con la identificación externa del dispensador."
            ),
            "example": "b3ea6cde-c60d-4c68-b42f-1964205d557f",
        },
    )
    flow_volume: float = Field(
        json_schema_extra={
            "title": "Volumen inicial del dispensador.",
            "description": (
                "Número de litros por segundo de salida de líquidos del dispensador."
            ),
            "example": 0.0653,
        },
    )
