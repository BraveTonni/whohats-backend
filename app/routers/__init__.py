from fastapi import FastAPI

from app.routers.api import register_api_routers


def register_routers(app: FastAPI) -> None:
    """Метод для регистрации всех роутеров"""
    register_api_routers(app)