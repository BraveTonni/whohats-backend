import orjson
import logging

from app.schemas.ws import WSConnection

from app.ws.messages import (
    StartSearchHandler, NewMessageHandler, EndChatHandler,
    WebRTCSignalHandler
)
from app.ws.connection_manager import WSConnectionManager


class WSMessageHandler:
    """Class for processing websocket message"""
    def __init__(self, connection: WSConnection, manager: WSConnectionManager):
        self.connection = connection
        self.manager = manager

        self.message_handlers = {
            'start_search': StartSearchHandler(self.connection, self.manager),
            'new_message': NewMessageHandler(self.connection, self.manager),
            'end': EndChatHandler(self.connection, self.manager),
            'webrtc': WebRTCSignalHandler(self.connection, self.manager)
        }

        self.__logger = logging.getLogger(__name__)

    async def process_message(self, message: str) -> None:
        """Process message"""
        content = orjson.loads(message)
        message_type = content.get("type")

        message_handler = self.message_handlers.get(message_type)

        if not message_handler:
            self.__logger.info(
                f"Получен неизвестный тип сообщения: {message_type}"
            )
            return

        await message_handler.handle(content)
