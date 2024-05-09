from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.staticfiles import StaticFiles

from contextlib import asynccontextmanager

from src.api import routes
from src.client.render import router as render
from src.core import settings
from src.core.tools import RSA
from src.db import db
from src.core.middleware import AuthBackend
from src.schemas.user import User


@asynccontextmanager
async def lifespan(app: FastAPI):
    # app.rsa = RSA(1024)
    yield
    db.close()


app = FastAPI(lifespan=lifespan)

app.add_middleware(AuthenticationMiddleware, backend=AuthBackend())
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="src/client/static"), name="static")


@app.get("/")
def get_main(request: Request):
    if isinstance(request.user, User):
        return RedirectResponse(url="/board")
    return RedirectResponse(url="/login")


# @app.get("/public-key")
# def get_public_key():
#     print(app.rsa.public_key)
#     return str(app.rsa.public_key[0]), str(app.rsa.public_key[1])


app.include_router(routes, tags=["api"])
app.include_router(render, tags=["client"])
