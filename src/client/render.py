from fastapi import APIRouter, Request, WebSocket
from fastapi.websockets import WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from starlette.authentication import UnauthenticatedUser

from src.core.middleware import auth_required
from src.db.repositories import user_repository

templates = Jinja2Templates(directory="src/client/templates")

router = APIRouter()


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

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


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
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{websocket.user.username} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{websocket.user.username} left the chat")


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


@router.get("/board")
@auth_required
async def render_board(request: Request):
    users_data = [conn.user.__dict__ for conn in manager.active_connections]

    print(users_data)
    return templates.TemplateResponse(
        "board.html", {"request": request, "data": users_data}
    )


@router.get("/login")
async def render_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/chat")
async def render_chat(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})
