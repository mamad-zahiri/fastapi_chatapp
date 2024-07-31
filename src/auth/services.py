from datetime import datetime

from fastapi import status
from fastapi.exceptions import HTTPException

from src.auth.schemas import UserLogin, UserSignup
from src.db.models import User
from src.settings import settings
from src.utils import jwt as jwt_util
from src.utils import users as user_util


async def create_user_service(user: UserSignup) -> User:
    if await User.find_one(User.email == user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exist",
        )

    user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        password=user.password,
        email=user.email,
        last_seen=datetime.now(),
    )

    user.password = user_util.hash_password(user.password)
    new_user = await user.insert()

    return new_user


async def obtain_pair_token_service(user: UserLogin) -> User:
    exp = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Incorrect email or password",
    )

    fetched_user = await User.find_one(User.email == user.email)

    if fetched_user is None:
        raise exp

    if user_util.verify_password(user.password, fetched_user.password):
        return generate_pair_token(fetched_user)

    raise exp


def create_access_token(user: User) -> str:
    payload = dict(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
    )
    return jwt_util.generate_access_token(payload)


def create_refresh_token(user: User) -> str:
    payload = dict(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
    )
    return jwt_util.generate_refresh_token(payload)


def generate_pair_token(user: User) -> dict[str, str]:
    return {
        "access_token": create_access_token(user),
        "refresh_token": create_refresh_token(user),
    }


def verify_token_service(token: str) -> bool:
    decoded_token = jwt_util.decode_jwt(
        token,
        settings.jwt_access_secret_key,
        settings.jwt_algorithm,
    )

    if decoded_token is None or jwt_util.token_expired(decoded_token):
        return False

    return True


async def refresh_token_service(token: str) -> dict[str, str] | None:
    decoded_token = jwt_util.decode_jwt(
        token,
        settings.jwt_refresh_secret_key,
        settings.jwt_algorithm,
    )

    if decoded_token is None or jwt_util.token_expired(decoded_token):
        return None

    user = await User.find_one(User.email == decoded_token["email"])
    return generate_pair_token(user)
