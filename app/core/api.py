from fastapi import APIRouter

from app.api import dispenser_commands, dispenser_queries


api_router = APIRouter()

api_router.include_router(
    dispenser_commands.router, prefix="/dispenser", tags=["Dispensador"]
)
api_router.include_router(
    dispenser_queries.router, prefix="/dispenser", tags=["Dispensador"]
)
