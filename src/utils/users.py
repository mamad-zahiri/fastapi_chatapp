from passlib.context import CryptContext

from src.db.models import User


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
    return await User.find().to_list()


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(raw_pass: str, hashed_pass: str) -> bool:
    return password_context.verify(raw_pass, hashed_pass)
