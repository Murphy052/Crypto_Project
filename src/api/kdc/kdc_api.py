from fastapi import APIRouter, Request

from src.core.middleware import auth_required
from src.core.tools import rsa, RSA
from src.db.repositories import public_keys_repository
from src.schemas import PublicKeysResponseSchema

router = APIRouter(prefix="/kdc")


@router.get("/public-key")
def get_public_key():
    return PublicKeysResponseSchema(public_key_exp=rsa.public_key[0], public_key_n=str(rsa.public_key[1]))  


@router.get("/public-key/{user}")
@auth_required
async def get_user_public_key(user: str, request: Request):
    keys = public_keys_repository.get_keys_pair_by_username(username=user)
    msg = f"{keys}:{user}"
    return f"{RSA.encrypt_with_key(msg, rsa.private_key)}"
