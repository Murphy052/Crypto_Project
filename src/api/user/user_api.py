from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.api.user.usecases import user_login_usecase, register_usecase
from src.schemas import TokenSchema

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
