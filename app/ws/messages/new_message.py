import html

from .base import MessageHandler

from app.schemas.ws import WSConnection
from app.ws.connection_manager import WSConnectionManager

from app.core.ws_manager import ws_manager


class NewMessageHandler(MessageHandler):
    def __init__(self, connection: WSConnection, manager: WSConnectionManager):
        super().__init__(connection, manager)

    async def handle(self, content: dict) -> None:
        message = html.escape(content.get("params", {}).get("content")).strip()

        if not message:
            return

        # Длина ограничена до 1024 символов
        if len(message) > 1024:
            message = message[:1024]

        # Получаем собеседника
        partner_id = await ws_manager.get_chat(self.connection.user_id)
        partner = ws_manager.active_connections.get(partner_id)

        await partner.websocket.send_json(
            {
                "type": "message",
                "params": {
                    "content": message,
                    "self": False
                }
            }
        )

        await self.connection.websocket.send_json(
            {
                "type": "message",
                "params": {
                    "content": message,
                    "self": True
                }
            }
        )
