import uuid
from datetime import datetime, timezone
from typing import Final, Union

import pytest
from httpx import AsyncClient

from app.core.db import Base, SessionLocal, engine
from app.main import app
from app.schemas.dispenser import (
    DISPENSER_STATUS_CLOSE,
    DISPENSER_STATUS_OPEN,
    DispenserSpendingLineCreateIn,
    DispenserSpendingLineIn,
    DispenserSpendingLineUpdateIn,
)

DEFAULT_FLOW_VOLUME: Final[float] = 0.0653


@pytest.fixture
async def async_app_client():
    async with AsyncClient(app=app, base_url="http://localhost") as client:
        yield client


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(engine)
    session = SessionLocal()

    yield session

    session.rollback()
    session.close()


@pytest.fixture(scope="module")
def valid_new_dispenser_request():
    return DispenserSpendingLineCreateIn(flow_volume=DEFAULT_FLOW_VOLUME)


@pytest.fixture(scope="module")
def unknown_dispenser_request():
    return (str(uuid.uuid4()), DispenserSpendingLineIn())


@pytest.fixture(scope="module")
def change_status_request():
    def _method(
        status: Union[DISPENSER_STATUS_OPEN, DISPENSER_STATUS_CLOSE],
        when: datetime = datetime.now(tz=timezone.utc),
    ):
        return DispenserSpendingLineUpdateIn(status=status, updated_at=when)

    return _method
