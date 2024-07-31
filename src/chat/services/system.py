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
