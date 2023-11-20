from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.crud import dispenser
from app.crud.exception.dispenser_already_opened_closed_exception import (
    DispenserAlreadyOpenedClosedException,
)
from app.crud.exception.dispenser_not_found_exception import DispenserNotFoundException
from app.schemas.dispenser import (
    DispenserSpendingLineCreateIn,
    DispenserSpendingLineCreateOut,
    DispenserSpendingLineUpdateIn,
)

router = APIRouter()


@router.post(
    "/",
    summary="Crea un nuevo dispensador.",
    response_description="Dispensador creado correctamente.",
    response_model=DispenserSpendingLineCreateOut,
)
async def create(
    dispense_in: DispenserSpendingLineCreateIn, db_session: Session = Depends(get_db)
):
    db_dispenser = await dispenser.create(db_session=db_session, dispenser=dispense_in)

    return DispenserSpendingLineCreateOut(
        id=db_dispenser.reference, flow_volume=db_dispenser.flow_volume
    )


@router.put(
    "/{id}",
    summary="Actualiza el estado de un dispensador.",
    response_description="Estado del dispensador actualizado.",
    status_code=202,
)
async def change_status(
    id: Annotated[
        str,
        Path(
            title="El identificador del dispensador a actualizar.",
            pattern=r"^[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}$",
        ),
    ],
    status_in: DispenserSpendingLineUpdateIn,
    db_session: Session = Depends(get_db),
):
    try:
        await dispenser.change_status(
            db_session=db_session, reference=id, request=status_in
        )
    except DispenserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DispenserAlreadyOpenedClosedException as e:
        raise HTTPException(status_code=409, detail=str(e))
