from pydantic import EmailStr
from socketio import AsyncServer
from socketio.exceptions import ConnectionRefusedError

from src.auth.services import verify_token_service
from src.chat.services.clients import online_users
from src.db.models import User
from src.settings import settings
from src.utils.chat import token_provided
from src.utils.jwt import decode_jwt, token_expired


async def connection_service(sio: AsyncServer, sid: str, auth: dict[str, str]):
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

    user = await User.find_one(User.email == decoded_token.get("email"))
    if user is None:
        raise ConnectionRefusedError()

    # this email used when disconnect so we can update last_seen
    await sio.save_session(sid, {"email": user.email})

    online_users.add(user.email, sid)


async def disconnection_service(sio: AsyncServer, sid) -> EmailStr:
    email = (await sio.get_session(sid)).get("email")
    online_users.pop(email)
    return email


async def verify_user_service(env: dict[str, str]) -> User | None:
    decoded_token = decode_jwt(
        env["token"],
        settings.jwt_access_secret_key,
        settings.jwt_algorithm,
    )

    if decoded_token is None or token_expired(decoded_token):
        return None

    return await User.find_one(User.email == decoded_token["email"])
