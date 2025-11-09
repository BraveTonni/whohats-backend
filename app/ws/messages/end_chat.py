from .base import MessageHandler
from app.schemas.ws import WSConnection
from app.ws.connection_manager import WSConnectionManager

from app.core.ws_manager import ws_manager


class EndChatHandler(MessageHandler):
    def __init__(self, connection: WSConnection, manager: WSConnectionManager):
        super().__init__(connection, manager)

    async def handle(self, content: dict) -> None:
        # Получаем собеседника
        partner_id = await ws_manager.get_chat(self.connection.user_id)
        partner = ws_manager.active_connections.get(partner_id)

        await ws_manager.remove_chat(partner.user_id if partner else -1, self.connection.user_id)

        if partner:
            await partner.websocket.send_json({"type": "end"})

        await self.connection.websocket.send_json({"type": "end"})
