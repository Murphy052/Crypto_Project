from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from src.core.middleware import auth_required
from src.db.repositories import user_repository

templates = Jinja2Templates(directory="src/client/templates")

router = APIRouter()


@router.get("/board")
@auth_required
async def render_board(request: Request):
    texts_data = user_repository.get_all()

    print(texts_data)
    return templates.TemplateResponse("board.html", {"request": request})


@router.get("/login")
async def render_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})
