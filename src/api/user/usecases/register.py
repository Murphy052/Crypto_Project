import re
from contractsPY import Usecase, if_fails
from passlib.context import CryptContext

from src.db.repositories import user_repository
from src.schemas.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@if_fails(message="Username is invalid or used by someone")
def validate_username(state):
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    if not re.match(pattern, state.username):
        return False

    user = user_repository.get_user(state.username)

    return False if user else True


@if_fails(message="Cannot create user")
def create_user(state):
    try:
        state.user = user_repository.create(
            User(
                username=state.username,
                password=pwd_context.hash(state.password),
            )
        )
    except:
        return False
    return True if state.user else False


register_usecase = Usecase()
register_usecase.contract = [
    validate_username,
    create_user,
]
