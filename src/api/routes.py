from fastapi import APIRouter
from src.api.user.user_api import router as user_router


routes = APIRouter(prefix="/api/v1")

routes.include_router(user_router, prefix="/user")
