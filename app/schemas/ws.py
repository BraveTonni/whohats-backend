from typing import Optional

from enum import IntEnum, auto

from dataclasses import dataclass, field

from fastapi import WebSocket

from .search_params import SearchParams


class WSState(IntEnum):
    READY = auto()
    FINDING = auto()
    CHATTING = auto()


@dataclass
class WSConnection:
    websocket: WebSocket
    user_id: str

    status: WSState = field(default=WSState.READY)

    search_params: Optional[SearchParams] = None

    partner: Optional["WSConnection"] = None
