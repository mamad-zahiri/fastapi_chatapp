from pydantic import EmailStr
from socketio import AsyncServer
from socketio.exceptions import ConnectionRefusedError

from src.auth.services import verify_token_service
from src.chat.services.clients import online_users
from src.settings import settings
from src.utils.chat import token_provided
from src.utils.jwt import decode_jwt
from src.utils.users import find_user


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

    user = await find_user(decoded_token["email"])

    if user is None:
        raise ConnectionRefusedError()

    # this email used when disconnect so we can update last_seen
    await sio.save_session(sid, {"email": user.email})

    online_users.add(user.email, sid)


async def disconnection_service(sio: AsyncServer, sid) -> EmailStr:
    email = (await sio.get_session(sid)).get("email")
    return email
