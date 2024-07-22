from fastapi import APIRouter

from src.auth.schemas import UserSignup
from src.auth.services import create_user_service

router = APIRouter()


@router.post("/signup")
async def signup(user: UserSignup):
    await create_user_service(user)
