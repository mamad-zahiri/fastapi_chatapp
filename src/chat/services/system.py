from src.db.models import User


async def list_users_service():
    # TODO: we need a logic to select which users to send
    users = await User.find_all().to_list()

    def dump(u):
        return u.model_dump(
            exclude=["password", "last_seen"],
            mode="json",
        )

    users = list(map(dump, users))

    return users


async def search_users_service(email: str):
    users = await User.find({"email": {"$regex": f".*{email}.*"}}).to_list()

    def dump(u):
        return u.model_dump(
            exclude=["password", "last_seen"],
            mode="json",
        )

    users = list(map(dump, users))

    return users


async def search_groups_service(name: str):
    groups = await User.find({"name": {"$regex": f".*{name}.*"}}).to_list()

    def dump(u):
        return u.model_dump(
            # exclude=["password", "last_seen"],
            mode="json",
        )

    groups = list(map(dump, groups))

    return groups
