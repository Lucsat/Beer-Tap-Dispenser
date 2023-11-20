"""Conjunto de utilides para la realización de tests a nivel de CRUD."""
from datetime import datetime, timedelta

from app.crud import dispenser
from app.models.dispenser import DispenserSpendingLine
from app.schemas.dispenser import DISPENSER_STATUS_CLOSE, DISPENSER_STATUS_OPEN


async def do_create_dispenser_request(
    db_session,
    valid_new_dispenser_request,
) -> DispenserSpendingLine:
    """
    Devuelve un nuevo dispensador, en el cual se ha realizado un uso
    completo (abrir y cerrar).

    Args:
        db_session (:class:`app.core.db.SessionLocal`): sesión local de
            acceso a la base de datos.
        valid_new_dispenser_request
        (:class:`app.schemas.dispenser.DispenserSpendingLineCreateIn`):
            Datos de inicialización de un nuevo dispensador a crear
            (fixture), para poder localizarlo mediante su referencia.
    """
    db_new_dispenser = await dispenser.create(
        db_session=db_session, dispenser=valid_new_dispenser_request
    )

    return db_new_dispenser


async def do_complete_dispenser_usage_requests(
    db_session,
    db_dispenser: DispenserSpendingLine,
    change_status_request,
    open_at: datetime,
    elapsed_seconds: int,
):
    """
    Realiza la petición de creación de un dispensador, y las llamadas para
    registrar un uso de este (abrir y cerrar tras unos segundos).

    Args:
        db_session (:class:`app.core.db.SessionLocal`): sesión local de
            acceso a la base de datos.
        db_dispenser_id (:class:`app.models.dispenser.DispenserSpendingLine`):
            Objeto con los datos del dispensador extraídos de la base de datos.
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
    await dispenser.change_status(
        db_session=db_session,
        reference=db_dispenser.reference,
        request=change_status_request(status=DISPENSER_STATUS_OPEN, when=open_at),
    )

    await dispenser.change_status(
        db_session=db_session,
        reference=db_dispenser.reference,
        request=change_status_request(
            status=DISPENSER_STATUS_CLOSE,
            when=open_at + timedelta(seconds=elapsed_seconds),
        ),
    )
