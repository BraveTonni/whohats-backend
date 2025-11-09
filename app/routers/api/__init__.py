from fastapi import FastAPI

from fastapi.routing import APIRouter

from app.routers.api.websocket import router as ws_router


def register_api_routers(app: FastAPI) -> None:
    """Регистрация роутеров связанных с API"""
    api_router = APIRouter(
        prefix="/api"
    )

    api_router.include_router(ws_router)

    app.include_router(api_router)
