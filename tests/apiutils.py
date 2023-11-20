"""Conjunto de utilidades para la realización de testa a nivel de API."""


from datetime import datetime, timedelta

from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient, Response

from app.schemas.dispenser import DISPENSER_STATUS_CLOSE, DISPENSER_STATUS_OPEN


async def do_create_dispenser_request(
    async_app_client, valid_new_dispenser_request
) -> tuple:
    """
    Realiza la petición para crear un nuevo dispensador.

    Args:
        async_app_client (:class:`httpx.AsyncClient`): cliente HTTP asíncrono
            (DI).
        valid_new_dispenser_request
        (:class:`app.schemas.dispenser.DispenserSpendingLineCreateIn`):
            Datos de inicialización del nuevo dispensador a crear (fixture).

    Returns:
        Una tupla que contiene la respuesta de la API, así como el json con los
        datos del dispensador.
    """
    response = await async_app_client.post(
        "/api/dispenser/",
        json=jsonable_encoder(valid_new_dispenser_request),
    )
    dispenser = response.json()

    return response, dispenser


async def do_complete_usage_request(
    client: AsyncClient,
    dispenser_id: str,
    change_status_request,
    open_at: datetime,
    elapsed_seconds: int,
) -> Response:
    """
    Realiza la petición de creación de un dispensador, y las llamadas para
    registrar un uso de este (abrir y cerrar tras unos segundos).

    Args:
        client (:class:`httpx.AsyncClient`): cliente HTTP asíncrono (DI).
        dispenser_id (str): Identificador público del dispensador.
        change_status_request
        (:class:`app.schemas.dispenser.DispenserSpendingLineUpdateIn`):
            Datos con petición de cambio de estado del dispensador (fixture).
        open_at (datetime): Fecha y hora de la petición de apertura del
            dispensador.
        elapsed_seconds (int): Segundos a transcurrir entre la apertura y el
            cierre del dispensador.

    Returns:
        La respuesta de la API a la petición de cierre del dispensador.
    """
    response = await client.put(
        f"/api/dispenser/{dispenser_id}",
        json=jsonable_encoder(
            change_status_request(status=DISPENSER_STATUS_OPEN, when=open_at),
        ),
    )

    response = await client.put(
        f"/api/dispenser/{dispenser_id}",
        json=jsonable_encoder(
            change_status_request(
                status=DISPENSER_STATUS_CLOSE,
                when=open_at + timedelta(seconds=elapsed_seconds),
            )
        ),
    )

    return response
