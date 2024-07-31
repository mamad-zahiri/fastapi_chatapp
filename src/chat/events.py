from datetime import datetime

import socketio

from src.auth.services import verify_token_service
from src.chat.services import private
from src.chat.services.auth import connection_service, disconnection_service, verify_user_service
from src.chat.services.clients import online_users
from src.chat.services.system import list_users_service
from src.db.models import Group, GroupChat, GroupMember, PrivateChat, User
from src.settings import settings
from src.utils.jwt import decode_jwt

redis_uri = f"redis://{settings.redis_host}:{settings.redis_port}"
redis_manager = socketio.AsyncRedisManager(redis_uri)

sio = socketio.AsyncServer(
    cors_allowed_origins="*",
    async_mode="asgi",
    client_manager=redis_manager,
)


@sio.on("connect")
async def connect(sid, e, auth):
    await connection_service(sio, sid, auth)
    await sio.emit("/auth/verify", "verified", to=sid)


@sio.on("disconnect")
async def disconnect(sid):
    email = await disconnection_service(sio, sid)
    await sio.emit("/broadcast/user-disconnect", data=email)


@sio.on("/system/list-users")
async def system_list_users(sid):
    return await list_users_service()


@sio.on("/system/list-online-users")
async def system_list_online_users(sid):
    return list(online_users.all().keys())


@sio.on("/private/chat")
async def private_chat(sid, env):
    sender = await verify_user_service(env)
    if sender is None:
        return "invalid token"

    receiver = await User.find_one(User.email == env.get("receiver"))
    if receiver is None:
        return "invalid receiver"

    msg = PrivateChat(
        sender=sender,
        receiver=receiver,
        file=env.get("file_link"),
        message=env.get("message"),
        timestamp=datetime.now(),
    )

    payload = await private.create_message_service(msg)
    return await private.send_message_service(sio, payload)


@sio.on("/private/list-new-chats")
async def private_list_new_chats(sid, env):
    # TODO: refactor and clean this function
    receiver = await verify_user_service(env)

    new_chats = await PrivateChat.find_many(
        PrivateChat.receiver.id == receiver.id,
        PrivateChat.seen == False,
        fetch_links=True,
    ).to_list()

    return list(map(lambda x: x.model_dump(exclude=["receiver", "seen"]), new_chats))


@sio.on("/private/list-chats")
async def private_list_chats(sid, env):
    # TODO: refactor and clean this function
    receiver = await verify_user_service(env)

    old_chats = await PrivateChat.find_many(
        PrivateChat.receiver.id == receiver.id,
        PrivateChat.seen == True,
        fetch_links=True,
    ).to_list()

    return list(map(lambda x: x.model_dump(exclude=["receiver", "seen"]), old_chats))


@sio.on("/system/create-group")
async def system_add_groups(sid, env):
    # TODO: refactor and clean this function
    user = await verify_user_service(env)

    if user is None:
        return "invalid token"

    group = await Group.find_one(Group.name == env.get("group"))

    if group is None:
        group = Group(name=env.get("group"))
        await group.save()
        return f"group {group.name} created"

    return f"group {group.name} already exists"


@sio.on("/system/join-group")
async def group_join(sid, env):
    # TODO: refactor and clean this function
    user = await verify_user_service(env)

    if user is None:
        return "invalid token"

    group = await Group.find_one(Group.name == env.get("group"))

    if group is None:
        return "group does not exists"

    group_member = await GroupMember.find_one(GroupMember.group.id == group.id, GroupMember.member.id == user.id)

    if group_member is not None:
        return f"you are already a member of {group.name}"

    group_member = GroupMember(group=group, member=user)
    await group_member.save()

    await sio.enter_room(sid, group.id)
    await sio.emit("/group", data=f"user {user.email} joined group", room=group.id)

    return "ok"


@sio.on("/group/attach-group")
async def group_attach_group(sid, env):
    # TODO: refactor and clean this function
    user = await verify_user_service(env)

    if user is None:
        return "invalid token"

    group = await Group.find_one(Group.name == env.get("group"))

    if group is None:
        return "group does not exists"

    group_member = await GroupMember.find_one(GroupMember.group.id == group.id, GroupMember.member.id == user.id)

    if group_member is None:
        return f"you are not member of {group.name}"

    await sio.enter_room(sid, group.id)
    await sio.emit("/group", data=f"user {user.email} is onlined", room=group.id)

    return "ok"


@sio.on("/system/list-groups")
async def system_list_groups(sid, env):
    # TODO: refactor and clean this function
    if not verify_token_service(env["token"]):
        return "invalid token"

    groups = await Group.find_all().to_list()

    return list(map(lambda x: x.model_dump(), groups))


@sio.on("/group/send-message")
async def group_send_message(sid, env):
    # TODO: refactor and clean this function
    if not verify_token_service(env["token"]):
        return "invalid token"

    decoded_token = decode_jwt(
        env["token"],
        settings.jwt_access_secret_key,
        settings.jwt_algorithm,
    )

    user = await User.find_one(User.email == decoded_token["email"])
    group = await Group.find_one(Group.name == env.get("group"))

    if user is None or group is None:
        return "user or group does not exist"

    group_member = await GroupMember.find_one(GroupMember.group.id == group.id, GroupMember.member.id == user.id)

    if group_member is None:
        return f"user {user.email} is not a member of {group.name}"

    group_chat = GroupChat(
        message=env.get("message"),
        receiver=group,
        sender=user,
        timestamp=datetime.now(),
    )

    await group_chat.save()

    await sio.emit("/group/send-message", data=group_chat.model_dump(), room=group.id)

    return group_chat.model_dump()


@sio.on("/group/get-messages")
async def group_get_messages(sid, env):
    # TODO: refactor and clean this function
    if not verify_token_service(env["token"]):
        return "invalid token"

    user = await verify_user_service(env)
    group = await Group.find_one(Group.name == env.get("group"))

    if user is None or group is None:
        return "user or group does not exist"

    group_member = await GroupMember.find_one(GroupMember.group.id == group.id, GroupMember.member.id == user.id)

    if group_member is None:
        return f"user {user.email} is not a member of {group.name}"

    group_messages = await GroupChat.find_many(GroupChat.receiver.id == group.id).to_list()

    return list(map(lambda x: x.model_dump(), group_messages))
