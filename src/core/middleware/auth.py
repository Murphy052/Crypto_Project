from starlette.authentication import AuthenticationBackend


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
