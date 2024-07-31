from src.db.models import Group, User


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
