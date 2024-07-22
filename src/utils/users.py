from passlib.context import CryptContext
from pymongo.results import InsertOneResult

from src.db.connection import get_collection
from src.users.models import User


async def user_exists(email: str) -> bool:
    collection = get_collection("user")
    restult = await collection.find_one({"email": email})

    if restult is None:
        return False

    return True


async def create_user(user: User) -> InsertOneResult:
    collection = get_collection("user")
    return await collection.insert_one(user.model_dump())
    return await collection.insert_one(user.model_dump_json())


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return password_context.hash(password)
