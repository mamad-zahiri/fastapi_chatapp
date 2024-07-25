from datetime import datetime

import socketio
from socketio.exceptions import ConnectionRefusedError

from src.auth.services import verify_token_service
from src.chat.models import PrivateChat
from src.settings import settings
from src.users.models import User
from src.utils.chat import token_provided
from src.utils.jwt import decode_jwt
from src.utils.users import find_user, get_all_users

sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")

# TODO: use redis as cache server
#   It is not a good practice to save online users in dictionary. Instead
#   we could save them in a Redis Cache or something.
online_users = {}


async def get_receiver_and_status(email: str) -> tuple[User | dict, bool]:
    user = online_users.get(email)

    if user is None:
        return await User.find_one(User.email == email), False

    return user, True


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

    user = user.model_dump(
        mode="json",
        exclude=[
            "password",
            "email_verified",
            "chats",
            "groups",
        ],
    )
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


@sio.on("/system/list-users")
async def system_list_users(sid):
    # TODO 1: refactor and clean this function
    # TODO 2: we need a logic to select which users to send
    users = await get_all_users()

    def dump(u):
        return u.model_dump(
            exclude=[
                "password",
                "email_verified",
                "chats",
                "groups",
            ],
            mode="json",
        )

    users = list(map(dump, users))

    return users


@sio.on("/system/list-online-users")
async def system_list_online_users(sid):
    # TODO: refactor and clean this function
    return online_users


@sio.on("/private/chat")
async def private_chat(sid, env):
    decoded_token = decode_jwt(
        env["token"],
        settings.jwt_access_secret_key,
        settings.jwt_algorithm,
    )
    sender = await User.find_one(User.email == decoded_token["email"])

    receiver, is_online = await get_receiver_and_status(env["receiver"])

    if receiver is None:
        return "invalid receiver"

    payload = PrivateChat(
        timestamp=datetime.now(),
        message=env["message"],
        file="",
        sender=sender,
    )

    if is_online:
        await sio.emit("/private/chat", payload.model_dump_json(exclude=["sender"]))

    receiver.chats.append(payload)
    await receiver.save()

    return payload.model_dump_json(exclude=["sender"])
