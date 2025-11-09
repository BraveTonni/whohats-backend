from .base import MessageHandler

from app.schemas.ws import WSConnection
from app.ws.connection_manager import WSConnectionManager

from app.core.ws_manager import ws_manager


class WebRTCSignalHandler(MessageHandler):
    def __init__(self, connection: WSConnection, manager: WSConnectionManager):
        super().__init__(connection, manager)

    async def handle(self, content: dict) -> None:
        params = content.get("params", {})

        if not params:
            return

        # Получаем собеседника
        partner_id = await ws_manager.get_chat(self.connection.user_id)
        partner = ws_manager.active_connections.get(partner_id)

        if not partner:
            return

        print(f"От: {self.connection.user_id} -> {content}")

        # Обработка разных типов сообщений
        if params.get("action") == "call_request":
            # Отправляем запрос на звонок
            await partner.websocket.send_json({
                "type": "webrtc",
                "params": {
                    "action": "incoming_call_request",
                }
            })
        elif params.get("action") == "call_accept":
            await partner.websocket.send_json({
                "type": "webrtc",
                "params": {
                    "action": "call_accept",
                }
            })
        elif params.get("action") == "call_decline":
            await partner.websocket.send_json({
                "type": "webrtc",
                "params": {
                    "action": "call_decline",
                }
            })
        elif params.get("action") == "call_end":
            await partner.websocket.send_json({
                "type": "webrtc",
                "params": {
                    "action": "call_end",
                }
            })

        else:
            # Пересылаем стандартные WebRTC сигналы (offer, answer, candidate)
            await partner.websocket.send_json({
                "type": "webrtc",
                "params": params
            })
