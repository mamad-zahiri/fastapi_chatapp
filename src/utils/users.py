from passlib.context import CryptContext

from src.users.models import User


async def user_exists(email: str) -> bool:
    restult = await User.find_one(User.email == email)

    if restult is None:
        return False

    return True


async def find_user(email: str) -> User | None:
    restult = await User.find_one(User.email == email)

    if restult is None:
        return None

    return restult


async def get_all_users() -> list[User]:
    collection = get_collection("user")
    restult = await collection.find().to_list(2)

    if restult is None:
        return None

    users = []

    async for user in restult:
        
        u = User(
            id=str(user["_id"]),
            first_name=user["first_name"],
            last_name=user["last_name"],
            email=user["email"],
            password=user["password"],
            last_seen=user["last_seen"],
            email_verified=user["email_verified"],
        )

        users.append(u)

    return users


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(raw_pass: str, hashed_pass: str) -> bool:
    return password_context.verify(raw_pass, hashed_pass)
