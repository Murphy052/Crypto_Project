from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from src.core.middleware import auth_required
from src.schemas.user import User
from src.api.kdc.websocket import manager

templates = Jinja2Templates(directory="src/client/templates")

router = APIRouter()


@router.get("/")
async def get_main(request: Request):
    if isinstance(request.user, User):
        return RedirectResponse(url="/board")
    return RedirectResponse(url="/login")


@router.get("/board")
@auth_required
async def render_board(request: Request):
    users_data = [conn.user.__dict__ for conn in manager.active_connections]

    return templates.TemplateResponse(
        "board.html", {"request": request, "data": users_data, "mson": '{"method": "user_conn", '+'"payload": "'+request.user.username+'"}', "username": {request.user.username}}
    )


@router.get("/login")
async def render_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/chat")
@auth_required
async def render_chat(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})
