from datetime import datetime, timedelta

import jwt
from jwt.exceptions import PyJWTError

from src.settings import settings


def encode_jwt(
    payload: dict[str, str],
    secret_key: str,
    algorithm: str,
) -> str:
    return jwt.encode(payload, secret_key, algorithm)


def decode_jwt(token: str, secret_key: str, algorithm: str) -> None | dict[str, str]:
    try:
        return jwt.decode(token, secret_key, [algorithm])

    except PyJWTError:
        return None


def token_expired(decoded_token: dict[str, str | int]) -> bool:
    expires_at = datetime.fromtimestamp(decoded_token["expires"])

    return expires_at >= datetime.now()


def generate_access_token(payload: dict[str, str]) -> str:
    exp_time = datetime.now() + timedelta(seconds=settings.jwt_access_token_expire)
    payload["expires"] = exp_time.timestamp()

    return encode_jwt(
        payload,
        settings.jwt_access_secret_key,
        settings.jwt_algorithm,
    )


def generate_refresh_token(payload: dict[str, str]) -> str:
    exp_time = datetime.now() + timedelta(seconds=settings.jwt_refresh_token_expire)
    payload["expires"] = exp_time.timestamp()

    return encode_jwt(
        payload,
        settings.jwt_refresh_secret_key,
        settings.jwt_algorithm,
    )
