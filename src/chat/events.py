import socketio
from socketio.exceptions import ConnectionRefusedError

from src.auth.services import verify_token_service
from src.settings import settings
from src.utils.chat import token_provided
from src.utils.jwt import decode_jwt
from src.utils.users import find_user

sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")

# TODO: use redis as cache server
#   It is not a good practice to save online users in dictionary. Instead
#   we could save them in a Redis Cache or something.
online_users = {}


@sio.on("connect")
async def connect(sid, e, auth):
    # TODO: refactor and clean this function
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

    user = user.model_dump(mode="json", exclude=["password", "email_verified"])
    online_users.update({sid: user})

    await sio.emit("/auth/verify", "verified", to=sid)


@sio.on("disconnect")
async def disconnect(sid):
    # TODO: refactor and clean this function
    try:
        online_users.pop(sid)
    except KeyError as e:
        pass

    await sio.emit("/broadcast/user-diconnect", data=sid)
