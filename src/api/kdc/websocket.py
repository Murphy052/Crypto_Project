import json
from dataclasses import dataclass

from fastapi import APIRouter, WebSocket
from fastapi.websockets import WebSocketDisconnect
from starlette.authentication import UnauthenticatedUser

router = APIRouter()


@dataclass
class MSON:
    method: str
    payload: str
    dest: str | None = None


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, black_listed: WebSocket | None = None):
        for connection in self.active_connections:
            if connection is black_listed:
                continue
            await connection.send_text(message)

    def get_connection(self, conn: str) -> WebSocket | None:
        for websocket in self.active_connections:
            if websocket.user.username == conn:
                return websocket
            return None


manager = ConnectionManager()
chat = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    if isinstance(websocket.user, UnauthenticatedUser):
        return

    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(data)
            try:
                s_data = MSON(**(json.loads(data)))
                print([w.user for w in manager.active_connections])
                if s_data.method == "connect":
                    dest: WebSocket = manager.get_connection(s_data.dest)
                    await manager.send_personal_message(data, dest)
                elif s_data.method == "confirm":
                    dest: WebSocket = manager.get_connection(s_data.dest)
                    await manager.send_personal_message(data, dest)
                elif s_data.method == "justify":
                    dest: WebSocket = manager.get_connection(s_data.dest)
                    await manager.send_personal_message(data, dest)
                elif s_data.method == "user_conn":
                    await manager.broadcast(
                        json.dumps(
                            MSON(method="user_conn", payload=f"{websocket.user.username}").__dict__,
                            indent=0
                        ),
                        black_listed=websocket
                    )
            except:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(json.dumps(MSON(method="user_disconn", payload=f"{websocket.user.username}").__dict__, indent=0))


@router.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    if isinstance(websocket.user, UnauthenticatedUser):
        return

    await chat.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await chat.send_personal_message(f"You wrote: {data}", websocket)
            await chat.broadcast(f"Client #{websocket.user.username} says: {data}")
    except WebSocketDisconnect:
        chat.disconnect(websocket)
        await chat.broadcast(f"Client #{websocket.user.username} left the chat")
