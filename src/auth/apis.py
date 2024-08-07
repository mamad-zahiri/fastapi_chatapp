from fastapi import APIRouter

from src.auth.schemas import UserLogin, UserSignup
from src.auth.services import (
    create_user_service,
    generate_pair_token,
    obtain_pair_token_service,
    refresh_token_service,
    verify_token_service,
)

router = APIRouter()


@router.post("/signup")
async def signup(user: UserSignup):
    new_user = await create_user_service(user)
    return generate_pair_token(new_user)


@router.post("/token")
async def obtain_pair_token(user: UserLogin) -> dict[str, str]:
    return await obtain_pair_token_service(user)


@router.post("/token/verify")
def verify_token(token: str) -> str:
    if verify_token_service(token):
        return "valid"
    else:
        return "invalid"


@router.post("/token/refresh")
async def refresh_token(token: str) -> dict[str, str] | str:
    pair_token = await refresh_token_service(token)

    if pair_token:
        return pair_token

    return "invalid refresh token"
