from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.crud import dispenser
from app.schemas.dispenser import DispenserSpendingLineAggregateOut
from app.services import reports_handler

router = APIRouter()


@router.get(
    "/{id}",
    summary="Crea un nuevo dispensador.",
    response_description="",
    response_model=DispenserSpendingLineAggregateOut,
)
async def get_dispenser_usage_data(
    id: Annotated[
        str,
        Path(
            title="El identificador del dispensador a consultar.",
            pattern=r"^[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}$",
        ),
    ],
    db_session: Session = Depends(get_db),
):
    db_dispenser = await dispenser.get_by_reference(db_session=db_session, reference=id)

    if db_dispenser is None:
        raise HTTPException(
            status_code=404,
            detail=str(f"Dispensador con referencia {id} no encontrado"),
        )

    data = reports_handler.calculate_total_amount_spent(dispenser=db_dispenser)

    return data
