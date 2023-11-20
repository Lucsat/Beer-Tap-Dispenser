import random
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.encoders import jsonable_encoder

from app.schemas.dispenser import DISPENSER_STATUS_OPEN
from app.services import reports_handler
from tests.apiutils import do_complete_usage_request, do_create_dispenser_request


@pytest.mark.anyio
async def test_get_data_unknown_dispenser(async_app_client):
    """
    Prueba la petición de obtención de datos de uso de un dispensador inexistente.

    Args:
        async_app_client (:class:`httpx.AsyncClient`): cliente HTTP asíncrono (DI).
    """
    response = await async_app_client.get(f"/api/dispenser/{str(uuid.uuid4())}")

    assert response.status_code == 404


@pytest.mark.anyio
async def test_get_dispenser_no_usages(
    async_app_client,
    valid_new_dispenser_request,
):
    """
    Prueba la petición de obtención de datos de uso de un dispensador sin usos.

    Args:
        async_app_client (:class:`httpx.AsyncClient`): cliente HTTP asíncrono (DI).
        valid_new_dispenser_request
        (:class:`app.schemas.dispenser.DispenserSpendingLineCreateIn`):
            Datos de inicialización del nuevo dispensador a crear (fixture).
    """
    response, dispenser = await do_create_dispenser_request(
        async_app_client, valid_new_dispenser_request
    )

    response = await async_app_client.get(f"/api/dispenser/{dispenser.get('id')}")

    data = response.json()
    usages = data.get("usages")

    assert response.status_code == 200
    assert len(usages) == 0
    assert data.get("amount") == 0.0


@pytest.mark.anyio
async def test_get_dispenser_one_usage_already_opened(
    async_app_client,
    valid_new_dispenser_request,
    change_status_request,
):
    """
    Prueba la petición de obtención de datos de uso de un dispensador con un
    único uso, todavía abierto.

    Args:
        async_app_client (:class:`httpx.AsyncClient`): cliente HTTP asíncrono (DI).
        valid_new_dispenser_request
        (:class:`app.schemas.dispenser.DispenserSpendingLineCreateIn`):
            Datos de inicialización del nuevo dispensador a crear (fixture).
    """
    response, dispenser = await do_create_dispenser_request(
        async_app_client, valid_new_dispenser_request
    )

    new_dispenser_id = dispenser.get("id")
    now = datetime.now(tz=timezone.utc)

    simulated_elapsed_seconds = 2

    # Restamos algunos segundos, simulando un uso abierto y sin cerrar con
    # cierto tiempo transcurrido
    response = await async_app_client.put(
        f"/api/dispenser/{new_dispenser_id}",
        json=jsonable_encoder(
            change_status_request(
                status=DISPENSER_STATUS_OPEN,
                when=now - timedelta(seconds=simulated_elapsed_seconds),
            ),
        ),
    )

    # Tratamos de cerrar 10 segundos después el dispensador ya cerrado previamente
    response = await async_app_client.get(f"/api/dispenser/{new_dispenser_id}")

    data = response.json()
    usages = data.get("usages")

    expected_spent = simulated_elapsed_seconds * reports_handler.COST_PER_SECOND

    assert response.status_code == 200
    assert len(usages) == 1
    assert data.get("amount") == expected_spent
    assert usages[0].get("opened_at") is not None
    assert usages[0].get("close_at") is None
    assert usages[0].get("total_spent") == expected_spent


@pytest.mark.anyio
async def test_get_dispenser_multiple_usages_and_closed(
    async_app_client,
    valid_new_dispenser_request,
    change_status_request,
):
    """
    Prueba la petición de obtención de datos de uso de un dispensador con varios
    usos, y que ya se encuentra cerrado.

    Args:
        async_app_client (:class:`httpx.AsyncClient`): cliente HTTP asíncrono
            (DI).
        valid_new_dispenser_request
        (:class:`app.schemas.dispenser.DispenserSpendingLineCreateIn`):
            Datos de inicialización del nuevo dispensador a crear (fixture).
    """
    response, dispenser = await do_create_dispenser_request(
        async_app_client, valid_new_dispenser_request
    )

    new_dispenser_id = dispenser.get("id")

    now = datetime.now(tz=timezone.utc)
    gap_seconds_between_events = 2
    random_usages = range(random.randrange(1, 6))

    # Abrimos y cerramos el dispensador un número aletario de veces. Entre cada
    # uso pasarán `gap_seconds_between_events` segundos, y cada uso tendrá una
    # duración de `gap_seconds_between_events` segundos
    for usage in random_usages:
        simulated_open_at = now + timedelta(
            seconds=(gap_seconds_between_events * usage) * gap_seconds_between_events
        )

        response = await do_complete_usage_request(
            client=async_app_client,
            dispenser_id=new_dispenser_id,
            change_status_request=change_status_request,
            open_at=simulated_open_at,
            elapsed_seconds=gap_seconds_between_events,
        )

    response = await async_app_client.get(f"/api/dispenser/{new_dispenser_id}")

    data = response.json()

    expected_spent = len(random_usages) * (
        reports_handler.COST_PER_SECOND * gap_seconds_between_events
    )

    assert response.status_code == 200
    assert len(data.get("usages")) == len(random_usages)
    assert data.get("amount") == expected_spent
