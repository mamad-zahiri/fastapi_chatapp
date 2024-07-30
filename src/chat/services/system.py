from src.utils.users import get_all_users


async def list_users_service():
    # TODO: we need a logic to select which users to send
    users = await get_all_users()

    def dump(u):
        return u.model_dump(
            exclude=["password", "last_seen"],
            mode="json",
        )

    users = list(map(dump, users))

    return users
