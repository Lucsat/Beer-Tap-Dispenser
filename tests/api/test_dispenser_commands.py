import uuid
from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest
from fastapi.encoders import jsonable_encoder

from app.schemas.dispenser import DISPENSER_STATUS_CLOSE, DISPENSER_STATUS_OPEN
from tests.apiutils import do_complete_usage_request, do_create_dispenser_request


@pytest.mark.anyio
async def test_create_dispenser(async_app_client, valid_new_dispenser_request):
    """
    Prueba la petición de creación de un dispensador.

    Args:
        async_app_client (:class:`httpx.AsyncClient`): cliente HTTP asíncrono (DI).
        valid_new_dispenser_request
        (:class:`app.schemas.dispenser.DispenserSpendingLineCreateIn`):
            Datos de inicialización del nuevo dispensador a crear (fixture).
    """
    response, dispenser = await do_create_dispenser_request(
        async_app_client, valid_new_dispenser_request
    )

    assert response.status_code == 200
    assert UUID(dispenser.get("id"), version=4)
    assert dispenser.get("flow_volume") == valid_new_dispenser_request.flow_volume


@pytest.mark.anyio
async def test_create_dispenser_without_data(async_app_client):
    """
    Prueba la petición de creación de un dispensador pasando insuficientes datos.

    Args:
        async_app_client (:class:`httpx.AsyncClient`): cliente HTTP asíncrono (DI).
    """
    response = await async_app_client.post("/api/dispenser/")

    assert response.status_code == 422


@pytest.mark.anyio
async def test_open_new_dispenser(
    async_app_client, valid_new_dispenser_request, change_status_request
):
    """
    Prueba la petición para abrir un nuevo dispensador, que está cerrado.

    Args:
        async_app_client (:class:`httpx.AsyncClient`): cliente HTTP
            asíncrono (DI).
        valid_new_dispenser_request
        (:class:`app.schemas.dispenser.DispenserSpendingLineCreateIn`):
            Datos de inicialización del nuevo dispensador a crear (fixture).
        change_status_request
        (:class:`app.schemas.dispenser.DispenserSpendingLineUpdateIn`):
            Datos con petición de cambio de estado de un dispensador
            (fixture).
    """
    response, dispenser = await do_create_dispenser_request(
        async_app_client, valid_new_dispenser_request
    )

    new_dispenser_id = dispenser.get("id")

    response = await async_app_client.put(
        f"/api/dispenser/{new_dispenser_id}",
        json=jsonable_encoder(
            change_status_request(
                status=DISPENSER_STATUS_OPEN, when=datetime.now(tz=timezone.utc)
            ),
        ),
    )

    assert response.status_code == 202


@pytest.mark.anyio
async def test_close_new_dispenser(
    async_app_client,
    valid_new_dispenser_request,
    change_status_request,
):
    """
    Prueba la petición para cerrar un nuevo dispensador, que está cerrado.

    Args:
        async_app_client (:class:`httpx.AsyncClient`): cliente HTTP asíncrono (DI).
        valid_new_dispenser_request
        (:class:`app.schemas.dispenser.DispenserSpendingLineCreateIn`):
            Datos de inicialización del nuevo dispensador a crear (fixture).
        change_status_request
        (:class:`app.schemas.dispenser.DispenserSpendingLineUpdateIn`):
            Datos con petición de cambio de estado de un dispensador (fixture).
    """
    response, dispenser = await do_create_dispenser_request(
        async_app_client, valid_new_dispenser_request
    )

    new_dispenser_id = dispenser.get("id")

    response = await do_complete_usage_request(
        client=async_app_client,
        dispenser_id=new_dispenser_id,
        change_status_request=change_status_request,
        open_at=datetime.now(tz=timezone.utc),
        elapsed_seconds=5,
    )

    assert response.status_code == 202


@pytest.mark.anyio
async def test_change_status_dispenser_not_found(
    async_app_client, change_status_request
):
    """
    Prueba un cambio de estado de un dispensador inexistente.

    Args:
        async_app_client (:class:`httpx.AsyncClient`): cliente HTTP asíncrono (DI).
        change_status_request
        (:class:`app.schemas.dispenser.DispenserSpendingLineUpdateIn`):
            Datos con petición de cambio de estado de un dispensador (fixture).
    """
    response = await async_app_client.put(
        f"/api/dispenser/{str(uuid.uuid4())}",
        json=jsonable_encoder(
            change_status_request(
                status=DISPENSER_STATUS_OPEN, when=datetime.now(tz=timezone.utc)
            ),
        ),
    )

    assert response.status_code == 404


@pytest.mark.anyio
async def test_open_dispenser_previously_closed(
    async_app_client,
    valid_new_dispenser_request,
    change_status_request,
):
    """
    Prueba la petición para cerrar un dispensador con un uso ya cerrado.

    Args:
        async_app_client (:class:`httpx.AsyncClient`): cliente HTTP
            asíncrono (DI).
        valid_new_dispenser_request
        (:class:`app.schemas.dispenser.DispenserSpendingLineCreateIn`):
            Datos de inicialización del nuevo dispensador a crear (fixture).
        change_status_request
        (:class:`app.schemas.dispenser.DispenserSpendingLineUpdateIn`):
            Datos con petición de cambio de estado de un dispensador
            (fixture).
    """
    response, dispenser = await do_create_dispenser_request(
        async_app_client, valid_new_dispenser_request
    )

    new_dispenser_id = dispenser.get("id")
    now = datetime.now(tz=timezone.utc)

    response = await do_complete_usage_request(
        client=async_app_client,
        dispenser_id=new_dispenser_id,
        change_status_request=change_status_request,
        open_at=now,
        elapsed_seconds=5,
    )

    # Tratamos de cerrar 10 segundos después el dispensador ya cerrado previamente
    response = await async_app_client.put(
        f"/api/dispenser/{new_dispenser_id}",
        json=jsonable_encoder(
            change_status_request(
                status=DISPENSER_STATUS_CLOSE, when=now + timedelta(seconds=10)
            ),
        ),
    )

    assert response.status_code == 409
