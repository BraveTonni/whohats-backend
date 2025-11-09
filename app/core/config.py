from pydantic_settings import BaseSettings


class Settings(BaseSettings):  # pylint: disable=invalid-name
    """Класс базовой конфигурации"""
    APP_NAME: str = "WhoHats"
