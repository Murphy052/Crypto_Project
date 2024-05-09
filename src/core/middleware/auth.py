from fastapi import Request, HTTPException, status
from starlette.authentication import AuthenticationBackend, AuthenticationError, UnauthenticatedUser
from functools import wraps

import jwt

from src.core import settings
from src.db.repositories import user_repository


class AuthBackend(AuthenticationBackend):
    """
    This is a custom auth backend class that will allow you to authenticate your request and return auth and user as
    a tuple
    """
    async def authenticate(self, request):
        # This function is inherited from the base class and called by some other class
        auth = request.cookies.get("authorization") or request.headers.get("authorization")
        if auth is None:
            return

        try:
            scheme, token = auth.split()
            if scheme.lower() != 'bearer':
                return
            decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except Exception as exc:
            raise AuthenticationError('Invalid JWT Token.')

        username: str = decoded.get("sub")

        user = user_repository.get_user(username=username)
        if user is None:
            raise AuthenticationError('Invalid JWT Token.')

        return auth, user


def auth_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request: Request = kwargs.get("request")
        if not request:
            raise HTTPException(status_code=400)

        user = request.user

        if isinstance(user, UnauthenticatedUser):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        return await func(*args, **kwargs)

    return wrapper
