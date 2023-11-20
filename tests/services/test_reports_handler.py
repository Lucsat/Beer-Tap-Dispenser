"""
    Prueba las acciones relacionadas con el servicio de cálculo de gastos
    de los dispensadores.
"""
from datetime import datetime, timedelta, timezone

import pytest

from app.services import reports_handler
from tests.conftest import DEFAULT_FLOW_VOLUME
from tests.crudutils import (
    do_complete_dispenser_usage_requests,
    do_create_dispenser_request,
)


@pytest.mark.asyncio
async def test_calculate_total_spent_without_usages(
    db_session, valid_new_dispenser_request
):
    """
    Prueba los cálculos de dinero gastado por un dispensador en el que todavía
    no se ha realizado ningún uso.

    Args:
        db_session (:class:`app.core.db.SessionLocal`): sesión local de
            acceso a la base de datos.
        valid_new_dispenser_request
        (:class:`app.schemas.dispenser.DispenserSpendingLineCreateIn`):
            Datos de inicialización del nuevo dispensador a crear (fixture).
    """
    db_new_dispenser = await do_create_dispenser_request(
        db_session,
        valid_new_dispenser_request,
    )

    aggregate = reports_handler.calculate_total_amount_spent(dispenser=db_new_dispenser)

    assert aggregate.amount == 0
    assert len(aggregate.usages) == 0


@pytest.mark.asyncio
async def test_calculate_total_spent_with_one_usage(
    db_session,
    valid_new_dispenser_request,
    change_status_request,
):
    """
    Prueba los cálculos de dinero gastado por un dispensador en el que todavía
    no se ha realizado ningún uso.

    Args:
        db_session (:class:`app.core.db.SessionLocal`): sesión local de
            acceso a la base de datos.
        valid_new_dispenser_request
        (:class:`app.schemas.dispenser.DispenserSpendingLineCreateIn`):
            Datos de inicialización del nuevo dispensador a crear (fixture).
        change_status_request
        (:class:`app.schemas.dispenser.DispenserSpendingLineUpdateIn`):
            Datos para realizar el cambio de estado del dispensador.
    """
    db_new_dispenser = await do_create_dispenser_request(
        db_session,
        valid_new_dispenser_request,
    )

    now = datetime.now(tz=timezone.utc)
    elapsed_seconds = 5

    await do_complete_dispenser_usage_requests(
        db_session=db_session,
        db_dispenser=db_new_dispenser,
        change_status_request=change_status_request,
        open_at=now,
        elapsed_seconds=elapsed_seconds,
    )

    aggregate = reports_handler.calculate_total_amount_spent(dispenser=db_new_dispenser)

    spent = elapsed_seconds * reports_handler.COST_PER_SECOND
    single_usage = aggregate.usages[0]

    assert aggregate.amount == spent
    assert len(aggregate.usages) == 1
    assert single_usage.total_spent == spent
    assert single_usage.closed_at == now + timedelta(seconds=elapsed_seconds)
    assert single_usage.flow_volume == DEFAULT_FLOW_VOLUME
