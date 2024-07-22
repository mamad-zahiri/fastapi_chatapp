from fastapi import status
from fastapi.exceptions import HTTPException

from src.auth.schemas import UserSignup
from src.users.models import User
from src.utils import users as user_util


async def create_user_service(user: UserSignup) -> User:
    if await user_util.user_exists(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exist",
        )

    await user_util.create_user(
        user.email,
        user.password.get_secret_value(),
        user.first_name,
        user.last_name,
    )
