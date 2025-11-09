import asyncio
import random
from typing import Optional

from fastapi.websockets import WebSocketState

from .base import MessageHandler
from app.schemas.ws import WSConnection, WSState
from app.schemas.search_params import SearchParams, Gender, Age
from app.ws.connection_manager import WSConnectionManager

from app.core.ws_manager import ws_manager


class StartSearchHandler(MessageHandler):
    def __init__(self, connection: WSConnection, manager: WSConnectionManager):
        super().__init__(connection, manager)
        self._search_task: Optional[asyncio.Task] = None

    async def handle(self, content: dict) -> None:
        # Парсим параметры
        try:
            search_params = self.__parse_search_params(content)
        except Exception as e:
            self._logger.error(f"Ошибка парсинга search_params: {e}")
            return

        # Проверяем, не в поиске ли уже
        if self.connection.status == WSState.FINDING:
            self._logger.info(f"Пользователь {self.connection.user_id} уже в поиске")
            return

        # Устанавливаем параметры и статус
        self.connection.search_params = search_params
        self.connection.status = WSState.FINDING

        self._logger.info(f"Начинаем поиск собеседника для {self.connection.user_id}")

        # Запускаем поиск в фоне
        self._search_task = asyncio.create_task(self._search_loop())
        self._search_task.add_done_callback(self._on_search_done)

    async def _search_loop(self):
        """Основной цикл поиска — НЕ блокирует handle()"""
        try:
            while True:
                # === ПРОВЕРКА СОСТОЯНИЯ ===
                if self.connection.websocket.client_state != WebSocketState.CONNECTED:
                    self._logger.info(f"WebSocket отключён: {self.connection.user_id}")
                    break

                if self.connection.status != WSState.FINDING:
                    self._logger.info(f"Поиск закончен: {self.connection.user_id}")
                    break

                # === ПОИСК ПАРТНЁРА ===
                partner = await self.__get_available_connection()
                if not partner:
                    await asyncio.sleep(1)
                    continue

                # === НАШЛИ! ===
                self._logger.info(f"Пара найдена: {self.connection.user_id} <-> {partner.user_id}")

                await ws_manager.add_chat(
                    from_uuid=self.connection.user_id,
                    to_uuid=partner.user_id
                )

                # Обновляем статусы
                partner.status = WSState.CHATTING
                self.connection.status = WSState.CHATTING

                # Отправляем уведомления
                await self._send_partner_found(to_conn=self.connection, partner_id=partner.user_id)
                await self._send_partner_found(to_conn=partner, partner_id=self.connection.user_id)

                break

        except asyncio.CancelledError:
            self._logger.info(f"Поиск отменён через cancel(): {self.connection.user_id}")
        except Exception as e:
            self._logger.error(f"Ошибка в _search_loop: {e}", exc_info=True)
        finally:
            # Гарантируем сброс статуса
            if self.connection.status == WSState.FINDING:
                self.connection.status = WSState.READY

    def _on_search_done(self, task: asyncio.Task):
        """Колбэк при завершении задачи поиска"""
        if task.cancelled():
            self._logger.info(f"Задача поиска отменена: {self.connection.user_id}")
        elif exc := task.exception():
            self._logger.error(f"Исключение в поиске: {exc}", exc_info=exc)

        self._search_task = None

    # === ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ===

    def __parse_search_params(self, content: dict) -> SearchParams:
        params = content.get("params", {})

        return SearchParams(
            my_gender=Gender(int(params.get("my_gender"))),
            companion_gender=Gender(int(params.get("companion_gender"))),
            my_age=Age(int(params.get("my_age"))),
            companion_age=Age(int(params.get("companion_age"))),
        )

    async def __get_available_connection(self) -> Optional[WSConnection]:
        connections = await self.manager.get_finding_connections()
        if not connections:
            return None

        # Исключаем себя и перемешиваем
        candidates = [c for c in connections if c.user_id != self.connection.user_id]
        random.shuffle(candidates)

        my_params = self.connection.search_params
        for conn in candidates:
            if self.__is_compatible(my_params, conn.search_params):
                return conn

        return None

    def __is_compatible(self, my: SearchParams, their: SearchParams) -> bool:
        return (
            their.companion_gender in (Gender.ANYONE, my.my_gender)
            and my.companion_gender in (Gender.ANYONE, their.my_gender)
            and their.companion_age in (Age.MORE_25, my.my_age)
            and my.companion_age in (Age.MORE_25, their.my_age)
        )

    async def _send_partner_found(self, to_conn: WSConnection, partner_id: str):
        """Безопасная отправка partner_find"""
        try:
            if to_conn.websocket.client_state == WebSocketState.CONNECTED:
                await to_conn.websocket.send_json({
                    "type": "partner_find",
                    "params": {
                        "partner_id": partner_id,
                        "my_id": to_conn.user_id,
                    },
                })
        except Exception as e:
            self._logger.warning(f"Не удалось отправить partner_find для {to_conn.user_id}: {e}")

    # === ОТМЕНА ПОИСКА ===

    def cancel_search(self):
        """Вызывается извне (например, по сообщению cancel_search или при disconnect)"""
        if self.connection.status == WSState.FINDING:
            self.connection.status = WSState.READY
            self._logger.info(f"Поиск принудительно отменён: {self.connection.user_id}")

        if self._search_task and not self._search_task.done():
            self._search_task.cancel()