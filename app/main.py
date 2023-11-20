from fastapi import FastAPI

from app.core import database  # noqa
from app.core.api import api_router
from app.core.db import Base, engine

app = FastAPI()

app.include_router(api_router, prefix="/api")

Base.metadata.create_all(bind=engine)
