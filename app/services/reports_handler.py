"""Conjunto de métodos de gestión y elaboración de informes y estructuras de datos."""


from datetime import datetime, timezone
from typing import Final

from app.models.dispenser import DispenserSpendingLine
from app.schemas.dispenser import DispenserSpendingLineAggregateOut
from app.schemas.usage import DispenserUsageOut

COST_PER_SECOND: Final[float] = 12.25


def calculate_total_amount_spent(
    dispenser: DispenserSpendingLine,
) -> DispenserSpendingLineAggregateOut:
    """
    Realiza los cálculos relacionados con el dinero gastado por el dispensador,
    en su totalidad, y por cada uso realizado.

    Args:
        dispenser (:class:`app.models.dispenser.DispenserSpendingLine`):
            objeto con los datos del dispensador en la base de datos.

    Returns:
        Instancia del modelo
        :class:`~app.schemas.dispenser.DispenserSpendingLineAggregateOut`
        con los datos agregados del dispensador y sus usos.
    """
    db_usages = dispenser.usages
    usages_out = []
    amount = 0.0

    for usage in db_usages:
        closed_at = usage.closed_at
        opened_at = usage.opened_at

        seconds_elapsed = (
            (closed_at - opened_at).seconds
            if closed_at is not None
            else (datetime.now(tz=timezone.utc) - opened_at).seconds
        )

        total_spent = COST_PER_SECOND * seconds_elapsed
        amount += total_spent

        usages_out.append(
            DispenserUsageOut(
                total_spent=total_spent,
                opened_at=opened_at,
                closed_at=closed_at,
                flow_volume=dispenser.flow_volume,
            )
        )

    return DispenserSpendingLineAggregateOut(amount=amount, usages=usages_out)
