import uuid
from datetime import datetime
from typing import List

from sqlalchemy.orm import Session

from app.crud.exception.dispenser_already_opened_closed_exception import (
    DispenserAlreadyOpenedClosedException,
)
from app.crud.exception.dispenser_not_found_exception import DispenserNotFoundException
from app.models.dispenser import DispenserSpendingLine
from app.models.usage import Usage
from app.schemas.dispenser import (
    DISPENSER_STATUS_CLOSE,
    DISPENSER_STATUS_OPEN,
    DispenserSpendingLineCreateIn,
    DispenserSpendingLineUpdateIn,
)


async def create(
    db_session: Session, dispenser: DispenserSpendingLineCreateIn
) -> DispenserSpendingLine:
    """
    Crea una nueva línea para dispensar cerveza.

    Args:
        db_session (:class:`sqlalchemy.orm.Session`): instancia de la sesión
            local de acceso a la base de datos.
        dispenser (:class:`app.schemas.dispenser.DispenserSpendingLineCreateIn`):
            objeto con los datos de petición a la API para la creación de la línea.

    Returns:
        Instancia del modelo :class:`~app.models.dispenser.DispenserSpendingLine`
            con los datos del nuevo registro creado en la base de datos.
    """
    reference_uuid = str(uuid.uuid4())

    db_dispenser = DispenserSpendingLine(
        reference=reference_uuid, flow_volume=dispenser.flow_volume
    )

    db_session.add(db_dispenser)
    db_session.commit()
    db_session.refresh(db_dispenser)

    return db_dispenser


async def get_by_reference(
    db_session: Session, reference: str
) -> DispenserSpendingLine | None:
    """
    Devuelve un dispensador a través de su referencia pública (UUID).

    Args:
        db_session (:class:`sqlalchemy.orm.Session`): instancia de la sesión
            local de acceso a la base de datos.
        reference (str): Identificador (UUID) del dispensador a localizar.

    Returns:
        Instancia del modelo :class:`~app.models.dispenser.DispenserSpendingLine`
            con los datos del nuevo registro creado en la base de datos.
    """
    return (
        db_session.query(DispenserSpendingLine)
        .filter(DispenserSpendingLine.reference == reference)
        .first()
    )


async def change_status(
    db_session: Session, reference: str, request: DispenserSpendingLineUpdateIn
) -> None:
    """
    Cambia el estado (abierto/cerrado) en un dispensador.

    Args:
        db_session (:class:`sqlalchemy.orm.Session`): instancia de la sesión
            local de acceso a la base de datos.
        reference (str): Identificador (UUID) del dispensador a localizar.
        request (:class:`app.schemas.dispenser.DispenserSpendingLineUpdateIn`):
            objeto con los datos de actualización del dispensador.
    """
    db_dispenser = await get_by_reference(db_session=db_session, reference=reference)

    if db_dispenser is None:
        raise DispenserNotFoundException(
            f"No se ha encontrado el dispensador con referencia {reference}"
        )

    if not __check_request_consistency(dispenser=db_dispenser, status=request.status):
        raise DispenserAlreadyOpenedClosedException(
            f"No se ha encontrado el dispensador con referencia {reference}"
        )

    db_usage = __handle_dispender_usage(
        dispenser_id=db_dispenser.id,
        when=request.updated_at,
        usages=db_dispenser.usages,
    )

    db_session.add(db_usage)
    db_session.commit()
    db_session.refresh(db_usage)


def __check_request_consistency(dispenser: DispenserSpendingLine, status: str) -> bool:
    """
    Comprueba si se está tratando de realizar un cambio de estado coherente en el
    dispensador, teniendo en cuenta el estado actual en el que se encuentra.

    Args:
        dispenser (:class:`~app.models.dispenser.DispenserSpendingLine`): dispensador
            extraído de la base de datos con el estado actual.
        status (str): Nuevo estado del dispensador.

    Returns:
        True si se trata de pasar un estado actual "open" a "close", o viceversa, o
        False en caso de tratar de cerrar ("close") un dispensador ya cerrado, o de
        abrir ("open") un dispensador ya abierto.
    """
    request_is_coherente = False

    if len(dispenser.usages) == 0:
        request_is_coherente = True if status == DISPENSER_STATUS_OPEN else False
    else:
        request_is_coherente = (
            True
            if status == __calculate_coherent_dispenser_next_status(dispenser.usages)
            else False
        )

    return request_is_coherente


def __calculate_coherent_dispenser_next_status(
    usages: List[Usage],
) -> str:
    """
    Analiza los usos realizados en un dispensador, y calcula cual debería ser la
    siguiente petición de cambio de su estado.

    Args:
        usages (List[:class:`~app.models.usage.Usage`]): Listado de usos que se
            han realizado en el dispensador.

    Returns:
        :class:`~app.schemas.dispenser.DISPENSER_STATUS_OPEN` si el dispensador
        se encuentra cerrado actualmente, o
        :class:`~app.schemas.dispenser.DISPENSER_STATUS_CLOSE` en caso contrario.
    """
    next_status = DISPENSER_STATUS_OPEN

    if len(usages) > 0 and usages[-1].closed_at is None:
        next_status = DISPENSER_STATUS_CLOSE

    return next_status


def __handle_dispender_usage(
    dispenser_id: int, when: datetime, usages: List[Usage]
) -> Usage:
    """
    Crea un nuevo uso del dispensador, o recupera el último uso, con datos actualizados.

    Args:
        dispenser_id (int): Identificador interno del dispensador.
        when (datetime): Fecha propuesta para registrar el cambio de estado.
        usages (List[:class:`~app.models.usage.Usage`]): Listado de usos que se han
            realizado en el dispensador.

    Returns:
        :class:`~app.schemas.dispenser.DISPENSER_STATUS_OPEN` si el dispensador se
        encuentra cerrado actualmente, o
        :class:`~app.schemas.dispenser.DISPENSER_STATUS_CLOSE` en caso contrario.
    """
    db_usage = None

    if len(usages) == 0:
        db_usage = Usage(opened_at=when, dispenser_id=dispenser_id)
    else:
        db_usage = usages[-1]

        if db_usage.closed_at is None:
            db_usage.closed_at = when
        else:
            db_usage = Usage(opened_at=when, dispenser_id=dispenser_id)

    return db_usage
