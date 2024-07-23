from datetime import datetime

from fastapi import APIRouter

from src.auth.schemas import UserLogin, UserSignup
from src.auth.services import create_user_service, generate_pair_token, obtain_pair_token_service
from src.users.models import User

router = APIRouter()


@router.post("/signup")
async def signup(user: UserSignup):
    user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        password=user.password,
        email=user.email,
        email_verified=False,
        last_seen=datetime.now(),
    )
    new_user = await create_user_service(user)
    return generate_pair_token(new_user)


@router.post("/token")
async def obtain_pair_token(user: UserLogin) -> dict[str, str]:
    return await obtain_pair_token_service(user)
