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


async def find_user(email: str) -> User | None:
    collection = get_collection("user")
    restult = await collection.find_one({"email": email})

    if restult is None:
        return None

    return User(
        first_name=restult["first_name"],
        last_name=restult["last_name"],
        email=restult["email"],
        password=restult["password"],
        last_seen=restult["last_seen"],
        email_verified=restult["email_verified"],
    )


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(raw_pass: str, hashed_pass: str) -> bool:
    return password_context.verify(raw_pass, hashed_pass)
