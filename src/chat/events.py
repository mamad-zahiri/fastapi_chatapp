from datetime import datetime

import socketio

from src.chat.models import PrivateChat
from src.chat.services.auth import connection_service, disconnection_service
from src.chat.services.clients import online_users
from src.settings import settings
from src.users.models import User
from src.utils.jwt import decode_jwt
from src.utils.users import get_all_users

sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")


async def get_receiver_and_status(email: str) -> tuple[User | dict, bool]:
    sid = online_users.get(email)
    user = await User.find_one(User.email == email)

    return user, sid


@sio.on("connect")
async def connect(sid, e, auth):
    await connection_service(sid, auth)
    await sio.emit("/auth/verify", "verified", to=sid)


@sio.on("disconnect")
async def disconnect(sid):
    email = await disconnection_service(sid)
    await sio.emit("/broadcast/user-disconnect", data=email)


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
    return list(online_users.all().keys())


@sio.on("/private/chat")
async def private_chat(sid, env):
    # TODO: refactor and clean this function
    decoded_token = decode_jwt(
        env["token"],
        settings.jwt_access_secret_key,
        settings.jwt_algorithm,
    )
    sender = await User.find_one(User.email == decoded_token["email"])

    receiver, sid = await get_receiver_and_status(env["receiver"])

    if receiver is None:
        return "invalid receiver"

    payload = PrivateChat(
        timestamp=datetime.now(),
        message=env["message"],
        file="",
        sender=sender.email,
    )
    to_send = payload.model_dump(exclude=["id"])

    if sid is not None:
        await sio.emit(
            "/private/chat",
            to_send,
            to=sid,
        )

    receiver.chats.append(payload)
    await receiver.save()

    return to_send


@sio.on("/private/list-new-chats")
async def private_list_new_chats(sid, env):
    # TODO: refactor and clean this function
    decoded_token = decode_jwt(
        env["token"],
        settings.jwt_access_secret_key,
        settings.jwt_algorithm,
    )

    sender = await User.find_one(User.email == decoded_token["email"])

    # TODO:
    #   for long list of chats we must paginate the query
    new_chats = []

    for chat in sender.chats:
        if not chat.seen:
            new_chats.append(chat.model_dump(exclude=["seen"]))

    return new_chats


@sio.on("/private/list-chats")
async def private_list_chats(sid, env):
    # TODO: refactor and clean this function
    decoded_token = decode_jwt(
        env["token"],
        settings.jwt_access_secret_key,
        settings.jwt_algorithm,
    )

    sender = await User.find_one(User.email == decoded_token["email"])

    # TODO:
    #   for long list of chats we must paginate the query
    old_chats = []

    for chat in sender.chats:
        if chat.seen:
            old_chats.append(chat.model_dump(exclude=["seen"]))

    return old_chats
