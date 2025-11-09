from fastapi.websockets import WebSocketState, WebSocketDisconnect

from app.schemas.ws import WSConnection, WSState


class WSConnectionManager:
    """WS Connection manager"""
    def __init__(self):
        self.active_connections: dict[str, WSConnection] = {}

        self.__chats: dict[str, str] = {}

    async def connect(self, connection: WSConnection) -> bool:
        """Установка соединения с пользователем"""
        await connection.websocket.accept()

        if self.active_connections.get(connection.user_id):
            await connection.websocket.send_json({"type": "already_connected"})
            await connection.websocket.close()
            
            return False

        self.active_connections[connection.user_id] = connection

        await connection.websocket.send_json(
            {
                "type": "me",
                "params": {
                    "my_id": connection.user_id
                }
            }
        )

        await self.__notify_stats()
        return True

    async def disconnect(self, connection: WSConnection) -> None:
        """Отключение соединения с пользователем"""
        # Отключаем комнату, если есть
        partner_id = self.__chats.get(connection.user_id)
        partner = self.active_connections.get(partner_id)
        print(f"отключение {connection.user_id}")

        if self.active_connections.get(connection.user_id):
            self.active_connections.pop(connection.user_id)

        if partner and partner.status == WSState.CHATTING:
            try:
                await partner.websocket.send_json({"type": "end"})
            except (RuntimeError, WebSocketDisconnect):
                pass
                
            partner.status = WSState.READY

        if not connection.websocket.client_state == WebSocketState.DISCONNECTED:  # noqa: E501
            await connection.websocket.close()

        self.__chats.pop(connection.user_id, None)

        if partner:
            self.__chats.pop(partner.user_id, None)

        await self.__notify_stats()

    async def broadcast(self, content: dict) -> None:
        """Метод оповещения сообщения всем пользователям"""
        for connection in list(self.active_connections.values()):
            try:
                await connection.websocket.send_json(content)
            except Exception:
                continue

    async def get_finding_connections(self) -> list[WSConnection]:
        """Возвращает список соединений, находящихся в режиме поиска."""
        return [
            conn for conn in self.active_connections.values()
            if conn.status == WSState.FINDING
        ]

    async def add_chat(self, from_uuid: str, to_uuid: str):
        self.__chats[from_uuid] = to_uuid
        self.__chats[to_uuid] = from_uuid

    async def remove_chat(self, from_uuid: str, to_uuid: str):
        self.__chats.pop(from_uuid, None)
        self.__chats.pop(to_uuid, None)

    async def get_chat(self, uuid: str) -> str:
        return self.__chats.get(uuid)

    async def __notify_stats(self) -> None:
        """Метод для оповещения статистики у пользователей"""
        content = {
            "type": "stats",
            "params": {
                "online": len(self.active_connections)
            }
        }

        await self.broadcast(content)
