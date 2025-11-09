import logging

from abc import ABC, abstractmethod

from app.schemas.ws import WSConnection

from app.ws.connection_manager import WSConnectionManager


class MessageHandler(ABC):
    def __init__(self, connection: WSConnection, manager: WSConnectionManager):
        self.connection = connection
        self.manager = manager

        self._logger = logging.getLogger(__name__)

    @abstractmethod
    async def handle(self, content: dict) -> None:
        raise NotImplementedError()
