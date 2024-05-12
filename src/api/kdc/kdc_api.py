from fastapi import APIRouter, Request

from src.core.middleware import auth_required
from src.core.tools import rsa, RSA
from src.db.repositories import public_keys_repository
from src.schemas import PublicKeySchema

router = APIRouter(prefix="/kdc")


@router.get("/public-key")
def get_public_key():
    return PublicKeySchema(public_key_exp=rsa.public_key[0], public_key_n=str(rsa.public_key[1]))


@router.get("/public-key/{user}")
@auth_required
async def get_user_public_key(user: str, request: Request):
    print(user)
    keys = public_keys_repository.get_keys_pair_by_username(username=user)
    print(keys)
    msg = f"{keys}:{user}"
    print(msg)
    return f"{RSA.encrypt_with_key(msg, rsa.private_key, 128)}"
