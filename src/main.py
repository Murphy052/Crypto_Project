from fastapi import FastAPI, Request
from contextlib import asynccontextmanager

from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.staticfiles import StaticFiles

from src.api import routes
from src.client.render import router as render
from src.db import db
from src.core.middleware import AuthBackend
from src.db.repositories import user_repository


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    db.close()


app = FastAPI(lifespan=lifespan)

app.add_middleware(AuthenticationMiddleware, backend=AuthBackend())

app.mount("/static", StaticFiles(directory="src/client/static"), name="static")


@app.get("/")
def get_main(request: Request):
    return str(request.user)


@app.get("/user")
async def get_user():
    return user_repository.create_user()


app.include_router(routes)
app.include_router(render)
