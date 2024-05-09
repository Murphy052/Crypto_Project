from contractsPY import if_fails, Usecase
from datetime import datetime
import jwt
from passlib.context import CryptContext

from src.core import settings
from src.db.repositories import user_repository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


@if_fails(message="Incorrect username or password")
def authenticate_user(state):
    state.user = user_repository.get_user(username=state.username)
    print(state.user)
    if not state.user:
        return None
    if not verify_password(state.password, state.user.password):
        return None
    return True if state.user else False


@if_fails(message="Login error")
def create_access_token(state):
    expire = datetime.utcnow() + settings.ACCESS_TOKEN_LIFETIME

    to_encode = {
        "sub": state.username,
        "exp": expire,
    }

    state.access_token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return True


user_login_usecase = Usecase()
user_login_usecase.contract = [
    authenticate_user,
    create_access_token
]
