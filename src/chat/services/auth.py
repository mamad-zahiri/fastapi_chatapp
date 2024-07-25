from pydantic import EmailStr
from socketio.exceptions import ConnectionRefusedError

from src.auth.services import verify_token_service
from src.chat.services.clients import online_users
from src.settings import settings
from src.utils.chat import token_provided
from src.utils.jwt import decode_jwt
from src.utils.users import find_user


async def connection_service(sid: str, auth: dict[str, str]):
    if not token_provided(auth):
        raise ConnectionRefusedError()

    token = auth["token"]

    if not verify_token_service(token):
        raise ConnectionRefusedError()

    decoded_token = decode_jwt(
        token,
        settings.jwt_access_secret_key,
        settings.jwt_algorithm,
    )

    user = await find_user(decoded_token["email"])

    if user is None:
        raise ConnectionRefusedError()

    online_users.add(user.email, sid)


async def disconnection_service(sid) -> EmailStr:
    return online_users.pop(sid)
