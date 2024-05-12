from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm

from src.api.user.usecases import user_login_usecase, register_usecase
from src.core.middleware import auth_required
from src.db.repositories import public_keys_repository
from src.schemas import TokenSchema, PublicKeySchema, PublicKeys

router = APIRouter()


@router.post("/login", response_model=TokenSchema)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> TokenSchema:
    result = user_login_usecase.apply(
        username=form_data.username,
        password=form_data.password,
    )
    if result.case == "success":
        return TokenSchema(access_token=result.state.access_token, token_type="bearer")

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=result.message,
        headers={"authorization": "Bearer"},
    )


@router.post("/register")
async def register(data: OAuth2PasswordRequestForm = Depends()):
    result = register_usecase.apply(
        username=data.username,
        password=data.password,
    )

    if result == "success":
        return "Success"

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=result.message,
    )


@router.post("/public-key")
@auth_required
async def post_public_key(item: PublicKeySchema, request: Request):
    public_keys_repository.create(
        PublicKeys(
            public_key_exp=item.public_key_exp,
            public_key_n=item.public_key_n,
            user_id=request.user.user_id,
        )
    )
