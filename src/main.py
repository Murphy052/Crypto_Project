from fastapi import FastAPI, Request
from contextlib import asynccontextmanager

from starlette.middleware.authentication import AuthenticationMiddleware

from src.api import routes
from src.db import db
from src.core.middleware import AuthBackend
from src.db.repositories import user_repository


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    db.close()


app = FastAPI(lifespan=lifespan)

app.add_middleware(AuthenticationMiddleware, backend=AuthBackend())


@app.get("/")
def get_main(request: Request):
    return str(request.user)


@app.get("/user")
async def get_user():
    return user_repository.create_user()


app.include_router(routes)
