import uuid

from fastapi import WebSocket, WebSocketDisconnect, Query

from fastapi.routing import APIRouter

from app.ws.message_handler import WSMessageHandler
from app.schemas.ws import WSConnection
from app.core.ws_manager import ws_manager

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str = Query(None)
) -> None:
    """Websocket connect endpoint"""
    if not user_id:
        user_id = str(uuid.uuid4())

    connection = WSConnection(
        websocket=websocket,
        user_id=user_id
    )

    is_connected = await ws_manager.connect(connection)

    if not is_connected:
        return

    handler = WSMessageHandler(connection, ws_manager)

    try:
        while True:
            message = await websocket.receive_text()

            await handler.process_message(
                message=message
            )
    except WebSocketDisconnect:
        await ws_manager.disconnect(connection)
