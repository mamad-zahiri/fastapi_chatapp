from typing import Any

from socketio import AsyncServer

from src.db.models import Group, GroupChat, GroupMember, User


async def create_group_service(name: str, user: User) -> list[Group, bool]:
    # NOTE: we could check some permissions for user to see if it can create
    # new group or not

    created = False
    group = await Group.find_one(Group.name == name)

    if group is None:
        group = Group(name=name)
        await group.save()
        created = True

    return group, created


async def join_group_service(group: Group, user: User):
    # NOTE: we could check some permissions for user to see if it can join
    # this group or not

    joined = False

    group_member = await GroupMember.find_one(
        GroupMember.group.id == group.id,
        GroupMember.member.id == user.id,
    )

    if group_member is None:
        group_member = GroupMember(group=group, member=user)
        group_member = await group_member.create()
        joined = True

    return group_member, joined


async def is_group_member(group: Group, user: User) -> bool:
    group_member = await GroupMember.find_one(
        GroupMember.group.id == group.id,
        GroupMember.member.id == user.id,
    )

    if group_member is None:
        return False

    return True


async def create_group_message_service(message: GroupChat) -> list[GroupChat | None, bool, str]:
    user = message.sender
    group = message.receiver

    group_message = None
    err_msg = ""

    if not is_group_member(group, user):
        err_msg = f"user {user.email} is not a member of {group.name}"
        return group_message, err_msg

    group_message = await message.create()

    return group_message, err_msg


async def send_group_message_service(sio: AsyncServer, message: GroupChat) -> dict[str, Any]:
    payload = message.model_dump()

    await sio.emit(
        "/group/send-message",
        data=payload,
        room=message.receiver.id,
    )

    return payload
