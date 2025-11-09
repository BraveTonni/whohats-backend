import uvicorn

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import register_routers

from app.utils.log import setup_logger

from app.core.config import Settings

setup_logger()

settings = Settings()
app = FastAPI(
    title=settings.APP_NAME
)

app.mount("/static", StaticFiles(directory="static"), name="static")

register_routers(app)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
