from datetime import datetime

from fastapi import APIRouter

from src.auth.schemas import UserSignup
from src.auth.services import create_user_service
from src.users.models import User

router = APIRouter()


@router.post("/signup")
async def signup(user: UserSignup):
    user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        password=user.password,
        email=user.email,
        email_verified=False,
        last_seen=datetime.now(),
    )
    await create_user_service(user)
