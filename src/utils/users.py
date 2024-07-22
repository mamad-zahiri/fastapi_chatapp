from pymongo.results import InsertOneResult

from src.db.connection import get_collection


async def user_exists(email: str) -> bool:
    collection = get_collection("user")
    restult = await collection.find_one({"email": email})

    if restult is None:
        return False

    return True


async def create_user(
    email: str,
    password: str,
    first_name: str | None = None,
    last_name: str | None = None,
) -> InsertOneResult:
    data = dict(
        email=email,
        password=password,
        first_name=first_name or "",
        last_name=last_name or "",
    )
    collection = get_collection("user")
    return await collection.insert_one(data)
