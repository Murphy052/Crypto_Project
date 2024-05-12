from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.staticfiles import StaticFiles

from contextlib import asynccontextmanager

from src.api import routes
from src.client.render import router as render
from src.api.kdc.kdc_api import router as kdc_router
from src.api.kdc.websocket import router as websocket
from src.core import settings
from src.db import db
from src.core.middleware import AuthBackend, auth_required
from src.db.repositories import public_keys_repository, user_repository


@asynccontextmanager
async def lifespan(app: FastAPI):
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


@app.get("/test")
@auth_required
async def test_endpoint(request: Request):
    print(s := public_keys_repository.get_keys_pair_by_username(username="Iguliyev"))
    return s


app.include_router(routes, tags=["api"])
app.include_router(render, tags=["client"])
app.include_router(kdc_router, tags=["kdc"])
app.include_router(websocket)
