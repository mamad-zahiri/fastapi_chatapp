from datetime import datetime

import socketio

from src.chat.services.auth import (
    connection_service,
    disconnection_service,
    verify_user_service,
)
from src.chat.services.clients import online_users
from src.chat.services.group import (
    create_group_message_service,
    create_group_service,
    is_group_member,
    join_group_service,
    send_group_message_service,
)
from src.chat.services.private import (
    create_private_message_service,
    send_private_message_service,
)
from src.chat.services.system import list_users_service, search_users_service
from src.db.models import Group, GroupChat, GroupMember, PrivateChat, User
from src.settings import settings

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


@sio.on("/system/search-users")
async def system_search_users(sid, env):
    print(env)
    return await search_users_service(env.get("q"))


@sio.on("/system/list-online-users")
async def system_list_online_users(sid):
    return list(online_users.all().keys())


@sio.on("/private/send_message")
async def private_send_message(sid, env):
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

    payload = await create_private_message_service(msg)
    return await send_private_message_service(sio, payload)


@sio.on("/private/list-new-messages")
async def private_list_new_messages(sid, env):
    receiver = await verify_user_service(env)

    new_messages = await PrivateChat.find_many(
        PrivateChat.receiver.id == receiver.id,
        PrivateChat.seen == False,
        fetch_links=True,
    ).to_list()

    return list(map(lambda x: x.model_dump(), new_messages))


@sio.on("/private/list-old-messages")
async def private_list_old_messages(sid, env):
    receiver = await verify_user_service(env)

    old_messages = await PrivateChat.find_many(
        PrivateChat.receiver.id == receiver.id,
        PrivateChat.seen == True,
        fetch_links=True,
    ).to_list()

    return list(map(lambda x: x.model_dump(), old_messages))


@sio.on("/system/create-group")
async def system_add_groups(sid, env):
    user = await verify_user_service(env)

    if user is None:
        return "invalid token"

    group, created = await create_group_service(env.get("group"), user)

    if created:
        return f"group {group.name} created"

    return f"group {group.name} already exists"


@sio.on("/system/join-group")
async def group_join(sid, env):
    user = await verify_user_service(env)
    if user is None:
        return "invalid token"

    group = await Group.find_one(Group.name == env.get("group"))
    if group is None:
        return "group does not exists"

    _group_member, joined = await join_group_service(group, user)

    if not joined:
        return f"you are already a member of {group.name} or can not join"

    await sio.enter_room(sid, group.id)
    await sio.emit("/group", data=f"user {user.email} joined group", room=group.id)

    return f"you are joined to {group.name}"


@sio.on("/group/attach-group")
async def group_attach_group(sid, env):
    user = await verify_user_service(env)
    if user is None:
        return "invalid token"

    group = await Group.find_one(Group.name == env.get("group"))
    if group is None:
        return "group does not exists"

    group_member = await GroupMember.find_one(
        GroupMember.group.id == group.id,
        GroupMember.member.id == user.id,
    )

    if group_member is None:
        return f"you are not member of {group.name}"

    await sio.enter_room(sid, group.id)
    await sio.emit("/group", data=f"user {user.email} is onlined", room=group.id)

    return "ok"


@sio.on("/system/list-groups")
async def system_list_groups(sid, env):
    user = await verify_user_service(env)
    if user is None:
        return "invalid token"

    groups = await Group.find_all().to_list()

    return list(map(lambda x: x.model_dump(), groups))


@sio.on("/system/search-groups")
async def system_search_groups(sid, env):
    print(env)
    return await search_users_service(env.get("q"))


@sio.on("/group/send-message")
async def group_send_message(sid, env):
    user = await verify_user_service(env)
    if user is None:
        return "invalid token"

    group = await Group.find_one(Group.name == env.get("group"))
    if group is None:
        return "group does not exists"

    message = GroupChat(
        message=env.get("message"),
        receiver=group,
        sender=user,
        timestamp=datetime.now(),
    )
    message, err = await create_group_message_service(message)

    if message is None:
        return err

    return await send_group_message_service(sio, message)


@sio.on("/group/get-messages")
async def group_get_messages(sid, env):
    user = await verify_user_service(env)
    if user is None:
        return "invalid token"

    group = await Group.find_one(Group.name == env.get("group"))
    if group is None:
        return "group does not exists"

    if not is_group_member(group, user):
        return f"user {user.email} is not a member of {group.name}"

    group_messages = await GroupChat.find_many(
        GroupChat.receiver.id == group.id
    ).to_list()

    return list(map(lambda x: x.model_dump(), group_messages))
