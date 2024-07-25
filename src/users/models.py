from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from beanie import BackLink, Document
from pydantic import EmailStr, Field

from src.chat.models import Group, PrivateChat


class User(Document):
    id: UUID = Field(default_factory=uuid4)
    first_name: str = ""
    last_name: str = ""
    email: EmailStr
    email_verified: bool
    password: str = Field(repr=False)
    last_seen: datetime
    groups: List[BackLink[Group]] = Field(original_field="members", default=[])
    chats: List[PrivateChat] = []

    class Settings:
        name = "users"
