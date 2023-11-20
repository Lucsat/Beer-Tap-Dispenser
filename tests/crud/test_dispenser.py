"""Prueba las acciones relacionadas con los dispensadores."""
from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest

from app.crud import dispenser
from app.crud.exception.dispenser_already_opened_closed_exception import (
    DispenserAlreadyOpenedClosedException,
)
from app.crud.exception.dispenser_not_found_exception import DispenserNotFoundException
from app.schemas.dispenser import DISPENSER_STATUS_CLOSE, DISPENSER_STATUS_OPEN
from tests.crudutils import (
    do_complete_dispenser_usage_requests,
    do_create_dispenser_request,
)


@pytest.mark.asyncio
async def test_create_dispenser(db_session, valid_new_dispenser_request):
    """
    Prueba la creación de un dispensador.

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

    assert UUID(db_new_dispenser.reference, version=4)
    assert db_new_dispenser.flow_volume == valid_new_dispenser_request.flow_volume


@pytest.mark.asyncio
async def test_find_dispenser_by_reference(db_session, valid_new_dispenser_request):
    """
    Prueba la búsqueda de un dispensador a través de una referencia existente.

    Args:
        db_session (:class:`app.core.db.SessionLocal`): sesión local de
            acceso a la base de datos.
        valid_new_dispenser_request
        (:class:`app.schemas.dispenser.DispenserSpendingLineCreateIn`):
            Datos de inicialización de un nuevo dispensador a crear (fixture),
            para poder localizarlo mediante su referencia.
    """
    db_new_dispenser = await do_create_dispenser_request(
        db_session,
        valid_new_dispenser_request,
    )

    db_dispenser_by_ref = await dispenser.get_by_reference(
        db_session=db_session, reference=db_new_dispenser.reference
    )

    assert db_new_dispenser.id == db_dispenser_by_ref.id


@pytest.mark.asyncio
async def test_open_new_dispenser(
    db_session, valid_new_dispenser_request, change_status_request
):
    """
    Prueba el cambio de estado de un dispensador recién creado.

    Args:
        db_session (:class:`app.core.db.SessionLocal`): sesión local de
            acceso a la base de datos.
        valid_new_dispenser_request
        (:class:`app.schemas.dispenser.DispenserSpendingLineCreateIn`):
            Datos de inicialización de un nuevo dispensador a crear
            (fixture), para poder localizarlo mediante su referencia.
        change_status_request
            (:class:`app.schemas.dispenser.DispenserSpendingLineUpdateIn`):
            Datos para realizar el cambio de estado del dispensador.
    """
    db_new_dispenser = await do_create_dispenser_request(
        db_session,
        valid_new_dispenser_request,
    )

    try:
        await dispenser.change_status(
            db_session=db_session,
            reference=db_new_dispenser.reference,
            request=change_status_request(
                status=DISPENSER_STATUS_OPEN,
                when=datetime.now(tz=timezone.utc) + timedelta(seconds=5),
            ),
        )
    except Exception as e:
        pytest.fail(f"Excepción no esperada... {e}")


@pytest.mark.asyncio
async def test_dispenser_not_found(db_session, unknown_dispenser_request):
    """
    Prueba la búsqueda de un dispensador no existente.

    Args:
        db_session (:class:`app.core.db.SessionLocal`): sesión local de
            acceso a la base de datos.
    """
    unknown_reference, request = unknown_dispenser_request

    try:
        await dispenser.change_status(
            db_session=db_session,
            reference=unknown_reference,
            request=request,
        )
        pytest.fail("Excepción de control no lanzada...")
    except DispenserNotFoundException:
        assert True


@pytest.mark.asyncio
async def test_close_new_dispenser(
    db_session, valid_new_dispenser_request, change_status_request
):
    """
    Prueba la petición de cerrar un dispensador recién creado (y por lo
    tanto, cerrado)

    Args:
        db_session (:class:`app.core.db.SessionLocal`): sesión local de
            acceso a la base de datos.
        valid_new_dispenser_request
            (:class:`app.schemas.dispenser.DispenserSpendingLineCreateIn`):
            Datos de inicialización de un nuevo dispensador a crear (fixture),
            para poder localizarlo mediante su referencia.
        change_status_request
        (:class:`app.schemas.dispenser.DispenserSpendingLineUpdateIn`):
            Datos para realizar el cambio de estado del dispensador.
    """
    db_new_dispenser = await do_create_dispenser_request(
        db_session,
        valid_new_dispenser_request,
    )

    try:
        await dispenser.change_status(
            db_session=db_session,
            reference=db_new_dispenser.reference,
            request=change_status_request(
                status=DISPENSER_STATUS_CLOSE,
                when=datetime.now(tz=timezone.utc) + timedelta(seconds=5),
            ),
        )
        pytest.fail("Excepción de control no lanzada...")
    except DispenserAlreadyOpenedClosedException:
        assert True


@pytest.mark.asyncio
async def test_open_dispenser_previously_closed(
    db_session,
    valid_new_dispenser_request,
    change_status_request,
):
    """
    Prueba la apertura de un dispensador previamente cerrado.

    Args:
        db_session (:class:`app.core.db.SessionLocal`): sesión local de
            acceso a la base de datos.
        valid_new_dispenser_request
        (:class:`app.schemas.dispenser.DispenserSpendingLineCreateIn`):
            Datos de inicialización de un nuevo dispensador a crear (fixture),
            para poder localizarlo mediante su referencia.
        change_status_request
        (:class:`app.schemas.dispenser.DispenserSpendingLineUpdateIn`):
            Datos para realizar el cambio de estado del dispensador.
    """
    db_new_dispenser = await do_create_dispenser_request(
        db_session,
        valid_new_dispenser_request,
    )

    now = datetime.now(tz=timezone.utc)

    await do_complete_dispenser_usage_requests(
        db_session=db_session,
        db_dispenser=db_new_dispenser,
        change_status_request=change_status_request,
        open_at=now,
        elapsed_seconds=5,
    )

    # Segunda petición de apertura, en un dispensador que ya tiene un uso anterior
    try:
        await dispenser.change_status(
            db_session=db_session,
            reference=db_new_dispenser.reference,
            request=change_status_request(
                status=DISPENSER_STATUS_OPEN,
                when=now + timedelta(seconds=10),
            ),
        )
    except Exception as e:
        pytest.fail(f"Excepción no esperada... {e}")


@pytest.mark.asyncio
async def test_close_already_closed_dispenser_with_previous_usages(
    db_session,
    valid_new_dispenser_request,
    change_status_request,
):
    """
    Prueba la petición de cierre de un dispensador el cual ya se había
    utilizado previamente.

    Args:
        db_session (:class:`app.core.db.SessionLocal`): sesión local de
            acceso a la base de datos.
        valid_new_dispenser_request
        (:class:`app.schemas.dispenser.DispenserSpendingLineCreateIn`):
            Datos de inicialización de un nuevo dispensador a crear (fixture),
            para poder localizarlo mediante su referencia.
        change_status_request
        (:class:`app.schemas.dispenser.DispenserSpendingLineUpdateIn`):
            Datos para realizar el cambio de estado del dispensador.
    """
    db_new_dispenser = await do_create_dispenser_request(
        db_session,
        valid_new_dispenser_request,
    )

    now = datetime.now(tz=timezone.utc)

    await do_complete_dispenser_usage_requests(
        db_session=db_session,
        db_dispenser=db_new_dispenser,
        change_status_request=change_status_request,
        open_at=now,
        elapsed_seconds=5,
    )

    # Volvemos a pedir cerrar el dispensador (que ya tiene un uso anterior,
    # y está cerrado)
    try:
        await dispenser.change_status(
            db_session=db_session,
            reference=db_new_dispenser.reference,
            request=change_status_request(
                status=DISPENSER_STATUS_CLOSE,
                when=now + timedelta(seconds=10),
            ),
        )
        pytest.fail("Excepción de control no lanzada...")
    except DispenserAlreadyOpenedClosedException:
        assert True
