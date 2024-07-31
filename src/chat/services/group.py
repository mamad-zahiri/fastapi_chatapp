from src.db.models import Group, GroupMember, User


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
